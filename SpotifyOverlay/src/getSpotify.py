import time

import urllib.parse
import urllib3
import auth
import requests
import threading
import pycurl
import json
from io import BytesIO

currentSong = ""

def getActiveDeviceID():  
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    buffer = BytesIO()
    c = pycurl.Curl()

    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/devices")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return(None, None)
    
    if status == 401:
        #print("get active device id - refreshing tokens")
        auth.getNewTokens()
        return getActiveDeviceID()
        

    elif status == 200 or status == 204:
        devices = json.loads(buffer.getvalue().decode('utf-8'))['devices']
        ##print("devices: ", devices)
        for dev in devices:
            if dev['is_active'] == True:
                ##print("exit")
                return (dev['id'], True)
            
        if len(devices) > 0:
            ##print("exit")
            return (devices[0]['id'], False)
        else:
            ##print("exit")
            return(None, False)
    
    else:
        #print("Get active device id error: ", status, " - ", json.loads(buffer.getvalue().decode('utf-8')))
        return(None, None)

def getActiveDevice():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/devices")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return(None, None)

    if status == 401:
        
        #print("getactivedevice - refreshing tokens")
        auth.getNewTokens()
        return getActiveDevice()
    elif status == 200 or status == 204:
        devices = json.loads(buffer.getvalue().decode('utf-8'))['devices']

        for dev in devices:
            if dev['is_active'] == True:
                return (dev, True)
            
        if len(devices) > 0:
            return (devices[0], False)
        else:
            return(None, False)
    else:
        #print("Get active device id error: ", status)
        return(None, None)

def getCurrentPlayingType():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = pycurl.Curl()

    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/currently-playing")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    #c.setopt(c.HEADERFUNCTION, retryAfter)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()
    except pycurl.error:
        #print("get current playing type exception: ", pycurl.error)
        return None
    
    if status == 401:
        #print("get current playing type - refresh tokens")
        auth.getNewTokens()
        return getCurrentPlayingType()
    elif status == 200 or status == 204: 
        return json.loads(buffer.getvalue().decode('utf-8'))['currently_playing_type']
    elif status == 429:
        #print("----------------------------------------------")
        return None
    else:
        #print("get current playing type error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return None

def getCurrentSongID():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = pycurl.Curl()

    if getCurrentPlayingType() == 'track': 
        c.setopt(c.URL, "https://api.spotify.com/v1/me/player/currently-playing")
    elif getCurrentPlayingType() == 'episode':
        c.setopt(c.URL, "https://api.spotify.com/v1/me/player/currently-playing?additional_types=episode")
    else:
        #print("Cant get current type")
        return None
    
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()
    except pycurl.error:
        #print("exception: ", pycurl.error)      
        return None
    
    if status == 401:
        #print(f"get {getCurrentPlayingType()} id - refreshing tokens")
        auth.getNewTokens()
        return getCurrentSongID()
    elif status == 200 or status == 204:
        return json.loads(buffer.getvalue().decode('utf-8'))['item']['id']
    else:
        #print("get song id error: ", status)
        return None
            
def getCurrentSongAndArtist():
    global currentSongAndArtist
    acces_token = auth.getAuthToken()
    if acces_token == None:
        return "Restart Spotify Overlay"
    
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    buffer = BytesIO()
    c = pycurl.Curl()

    params= {"additional_types": "episode"}
    

    playingType = getCurrentPlayingType()
    if playingType == "episode":
        c.setopt(c.URL, "https://api.spotify.com/v1/me/player/currently-playing?additional_types=episode")
    elif playingType == 'track':
        c.setopt(c.URL, "https://api.spotify.com/v1/me/player/currently-playing")
    else:
        return "No song playing"

    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return "Check your internet, can't get current song or no song is currently playing"

    

    if status == 401:
        #print("get current song (or episode) - refreshing tokens")
        auth.getNewTokens()
        return getCurrentSongAndArtist()
    elif status == 200 or status == 204:
        response = json.loads(buffer.getvalue().decode('utf-8'))

        if getCurrentPlayingType() == "track":
            currentSongAndArtist = (response['item']['name'], response['item']['artists'][0]['name'])
        elif getCurrentPlayingType() == "episode":
            currentSongAndArtist = (response['item']['name'], response['item']['show']['name'])
        else:
            currentSongAndArtist = (None, None)
    else:
        #print("get current song error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        currentSongAndArtist = (None, None)
    return currentSongAndArtist


