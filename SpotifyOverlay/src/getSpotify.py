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
        print("get active device id pycurl exception: ", pycurl.error)
        return(None, None)
    
    if status == 401:
        print("get active device id - refreshing tokens")
        auth.getNewTokens()
        return getActiveDeviceID()
        

    elif status == 200 or status == 204:
        devices = json.loads(buffer.getvalue().decode('utf-8'))['devices']

        for dev in devices:
            if dev['is_active'] == True:
                print("getActiveDeviceID - device found.")
                return (dev['id'], True)
            
        if len(devices) > 0:
            print("getActiveDeviceID - inactive device found.")
            return (devices[0]['id'], False)
        else:
            print("getActiveDeviceID - No devices found.")
            return(None, False)
    
    else:
        print("getActiveDeviceID error: ", status, " - ", json.loads(buffer.getvalue().decode('utf-8')))
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
        print("getActiveDevice - pycurl exception: ", status, " ", pycurl.error)
        return(None, None)

    if status == 401:
        
        print("getActiveDevice - refreshing tokens")
        auth.getNewTokens()
        return getActiveDevice()
    elif status == 200 or status == 204:
        devices = json.loads(buffer.getvalue().decode('utf-8'))['devices']

        for dev in devices:
            if dev['is_active'] == True:
                print("getActiveDevice - device found.")
                return (dev, True)
            
        if len(devices) > 0:
            print("getActiveDevice - inactive device found.")
            return (devices[0], False)
        else:
            print("getActiveDevice, no device found.")
            return(None, False)
    else:
        print("getActiveDevice: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return(None, None)

def getCurrentPlayingType():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = pycurl.Curl()

    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/currently-playing")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)

    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()
    except pycurl.error:
        print("getCurrentPlayingType pycurl exception: ", pycurl.error)
        return None
    
    if status == 401:
        print("get current playing type - refresh tokens")
        auth.getNewTokens()
        return getCurrentPlayingType()
    elif status == 200 or status == 204: 
        return json.loads(buffer.getvalue().decode('utf-8'))['currently_playing_type']
    else:
        print("get current playing type error: ", status, " - ", buffer.getvalue().decode('utf-8'))
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
        print("getCurrentSongID - Cant get current type")
        return None
    
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()
    except pycurl.error:
        print("getCurrentSongID - pycurl exception: ", pycurl.error)      
        return None
    
    if status == 401:
        print("getCurrentSongID - refreshing tokens")
        auth.getNewTokens()
        return getCurrentSongID()
    elif status == 200 or status == 204:
        return json.loads(buffer.getvalue().decode('utf-8'))['item']['id']
    else:
        print("getCurrentSongAndArtist: ", status, " - ", buffer.getvalue().decode('utf-8'))
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
        currentSongAndArtist = (None, None)

    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()
    except pycurl.error:
        print("getCurrentSongAndArtist - pycurl exception: ", status, " - ", pycurl.error)
        return (None, None)

    if status == 401:
        print("getCurrentSongAndArtist - refreshing tokens")
        auth.getNewTokens()
        return getCurrentSongAndArtist()
    elif status == 200 or status == 204:
        response = json.loads(buffer.getvalue().decode('utf-8'))

        if getCurrentPlayingType() == "track":
            currentSongAndArtist = (response['item']['name'], response['item']['artists'][0]['name'])
        elif getCurrentPlayingType() == "episode":
            currentSongAndArtist = (response['item']['name'], response['item']['show']['name'])
        else:
            print("getCurrentSongAndArtist - track type undefined")
            currentSongAndArtist = (None, None)
    else:
        print("getCurrentSongAndArtist: ", status, " - ", buffer.getvalue().decode('utf-8'))
        currentSongAndArtist = (None, None)
    return currentSongAndArtist


#returns current progress and duration of song.
def getProgressAndDuration():
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
        print("getProgressAndDuration - cant get current playing type.")
        return(None, None)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)

    try:   
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("getProgressAndDuration - pycurl exception: ", pycurl.error)
        return(None, None)

    if status == 401:
        print("getProgressAndDuration - refreshing tokens")
        auth.getNewTokens()
        return getProgressAndDuration()
    elif status == 200 or status == 204:
        progress = json.loads(buffer.getvalue().decode('utf-8'))
        #print("getProgressAndDuration - Returning progress and duration...")
        return (progress['progress_ms'], progress['item']['duration_ms'])
        
    else:
        print("getProgressAndDuration: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return (None, None)

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
        print("seekToPosition pycurl exception: ", pycurl.error)
        return False
    
    #print("STATUS: " , status)


    if status == 401:
        print("seekToPosition - refreshing token")
        auth.getNewTokens()
        return seekToPosition()

    elif status != 200 or status != 204:
        print("seekToPosition: ", status, " - ", buffer.getvalue().decode('utf-8'))
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
        print("restartDevice pycurl exception: ", pycurl.error)
        return None

    if status  == 401: 
        print("restartDevice - refreshing token")
        auth.getNewTokens()
        return restartDevice()

    elif status == 204 or status == 200:
        print("restarting device")
        startPlayback()
        return True
    else:
        print("restartDevice error: ", status, " - ", buffer.getvalue().decode('utf-8'))
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
        print("getPlaybackState pycurl exception: ", pycurl.error)
        return None

    if status == 401:
        print("getplaybackstate - refreshing tokens")
        auth.getNewTokens()
        return getPlaybackState()
    elif status == 200 or status == 204:
        playbackState = json.loads(buffer.getvalue().decode('utf-8'))['is_playing']        
        return playbackState
    else:
        print("getPlaybackState: ", status, " - ", buffer.getvalue().decode('utf-8'))
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
            print("startPlayback pycurl exception: ", pycurl.error)
            return None
        if status == 401:
            print("start playback - refreshing tokens")
            auth.getNewTokens()
            return startPlayback()
        elif status == 204 or status == 200:
            print("starting playback...")
            return True
        else:
            print("startPlayback error: ", status, " - ", buffer.getvalue().decode('utf-8'))
            return False
    elif deviceRunning == False:
        print("startPlayback - need to restart device.")
        return restartDevice()
    else:
        print("startPlayback: ", status, " - ", buffer.getvalue().decode('utf-8'))
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
                print("pausePlayback pycurl exception: ", pycurl.error)
                return None
            if status == 401:
                print("pausePlayback - refreshing tokens")
                auth.getNewTokens()
                return pausePlayback()
            elif status != 200 or status != 204:
                print("pausePlayback error: ", status)
                return False
    else:       
        print("pausePlayback: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return None

def togglePlayback():
    print('TOGGLE PLAYBACK')
    if getPlaybackState() == True:
        print("togglePlayback - Pausing playback")
        pausePlayback()
        return "Play"
    else:
        print("togglePlayback - start playback")
        startPlayback()
        return "Pause"
    

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
        print("restartSong - pycurl exception: ", pycurl.error)
        return False
    
    if status == 401:
        print("restartSong - refreshing token")
        auth.getNewTokens()
        return nextPlayback()

    elif status != 200 or status != 204:
        print("restartSong: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False

def nextPlayback():
    time.sleep(0.75)

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
        print("nextPlayback - pycurl exception: ", pycurl.error)
        return False
    
    if status == 401:
        print("nextPlayback- refreshing token")
        auth.getNewTokens()
        return nextPlayback()

    elif status != 200 or status != 204:
        print("nextPlayback: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False

def previousPlayback():
    time.sleep(0.75)

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
        print("previousPlayback - pycurl exception: ", pycurl.error)
        return None
    
    if status == 401: 
        print("previousPlayback - refreshing token")
        auth.getNewTokens()
        return previousPlayback()

    elif status != 200 or status != 204:
        print("previousPlayback: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False
    
def volumeChanageable():
    device = getActiveDevice()[0]
    #print("volume = ", device['supports_volume'])
    if device != None:
        return device['supports_volume']
    else:
        print("volumeChanageable - no device found.")
        return None
    
def volumeDown():
    time.sleep(0.75)
    if volumeChanageable() == True:
        buffer = BytesIO()
        c = pycurl.Curl()
        acces_token = auth.getAuthToken()
        authHeader =  [f"Authorization: Bearer {acces_token}"]
        params = {
            'device_id': getActiveDeviceID()[0]
        }

        
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
            print("volumeDown - pycurl exception: ", pycurl.error)
            return None    

        if status == 401:
            print("volumeDown - refreshing token")
            auth.getNewTokens()
            return volumeDown()
        elif status == 204 or status == 200:
            print("turning volume down...")
            return True
        else:
            print("volumeDown error: ", status, " - ", buffer.getvalue().decode('utf-8'))
            return False

def volumeUp():    
    time.sleep(0.75)
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
            print("volumeUp pycurl exception: ", pycurl.error)
            return False       

        if status == 401:
            print("volumeUp - refresh tokens")
            auth.getNewTokens()
            return volumeDown()
        elif status == 204 or status == 200:
            print("turning volume up...")
            return True
        else:
            print("volumeUp error: ", status, " - ", buffer.getvalue().decode('utf-8'))
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
        print("getShuffleState pycurl exception: ", pycurl.error)
        return None
    
    if status == 401:
        print("getshufflestate - refreshing tokens")
        auth.getNewTokens()
        return getShuffleState()
    elif status == 200 or status == 204:
        state = json.loads(buffer.getvalue().decode('utf-8'))['shuffle_state']        
        print("getting shuffle state")

        if state == True:
            print("Checking for smart shuffle")
            smart = json.loads(buffer.getvalue().decode('utf-8'))['smart_shuffle']
            if smart == True:
                return "Smart Shuffled"
            else:
                return "Shuffled" 
        else:
            return "Unshuffled"
    else:
        print("getShuffleState error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return None

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
        print("shuffleOff pycurl exception: ", pycurl.error)
        return None
    
    if status == 401:
        print("shuffleOff- refreshing tokens")
        auth.getNewTokens()
        return shuffleOff()
    elif status == 204 or status == 200:
        print("Turning shuffle off...")
        return True
    else:
        print("shuffleOff error: ", status, " - ", buffer.getvalue().decode('utf-8'))
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
        print("shuffleOn pycurl exception: ", pycurl.error)
        return None
    
    if status == 401:
        print("shuffleOn - refreshing tokens")
        auth.getNewTokens()
        return shuffleOn()
    elif status == 204 or status == 200:
        print("turning shuffle on...:")
        return True
    else:
        print("shuffleOn error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False
    
def toggleShuffle():
    time.sleep(0.75)
    state = getShuffleState()
    if state == "Unshuffled":
        print("shuffle on")
        return shuffleOn()
    elif state == "Shuffled" or state == "Smart Shuffled":
        print("shuffle off")
        return shuffleOff()        
    else:
        print("Cant turn shuffle on or off")
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


    print(buffer)

    if status == 401:
        print("getSongLikedState - refreshing tokens") 
        auth.getNewTokens()
        return getSongLikedState()
    
    elif status == 200 or status == 204:
        state = buffer.getvalue().decode('utf-8').replace('[', '').replace(']', '').replace(' ', '').split(',')
        
        if state[0] == "true": 
            return True
        
        elif state[0] == "false":
            return False
        
        else:
            print("getSongLikedState - Can't get song liked state.")
            return None
    
    else:
        print("getSongLikedState: ", status, " - ", buffer.getvalue().decode('utf-8'))
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
        print("likeSong - can't get current track type.")
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
        print("likeSong pycurl exception: ", pycurl.error)
        return None

    if status == 401:
        print("likeSong - refresh tokens") 
        auth.getNewTokens()
        return likeSong()
    elif status == 200 or status == 204:
        print("Liking track...")
        return True
    else:
        print("likeSong: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False

def unlikeSong():
    acces_token = auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = pycurl.Curl()

    headers = []
    headers.append(authHeader[0])
    headers.append("Content-Type: application/json")

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
        print("unlikeSong pycurl exception: ", pycurl.error)
        return None

    if status == 401:
        print("unlikeSong - refresh tokens")
        auth.getNewTokens()
        return likeSong()
    elif status == 200 or status == 204:
        print("unliking track...")
        return True
    else:
        print("unlikeSong: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False

def toggleLikeSong():
    state = getSongLikedState()

    if state == True:
        return unlikeSong()
    elif state == False:
        return likeSong()
    else:
        print("toggleLikeSong error: ", state)
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
        print("getRepeatState pycurl exception: ", pycurl.error)
        return None

    if status == 401:
        print("getRepeatState - refreshing tokens")
        auth.getNewTokens()
        return getRepeatState()
    
    elif status == 200 or status == 204:
        if buffer:
            state = json.loads(buffer.getvalue().decode('utf-8'))['repeat_state'] 
            return state
        else:
            print("Buffer Error")
            return None
    else:
        print("getRepeatState: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return None

def toggleRepeat():
    time.sleep(0.75)
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
            print("Repeat state error, state: ", state)
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
            print("toggleRepeat pycurl exception: ", pycurl.error)
            return None

        if status == 401:
            print("toggleRepeat - refreshing tokens")
            auth.getNewTokens()
            return toggleRepeat()
        
        elif status == 204 or status == 200:
            print("toggleRepeatn - Changing repeat mode...")
            return True
        
        else:
            print("toggleRepeat error: ", status, " - ", buffer.getvalue().decode('utf-8'))
            return None
    else:
        print("toggleRepeat - cant repeat, current track is not a song: ")
        return None

def refreshTokens():
    
    while True:
        time.sleep(3000)
        print("Getting new tokens")  
        auth.getNewTokens()