def getProgress():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    buffer = BytesIO()
    c = pycurl.Curl()


    playingType = getCurrentPlayingType()
    if playingType == "episode":
        c.setopt(c.URL, "https://api.spotify.com/v1/me/player/currently-playing?additional_types=episode")
    elif playingType == 'track':
        c.setopt(c.URL, "https://api.spotify.com/v1/me/player/currently-playing")
    else:
        return "No song playing"
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)

    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return(None, None)

    if status == 401:
        
        #print("getactivedevice - refreshing tokens")
        auth.getNewTokens()
        return getActiveDevice()
    elif status == 200 or status == 204:
        progress = json.loads(buffer.getvalue().decode('utf-8'))

        #print(json.dumps(progress['item'], indent=4))        
        return (progress['progress_ms'], progress['item']['duration_ms'])
        
    else:
        #print("Get active device id error: ", status)
        return None

def seekToPosition(position): 
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]    
    buffer = BytesIO()
    c = pycurl.Curl()

    #print("SEEK TO POS: ", position)
    params = {
            'device_id': getActiveDeviceID()[0],
    }

    c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/seek?position_ms={position}")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.CUSTOMREQUEST, "PUT")
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return False
    
    #print("STATUS: " , status)


    if status == 401:
        #print("restart song - refreshing token")
        auth.getNewTokens()
        return nextPlayback()

    elif status != 200 or status != 204:
        #print("restart song error: ", status)
        return False


def restartDevice(): 
    buffer = BytesIO()
    c = pycurl.Curl()
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    params = {
        'device_ids': [getActiveDeviceID()[0]],
    }

    headers = []
    headers.append("Content-Type: application/json")
    headers.append(authHeader[0])
    
    c.setopt(c.URL, "https://api.spotify.com/v1/me/player")
    c.setopt(c.POSTFIELDS, json.dumps(params))
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.CUSTOMREQUEST, "PUT")
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return None

    if status  == 401: 
        #print("restarting playback - refreshing token")
        auth.getNewTokens()
        return restartDevice()

    elif status == 204 or status == 200:
        #print("restarting device")
        startPlayback()
        return True
    else:
        #print("restart device error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False

def getPlaybackState():
    buffer = BytesIO()
    c = pycurl.Curl()
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    c.setopt(c.URL, "https://api.spotify.com/v1/me/player")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("get playback state exception: ", pycurl.error)
        return None

    if status == 401:
        #print("getplaybackstate - refreshing tokens")
        auth.getNewTokens()
        return getPlaybackState()
    elif status == 200 or status == 204:
        playbackState = json.loads(buffer.getvalue().decode('utf-8'))['is_playing']        
        return playbackState
    else:
        #print("playback state error: ", status)
        return None

def startPlayback():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    
    id, deviceRunning = getActiveDeviceID()
    
    if deviceRunning == True:
        buffer = BytesIO()
        c = pycurl.Curl()

        headers = []
        headers.append(authHeader[0])
        headers.append("Content-Type: application/json")
        ##print(headers)
        
        params = { 'device_id': id }
        
        c.setopt(c.URL, "https://api.spotify.com/v1/me/player/play")
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.POSTFIELDS, json.dumps(params))
        c.setopt(c.HTTPHEADER, headers)
        c.setopt(c.CUSTOMREQUEST, "PUT")
        try:   
            c.perform()
            status = c.getinfo(c.RESPONSE_CODE)
            c.close()        
        except pycurl.error:
            #print("exception: ", pycurl.error)
            return None
        if status == 401:
            #print("start playback - refreshing tokens")
            auth.getNewTokens()
            return startPlayback()
        elif status == 204 or status == 200:
            #print("starting playback...")
            return True
        else:
            #print("start playback error: ", status, " - ", buffer.getvalue().decode('utf-8'))
            return False
    elif deviceRunning == False:
        #print("startplayback...restarting device.")
        return restartDevice()
    else:
        #print("start playback error: No device found")
        return None

def pausePlayback():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    
    id, deviceRunning = getActiveDeviceID()
    if id != None:
        if deviceRunning == True:
            buffer = BytesIO()
            c = pycurl.Curl()

            params = {
                    'device_id': id,
            }

            c.setopt(c.URL, "https://api.spotify.com/v1/me/player/pause")
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
            c.setopt(c.HTTPHEADER, authHeader)
            c.setopt(c.CUSTOMREQUEST, "PUT")
            try:   
                c.perform()
                status = c.getinfo(c.RESPONSE_CODE)
                c.close()        
            except pycurl.error:
                #print("exception: ", pycurl.error)
                return None
            if status == 401:
                #print("pause playback - refreshing tokens")
                auth.getNewTokens()
                return pausePlayback()
            elif status != 200 or status != 204:
                #print("pause playback error: ", status)
                return False
    else:       
        #print("pause playback error: No device found")
        return None

def togglePlayback():
    if getPlaybackState() == True:
        return pausePlayback()
    else:
        return startPlayback()

def restartSong():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]    
    buffer = BytesIO()
    c = pycurl.Curl()

    params = {
            'device_id': getActiveDeviceID()[0],
    }

    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/seek?position_ms=0")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.CUSTOMREQUEST, "PUT")
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return False
    
    if status == 401:
        #print("restart song - refreshing token")
        auth.getNewTokens()
        return nextPlayback()

    elif status != 200 or status != 204:
        #print("restart song error: ", status)
        return False

def nextPlayback():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]    
    buffer = BytesIO()
    c = pycurl.Curl()

    params = {
            'device_id': getActiveDeviceID()[0],
    }

    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/next")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return False
    
    if status == 401:
        #print("skip song - refreshing token")
        auth.getNewTokens()
        return nextPlayback()

    elif status != 200 or status != 204:
        #print("skip song error: ", status)
        return False

def previousPlayback():
    buffer = BytesIO()
    c = pycurl.Curl()
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    params = {
            'device_id': getActiveDeviceID()[0],
    }

    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/previous")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return None
    
    if status == 401: 
        #print("previous song - refreshing token")
        auth.getNewTokens()
        return previousPlayback()

    elif status != 200 or status != 204:
        #print(" song error: ", status)
        return False
    
def volumeChanageable():
    device = getActiveDevice()[0]
    #print("volume = ", device['supports_volume'])
    if device != None:
        return device['supports_volume']
    else:
        #print("no device found")
        return None
    
def volumeDown():
    
    if volumeChanageable() == True:
        buffer = BytesIO()
        c = pycurl.Curl()
        acces_token = auth.getAuthToken()
        authHeader =  [f"Authorization: Bearer {acces_token}"]
        params = {
            'device_id': getActiveDeviceID()[0]
        }

        #print("params = ", urllib.parse.urlencode(params))
        
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/volume?volume_percent={getActiveDevice()[0]['volume_percent'] - 10}")
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
        c.setopt(c.CUSTOMREQUEST, "PUT")
        c.setopt(c.HTTPHEADER, authHeader)
        try:   
            c.perform()
            status = c.getinfo(c.RESPONSE_CODE)
            c.close()        
        except pycurl.error:
            #print("exception: ", pycurl.error)
            return None    

        if status == 401:
            #print("volume down - refreshing token")
            auth.getNewTokens()
            return volumeDown()
        elif status == 204 or status == 200:
            #print("turning volume down...")
            return True
        else:
            #print("volume down error: ", status, " - ", buffer.getvalue().decode('utf-8'))
            return False

def volumeUp():    
    #print("enter volume up")
    if volumeChanageable() == True:
        #print("volume changable")
        buffer = BytesIO()
        c = pycurl.Curl()
        acces_token = auth.getAuthToken()
        authHeader =  [f"Authorization: Bearer {acces_token}"]
        
        params = {
            'device_id': getActiveDeviceID()[0]
        }

        #print("params = ", urllib.parse.urlencode(params))
        
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/volume?volume_percent={getActiveDevice()[0]['volume_percent'] + 10}")
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
        c.setopt(c.CUSTOMREQUEST, "PUT")
        c.setopt(c.HTTPHEADER, authHeader)
        try:   
            c.perform()
            status = c.getinfo(c.RESPONSE_CODE)
            c.close()        
        except pycurl.error:
            #print("exception: ", pycurl.error)
            return None       

        if status == 401:
            #print("volume up - refresh tokens")
            auth.getNewTokens()
            return volumeDown()
        elif status == 204 or status == 200:
            #print("turning volume up...")
            return True
        else:
            #print("volume up error: ", status, " - ", buffer.getvalue().decode('utf-8'))
            return False
      
def getShuffleState():
    buffer = BytesIO()
    c = pycurl.Curl()
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    c.setopt(c.URL, "https://api.spotify.com/v1/me/player")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("get shuffle state exception: ", pycurl.error)
        return None
    
    if status == 401:
        #print("getshufflestate - refreshing tokens")
        auth.getNewTokens()
        return getShuffleState()
    elif status == 200 or status == 204:
        state = json.loads(buffer.getvalue().decode('utf-8'))['shuffle_state']        
        ##print("shuffle state = " , state)
        return state
    else:
        #print("shuffle state error: ", status)
        return False

def shuffleOff():
    buffer = BytesIO()
    c = pycurl.Curl()
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]    
    params = {
        'device_id': getActiveDeviceID()[0]
    }
    
    c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/shuffle?state={False}")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CUSTOMREQUEST, "PUT")
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return None
    
    if status == 401:
        #print("shuffle off - refreshing tokens")
        auth.getNewTokens()
        return shuffleOff()
    elif status == 204 or status == 200:
        #print("Turning shuffle off...")
        return True
    else:
        #print("shuffle off error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False
    
def shuffleOn():
    buffer = BytesIO()
    c = pycurl.Curl()
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    params = {
        'device_id': getActiveDeviceID()[0]
    }
    
    c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/shuffle?state={True}")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CUSTOMREQUEST, "PUT")
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return None
    
    if status == 401:
        #print("shuffle on - refreshing tokens")
        auth.getNewTokens()
        return shuffleOn()
    elif status == 204 or status == 200:
        #print("turning shuffle on...:")
        return True
    else:
        #print("shuffle on error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False
    
def toggleShuffle():
    state = getShuffleState()
    if state == True:
        #print("shuffle off")
        return shuffleOff()
    elif state == False:
        #print("shuffle on")
        return shuffleOn()        
    else:
        #print("Cant turn shuffle on or off")
        return None

def getSongLikedState():  
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = pycurl.Curl()

    type = getCurrentPlayingType()
    if type  == "track":
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/tracks/contains?ids={getCurrentSongID()}")
    elif type == 'episode':
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/episodes/contains?ids={getCurrentSongID()}")
    else:
        #print("Cant get liked state")
        return None
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("get liked state exception: ", pycurl.error)
        return None

    if status == 401:
        #print("get liked state - refreshing tokens") 
        auth.getNewTokens()
        return getSongLikedState()
    elif status == 200 or status == 204:
        state = buffer.getvalue().decode('utf-8').replace('[', '').replace(']', '').replace(' ', '').split(',')
        if state[0] == "true": 
            return True
        elif state[0] == "false":
            return False
        else:
            return None
    else:
        #print(f"get {type} liked state error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return None

def likeSong(): 
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = pycurl.Curl()

    headers = []
    headers.append(authHeader[0])
    headers.append("Content-Type: application/json")
    #print(headers)
    
    params = {
            'ids': getCurrentSongID()
    }    

    type = getCurrentPlayingType()
    if type == "track":
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/tracks?ids={getCurrentSongID()}")
    elif type == "episode":    
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/episodes?ids={getCurrentSongID()}")
    else:
        return None
        
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.CUSTOMREQUEST, "PUT")
    
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return None

    if status == 401:
        #print("Like song - refresh tokens") 
        auth.getNewTokens()
        return likeSong()
    elif status == 200 or status == 204:
        #print("Liking track...")
        return True
    else:
        #print(f"like {type} error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False

def unlikeSong():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = pycurl.Curl()

    headers = []
    headers.append(authHeader[0])
    headers.append("Content-Type: application/json")
    #print(headers)
    
    params = {
            'ids': getCurrentSongID()
    }    

    type = getCurrentPlayingType()
    if type == "track":
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/tracks?ids={getCurrentSongID()}")
    elif type == "episode":    
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/episodes?ids={getCurrentSongID()}")
    else:
        return None
        
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.CUSTOMREQUEST, "DELETE")
    
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("exception: ", pycurl.error)
        return None

    if status == 401:
        #print("Unlike song - refresh tokens")
        auth.getNewTokens()
        return likeSong()
    elif status == 200 or status == 204:
        #print("unliking track...")
        return True
    else:
        #print(f"unlike {type} error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False

def toggleLikeSong():
    state = getSongLikedState()

    if state == True:
        return unlikeSong()
    elif state == False:
        return likeSong()
    else:
        #print("Can't like/unlike current track")
        return None

def getRepeatState():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = pycurl.Curl()

    c.setopt(c.URL, "https://api.spotify.com/v1/me/player")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("get repeat state exception: ", pycurl.error)
        return None

    if status == 401:
        #print("getrepeatstate - refreshing tokens")
        auth.getNewTokens()
        return getRepeatState()
    elif status == 200 or status == 204:
        state = json.loads(buffer.getvalue().decode('utf-8'))['repeat_state'] 
        return state
    else:
        #print("repeat state error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return None

def toggleRepeat():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    if getCurrentPlayingType() == "track":
        buffer = BytesIO()
        c = pycurl.Curl()

        headers = []
        headers.append(authHeader[0])
        headers.append("Content-Type: application/json")
        
        state = getRepeatState()
        params = {
            'device_id': getActiveDeviceID(),
            'state': state
        }
        
        if state == "off":
            c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/repeat?state=context")
        elif state == "context":
            c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/repeat?state=track")
        elif state == "track":
            c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/repeat?state=off")
        else:
            #print("Repeat state error, state: ", state)
            return None
        
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
        c.setopt(c.HTTPHEADER, headers)
        c.setopt(c.CUSTOMREQUEST, "PUT")
        try:   
            c.perform()
            status = c.getinfo(c.RESPONSE_CODE)
            c.close()        
            #print("status - ", status)
        except pycurl.error:
            #print("exception: ", pycurl.error)
            return None

        if status == 401:
            #print("toggle repeat - refreshing tokens")
            auth.getNewTokens()
            return toggleRepeat()
        elif status == 204 or status == 200:
            #print(f"Changing repeat mode...")
            return True
        else:
            #print(f"toggle repeat error: ", status, " - ", buffer.getvalue().decode('utf-8'))
            return None
    else:
        #print("Cant repeat current track/podcast episode.")
        return None

def refreshTokens():
    
    while True:
        time.sleep(3000)
        #print("Getting new tokens")  
        auth.getNewTokens()