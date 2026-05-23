import time
import asyncio
import urllib.parse
import urllib3
import auth
import requests
import threading
import pycurl
import json
from io import BytesIO
import aiocurl
currentSong = ""

async def getActiveDeviceID() -> tuple: 
    """
    Gets the active device ID and returns it along with the device's active (true or false) state.
    If no device is active, returns (None, None)
    
    :return: tuple containing the device and whether it is active or not 
    (e.g. ('my iPhone', false)).
    """
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    buffer = BytesIO()
    c = aiocurl.Curl()
    status = None

    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/devices")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("get active device id pycurl exception: ", pycurl.error)
        return(None, None)
    
    # if http error 401, refresh tokens
    if status == 401:
        print("get active device id - refreshing tokens")
        await auth.getNewTokens()
        return await getActiveDeviceID()
        

    elif status == 200 or status == 204:
        devices = json.loads(buffer.getvalue().decode('utf-8'))['devices']

        #find active device and return it
        for dev in devices:
            if dev['is_active'] == True:
                print("getActiveDeviceID - device found.")
                return (dev['id'], True)
        
        #if no active device is available, return first device
        if len(devices) > 0:
            print("getActiveDeviceID - inactive device found.")
            return (devices[0]['id'], False)
        #return None if no devices.
        else:
            #
            print("getActiveDeviceID - No devices found.")
            return(None, False)
    
    #catch for all other http errors
    else:
        print("getActiveDeviceID error: ", status, " - ", json.loads(buffer.getvalue().decode('utf-8')))
        return(None, None)

async def getActiveDevice() -> tuple: 
    """
    Gets the active device and returns it along with the device's active (true or false) state.
    If no device is active, returns (None, None).

    :return: tuple containing the device and whether it is active or not 
    (e.g. ('my iPhone', false)).
    """

    acces_token = await auth.getAuthToken()
    
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    buffer = BytesIO()
    c = aiocurl.Curl()
    status = None

    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/devices")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("getActiveDevice - pycurl exception: ", status, " ", pycurl.error)
        return(None, None)

    # if http error 401, refresh tokens
    if status == 401:
        print("getActiveDevice - refreshing tokens")
        await auth.getNewTokens()
        return await getActiveDevice()
    
    elif status == 200 or status == 204:
        devices = json.loads(buffer.getvalue().decode('utf-8'))['devices']
        
        #find active device and return it
        for dev in devices:
            if dev['is_active'] == True:
                #print("getActiveDevice - device found.")
                return (dev, True)
        
        #if no active device is available, return first device
        if len(devices) > 0:
            print("getActiveDevice - inactive device found.")
            return (devices[0], False)
        
        #return None, no device found.
        else:
            print("getActiveDevice, no device found.")
            return(None, False)
    else:

        #catch all for all other http errors 
        print("getActiveDevice: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return(None, None)

async def getCurrentPlayingType() -> str:
    
    """
    Gets the type of the current playing track (song or podcast)

    :return: string containing the type as either 'track' for a song or 'episode' for a podcast episode 
    """
     
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = aiocurl.Curl()
    status = None

    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/currently-playing")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)

    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()
    except pycurl.error:
        print("getCurrentPlayingType pycurl exception: ", pycurl.error)
        return None
    
    #http error 401 - refresh tokens
    if status == 401:
        print("get current playing type - refresh tokens")
        await auth.getNewTokens()
        return await getCurrentPlayingType()
    
    elif status == 200 or status == 204: 
        return json.loads(buffer.getvalue().decode('utf-8'))['currently_playing_type']
    
    else:
        #catch all for http errors
        print("get current playing type error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return None

async def getCurrentSongID() -> str:
    """
    Gets the ID the current playing track (song or podcast)

    :return: string containing the ID of the currently playing track 
    """

    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = aiocurl.Curl()
    status = None

    type = await getCurrentPlayingType()

    if type == 'track': 
        c.setopt(c.URL, "https://api.spotify.com/v1/me/player/currently-playing")
    elif type == 'episode':
        c.setopt(c.URL, "https://api.spotify.com/v1/me/player/currently-playing?additional_types=episode")
    else:
        print("getCurrentSongID - Cant get current type")
        return None
    
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()
    except pycurl.error:
        print("getCurrentSongID - pycurl exception: ", pycurl.error)      
        return None
    
    #http error 401 - refresh tokens
    if status == 401:
        print("getCurrentSongID - refreshing tokens")
        await auth.getNewTokens()
        return await getCurrentSongID()
    
    elif status == 200 or status == 204:
        return json.loads(buffer.getvalue().decode('utf-8'))['item']['id']
    
    else:
        #catch all for http errors
        print("getCurrentSongAndArtist: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return None
            
async def getCurrentSongAndArtist() -> tuple:
    """
    Gets the name of the current song and artist

    :return: tuple containing song name and artist (e.g. (song, artist)).
    """
    global currentSongAndArtist
    acces_token = await auth.getAuthToken()
    if acces_token == None:
        return "Restart Spotify Overlay"
    
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    buffer = BytesIO()
    c = aiocurl.Curl()    
    status = None
    playingType = await getCurrentPlayingType()
    if playingType == "episode":
        c.setopt(aiocurl.URL, "https://api.spotify.com/v1/me/player/currently-playing?additional_types=episode")
    elif playingType == 'track':
        c.setopt(aiocurl.URL, "https://api.spotify.com/v1/me/player/currently-playing")
    
    #if not playing a track or episode, return none.
    else:
        currentSongAndArtist = (None, None)

    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()
    except pycurl.error:
        print("getCurrentSongAndArtist - pycurl exception: ", status, " - ", pycurl.error)
        return (None, None)

    #http error 401 - refresh tokens
    if status == 401:
        print("getCurrentSongAndArtist - refreshing tokens")
        await auth.getNewTokens()
        return await getCurrentSongAndArtist()
    elif status == 200 or status == 204:
        response = json.loads(buffer.getvalue().decode('utf-8'))


        if playingType == "track":
            currentSongAndArtist = (response['item']['name'], response['item']['artists'][0]['name'])
        elif playingType == "episode":
            currentSongAndArtist = (response['item']['name'], response['item']['show']['name'])
        else:
            print("getCurrentSongAndArtist - track type undefined")
            currentSongAndArtist = (None, None)
    else:
        #catch all for http errors.
        print("getCurrentSongAndArtist: ", status, " - ", buffer.getvalue().decode('utf-8'))
        currentSongAndArtist = (None, None)
    return currentSongAndArtist

async def getProgressAndDuration() -> tuple:

    """
    Gets the current timestamp and duration of a track/episode in milliseconds.

    :return: tuple containing time stamp and duration in ms (e.g. (105000, 225000)).
    """
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    buffer = BytesIO()
    c = aiocurl.Curl()
    status = None

    playingType = await getCurrentPlayingType()
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
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("getProgressAndDuration - pycurl exception: ", pycurl.error)
        return(None, None)


    #http error 401 - refresh tokens
    if status == 401:
        print("getProgressAndDuration - refreshing tokens")
        await auth.getNewTokens()
        return await getProgressAndDuration()
    elif status == 200 or status == 204:
        progress = json.loads(buffer.getvalue().decode('utf-8'))
        #print("getProgressAndDuration - Returning progress and duration...")
        return (progress['progress_ms'], progress['item']['duration_ms'])
        
    else:
        #catch all other http errors
        print("getProgressAndDuration: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return (None, None)

async def seekToPosition(position: int) -> bool: 

    """
    Sets the current timestamp according to the position given.

    :param position: int representing the time in milliseconds to seek to.
    :return: bool representing if the seek was successful or not.
    """
    
    
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]    
    buffer = BytesIO()
    c = aiocurl.Curl()
    status = None
    device = await getActiveDeviceID()
    device = device[0]
    if device == None:
        print("seekToPosition error: no device found.")
        return False
    
    
    params = {
            'device_id': device,
    }

    c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/seek?position_ms={position}")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.CUSTOMREQUEST, "PUT")
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("seekToPosition pycurl exception: ", pycurl.error)
        return False
    
    #print("STATUS: " , status)


    if status == 401:
        print("seekToPosition - refreshing token")
        await auth.getNewTokens()
        return await seekToPosition()

    #catch all for http errors
    elif status != 200 or status != 204:
        print("seekToPosition: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False
    
    #seek to position successful
    else:
        return True

async def restartDevice() -> bool: 

    """
    Restarts inactive device and resumes playback.

    :return: bool representing if the restart was successful or not.
    """

    buffer = BytesIO()
    c = aiocurl.Curl()
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    id = await getActiveDeviceID()
    id = id[0]
    status = None
    #no device found, return none.
    if id == None:
        print("restartDevice error: no device found to restart.")
        return False    
    
    params = {
        'device_ids': [id],
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
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("restartDevice pycurl exception: ", pycurl.error)
        return None

    #http error 401 - refresh tokens
    if status  == 401: 
        print("restartDevice - refreshing token")
        await auth.getNewTokens()
        return await restartDevice()

    #start playback after restarting device
    elif status == 204 or status == 200:
        print("restarting device")
        await startPlayback()
        return True
    else:
        #catch for http errors
        print("restartDevice error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False

async def getPlaybackState() -> bool:

    """
    Returns playback state (playing or not).

    :return: bool representing true for playing and false for not.
    """

    status = None
    buffer = BytesIO()
    c = aiocurl.Curl()
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    c.setopt(c.URL, "https://api.spotify.com/v1/me/player")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("getPlaybackState pycurl exception: ", pycurl.error)
        return None

    #http error 401 - refresh tokens
    if status == 401:
        print("getplaybackstate - refreshing tokens")
        await auth.getNewTokens()
        return await getPlaybackState()
    elif status == 200 or status == 204:
        playbackState = json.loads(buffer.getvalue().decode('utf-8'))['is_playing']        
        return playbackState
    
    #catch for http errors
    else:
        print("getPlaybackState: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return None

async def startPlayback() -> bool:
    """
    Starts playback.

    :return: bool representing if starting playback was successful or not.
    """
    status = None
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    
    device = await getActiveDeviceID()
    id, deviceRunning = device
    if id != None:
        if deviceRunning == True:
            state = await getPlaybackState()
            if state == False:
                buffer = BytesIO()
                c = aiocurl.Curl()

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
                    await c.perform()
                    status = c.getinfo(c.RESPONSE_CODE)
                    c.close()        
                except pycurl.error:
                    print("startPlayback pycurl exception: ", pycurl.error)
                    return False
                
                #http error 401 - refresh tokens
                if status == 401:
                    print("start playback - refreshing tokens")
                    await auth.getNewTokens()
                    return await startPlayback()
                elif status == 204 or status == 200:
                    print("starting playback...")
                    return True
                
                #catch http errors
                else:
                    print("startPlayback error: ", status, " - ", buffer.getvalue().decode('utf-8'))
                    return False
            else:
                print("Already Playing")
                return True
        elif deviceRunning == False:
            print("startPlayback - need to restart device.")
            return await restartDevice()
        else:
            print("startPlayback: ", status, " - ", buffer.getvalue().decode('utf-8'))
            return False
    
    #no device found, return false
    else:
        return False

async def pausePlayback() -> bool:
    """
    Pause playback.

    :return: bool representing if pausing playback was successful or not.
    """
    status = None
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    
    device = await getActiveDeviceID()
    id, deviceRunning = device
    if id != None:
        if deviceRunning == True:
            buffer = BytesIO()
            c = aiocurl.Curl()

            params = {
                    'device_id': id,
            }

            c.setopt(aiocurl.URL, "https://api.spotify.com/v1/me/player/pause")
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
            c.setopt(c.HTTPHEADER, authHeader)
            c.setopt(c.CUSTOMREQUEST, "PUT")
            try:   
                await c.perform()
                status = c.getinfo(c.RESPONSE_CODE)
                c.close()        
            except pycurl.error:
                print("pausePlayback pycurl exception: ", pycurl.error)
                return False
            
            #http error 401 - refresh tokens
            if status == 401:
                print("pausePlayback - refreshing tokens")
                await auth.getNewTokens()
                return await pausePlayback()
            elif status != 200 or status != 204:
                print("pausePlayback error: ", status)
                return False

            #catch http errors
            else:       
                print("pausePlayback: ", status, " - ", buffer.getvalue().decode('utf-8'))
                return False
    
    #no device found, return false
    else:
        return False

async def togglePlayback():
    """
    Toggle playback.

    """
    print('TOGGLE PLAYBACK')
    if await getPlaybackState() == True:
        print("togglePlayback - Pausing playback")
        await pausePlayback()
    else:
        print("togglePlayback - start playback")
        await startPlayback()
    
async def restartSong() -> bool:

    """
    Restart a track from the beginning.

    :return: bool representing if restart was successful or not.
    """
    status = None
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]    
    buffer = BytesIO()
    c = aiocurl.Curl()

    id = await getActiveDeviceID()
    id = id[0]
    
    #no device found, return none.
    if id == None:
        print("restartDevice error: no device found to restart.")
        return False
    
    params = {
            'device_id': id,
    }

    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/seek?position_ms=0")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.CUSTOMREQUEST, "PUT")
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("restartSong - pycurl exception: ", pycurl.error)
        return False
    
    #http error 401 - refresh tokens
    if status == 401:
        print("restartSong - refreshing token")
        await auth.getNewTokens()
        return await restartSong()

    #catch http errors
    elif status != 200 or status != 204:
        print("restartSong: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False
    else:
        return True
    
async def nextPlayback() -> bool:
    """
    Skip to next track.

    :return: bool representing if skipping to next track was successful or not.
    """
    status = None
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]    
    buffer = BytesIO()
    c = aiocurl.Curl()

    id = await getActiveDeviceID()
    id = id[0]
    
    #no device found, return none.
    if id == None:
        print("nextPlayback error: no device found.")
        return False
    
    params = {
            'device_id': id,
    }

    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/next")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("nextPlayback - pycurl exception: ", pycurl.error)
        return False
    
    #http 401 error - refresh tokens
    if status == 401:
        print("nextPlayback- refreshing token")
        await auth.getNewTokens()
        return await nextPlayback()

    #catch http errors
    elif status != 200 or status != 204:
        print("nextPlayback: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False
    else:
        return True

async def previousPlayback() -> bool:
    """
    Goes back to previous track.

    :return: bool representing if going back to previous track was successful or not.
    """
    status = None
    buffer = BytesIO()
    c = aiocurl.Curl()
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    
    id = await getActiveDeviceID()
    id = id[0] 
    
    #no device found, return none.
    if id == None:
        print("previousPlayback error: no device found.")
        return False
    
    params = {
            'device_id': id,
    }
    c.setopt(c.URL, "https://api.spotify.com/v1/me/player/previous")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("previousPlayback - pycurl exception: ", pycurl.error)
        return False
    
    #http error 401 - refresh tokens
    if status == 401: 
        print("previousPlayback - refreshing token")
        await auth.getNewTokens()
        return await previousPlayback()

    #catch http errors
    elif status != 200 or status != 204:
        print("previousPlayback: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False
    else:
        return True 
    
async def volumeChangeable() -> bool:
    """
    Determines if current playing device supports changing volume through API.

    :return: bool representing if volume changing is supported or not.
    """
    device = await getActiveDevice()
    device = device[0]
    #print("volume = ", device['supports_volume'])
    if device != None:
        return device['supports_volume']
    else:
        print("volumeChanageable - no device found.")
        return None
    
async def volumeDown() -> bool:
    """
    Lowers volume.

    :return: bool representing if volume lowering was successful or not.
    """
    

    changeable = await volumeChangeable()
    if changeable == True:
        buffer = BytesIO()
        c = aiocurl.Curl()
        acces_token = await auth.getAuthToken()
        authHeader =  [f"Authorization: Bearer {acces_token}"]

        id = await getActiveDeviceID()
        id = id[0]
        
        #no device found, return none.
        if id == None:
            print("volumeDown error: no device found.")
            return False
        
        params = {
                'device_id': id,
        }
        
        device = await getActiveDevice()
        status = None
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/volume?volume_percent={device[0]['volume_percent'] - 10}")
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
        c.setopt(c.CUSTOMREQUEST, "PUT")
        c.setopt(c.HTTPHEADER, authHeader)
        try:   
            await c.perform()
            status = c.getinfo(c.RESPONSE_CODE)
            c.close()        
        except pycurl.error:
            print("volumeDown - pycurl exception: ", pycurl.error)
            return False    

        #http error 401 - refresh tokens
        if status == 401:
            print("volumeDown - refreshing token")
            await auth.getNewTokens()
            return await volumeDown()
        elif status == 204 or status == 200:
            print("turning volume down...")
            return True
        
        #catch http errors
        else:
            print("volumeDown error: ", status, " - ", buffer.getvalue().decode('utf-8'))
            return False

async def volumeUp() -> bool: 
    """
    Raises volume.

    :return: bool representing if volume raising was successful or not.
    """
    changeable = await volumeChangeable()
    if changeable == True:
        #print("volume changable")
        buffer = BytesIO()
        c = aiocurl.Curl()
        acces_token = await auth.getAuthToken()
        authHeader =  [f"Authorization: Bearer {acces_token}"]
        
        id = await getActiveDeviceID()
        id = id[0] 
        
        #no device found, return none.
        if id == None:
            print("volumeUp error: no device found.")
            return False
        
        params = {
                'device_id': id,
        }
        #print("params = ", urllib.parse.urlencode(params))
        
        device = await getActiveDevice()
        status = None

        c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/volume?volume_percent={device[0]['volume_percent'] + 10}")
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
        c.setopt(c.CUSTOMREQUEST, "PUT")
        c.setopt(c.HTTPHEADER, authHeader)
        try:   
            await c.perform()
            status = c.getinfo(c.RESPONSE_CODE)
            c.close()        
        except pycurl.error:
            print("volumeUp pycurl exception: ", pycurl.error)
            return False       

        #http error 401 - refresh tokens
        if status == 401:
            print("volumeUp - refresh tokens")
            await auth.getNewTokens()
            return await volumeDown()
        elif status == 204 or status == 200:
            print("turning volume up...")
            return True
        else:
            print("volumeUp error: ", status, " - ", buffer.getvalue().decode('utf-8'))
            return False
      
async def getShuffleState() -> str:

    """
    Returns the current shuffle state (shuffled, smart shuffled or unshuffled).

    :return: string representing the shuffle state (e.g. "Unshuffled").
    """
    status = None

    buffer = BytesIO()
    c = aiocurl.Curl()
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    c.setopt(c.URL, "https://api.spotify.com/v1/me/player")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("getShuffleState pycurl exception: ", pycurl.error)
        return None
    
    #http error 401 - refresh tokens
    if status == 401:
        print("getshufflestate - refreshing tokens")
        await auth.getNewTokens()
        return await getShuffleState()
    elif status == 200 or status == 204:
        state = json.loads(buffer.getvalue().decode('utf-8'))['shuffle_state']        
        #print("getting shuffle state")

        if state == True:
            #print("Checking for smart shuffle")
            smart = json.loads(buffer.getvalue().decode('utf-8'))['smart_shuffle']
            if smart == True:
                return "Smart Shuffled"
            else:
                return "Shuffled" 
        else:
            return "Unshuffled"
    
    #catch http errors
    else:
        print("getShuffleState error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return None

async def shuffleOff() -> bool:

    """
    Turns shuffle off

    :return: bool representing if turning shuffle off was successful.
    """
    status = None
        
    buffer = BytesIO()
    c = aiocurl.Curl()
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]    
    
    id = await getActiveDeviceID()
    id = id[0] 
    
    #no device found, return none.
    if id == None:
        print("shuffleOff error: no device found.")
        return False
    
    params = {
            'device_id': id,
    }

    c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/shuffle?state={False}")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CUSTOMREQUEST, "PUT")
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("shuffleOff pycurl exception: ", pycurl.error)
        return False
    
    #http error 401 - refresh tokens
    if status == 401:
        print("shuffleOff- refreshing tokens")
        await auth.getNewTokens()
        return shuffleOff()
    elif status == 204 or status == 200:
        print("Turning shuffle off...")
        return True
    
    #catch http errors
    else:
        print("shuffleOff error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False
    
async def shuffleOn() -> bool:
    """
    Turns shuffle on

    :return: bool representing if turning shuffle on was successful.
    """
    status = None
    buffer = BytesIO()
    c = aiocurl.Curl()
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    id = await getActiveDeviceID()
    id = id[0] 
    
    #no device found, return none.
    if id == None:
        print("shuffleOn error: no device found.")
        return False
    
    params = {
            'device_id': id,
    }
    
    c.setopt(c.URL, f"https://api.spotify.com/v1/me/player/shuffle?state={True}")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CUSTOMREQUEST, "PUT")
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("shuffleOn pycurl exception: ", pycurl.error)
        return False
    
    #http error 401 - refresh tokens
    if status == 401:
        print("shuffleOn - refreshing tokens")
        await auth.getNewTokens()
        return shuffleOn()
    elif status == 204 or status == 200:
        print("turning shuffle on...:")
        return True
    
    #catch http errors
    else:
        print("shuffleOn error: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False
    
async def toggleShuffle() -> bool:
    """
    Toggles shuffle

    :return: bool representing if toggling shuffle was successful.
    """
    state = await getShuffleState()
    if state == "Unshuffled":
        print("shuffle on")
        return await shuffleOn()
    elif state == "Shuffled" or state == "Smart Shuffled":
        print("shuffle off")
        return await shuffleOff()        
    else:
        print("Cant turn shuffle on or off")
        return False

async def getSongLikedState() -> bool:
    """
    Returns whether or not a track is liked or not

    :return: bool representing if a track is liked (e.g. True for liked),
    """  
    status = None
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = aiocurl.Curl()

    type = await getCurrentPlayingType()
    if type  == "track":
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/tracks/contains?ids={await getCurrentSongID()}")
    elif type == 'episode':
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/episodes/contains?ids={await getCurrentSongID()}")
    else:
        #print("Cant get liked state")
        return False
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        #print("get liked state exception: ", pycurl.error)
        return False


    #print(buffer)

    #http error 401 - refresh tokens
    if status == 401:
        print("getSongLikedState - refreshing tokens") 
        await auth.getNewTokens()
        return await getSongLikedState()
    
    elif status == 200 or status == 204:
        state = buffer.getvalue().decode('utf-8').replace('[', '').replace(']', '').replace(' ', '').split(',')
        
        if state[0] == "true": 
            return True
        
        elif state[0] == "false":
            return False
        
        else:
            print("getSongLikedState - Can't get song liked state.")
            return None
    
    #catch http errors
    else:
        print("getSongLikedState: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return None

async def likeSong() -> bool:

    """
    Likes a track for the user

    :return: bool representing if liking the track was successful.
    """   
    status = None
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = aiocurl.Curl()

    headers = []
    headers.append(authHeader[0])
    headers.append("Content-Type: application/json")
    #print(headers)
    
    ids = await getCurrentSongID()

    if ids != None:
        print("likeSong error - no device found")
        return False
    
    params = {
            'ids': ids
    }    

    type = await getCurrentPlayingType()
    if type == "track":
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/tracks?ids={getCurrentSongID()}")
    elif type == "episode":    
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/episodes?ids={getCurrentSongID()}")
    else:
        print("likeSong - can't get current track type.")
        return False
        
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.CUSTOMREQUEST, "PUT")
    
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("likeSong pycurl exception: ", pycurl.error)
        return False

    #http error 401 - refresh tokens
    if status == 401:
        print("likeSong - refresh tokens") 
        await auth.getNewTokens()
        return likeSong()
    elif status == 200 or status == 204:
        print("Liking track...")
        return True
    
    #catch http errors
    else:
        print("likeSong: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False

async def unlikeSong() -> bool:

    """
    Unlikes a track for the user

    :return: bool representing if unliking the track was successful.
    """   
    status = None
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = aiocurl.Curl()

    headers = []
    headers.append(authHeader[0])
    headers.append("Content-Type: application/json")

    ids = await getCurrentSongID()

    if ids != None:
        print("unlikeSong error - no device found")
        return False
    
    params = {
            'ids': ids
    }    
  

    type = await getCurrentPlayingType()
    if type == "track":
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/tracks?ids={await getCurrentSongID()}")
    elif type == "episode":    
        c.setopt(c.URL, f"https://api.spotify.com/v1/me/episodes?ids={await getCurrentSongID()}")
    else:
        print("unlikeSong error - cant determine track type.")
        return False
        
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.CUSTOMREQUEST, "DELETE")
    
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("unlikeSong pycurl exception: ", pycurl.error)
        return False
    
    #http error 401 - refresh tokens
    if status == 401:
        print("unlikeSong - refresh tokens")
        await auth.getNewTokens()
        return await likeSong()
    elif status == 200 or status == 204:
        print("unliking track...")
        return True
    
    #catch http errors
    else:
        print("unlikeSong: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return False

async def toggleLikeSong() -> bool:
    """
    Toggles like

    :return: bool representing if toggling like was successful.
    """
    state = getSongLikedState()

    if state == True:
        return await unlikeSong()
    elif state == False:
        return await likeSong()
    else:
        print("toggleLikeSong error: ", state)
        return False

async def getRepeatState() -> str:
    """
    Determines if repeat is enabled or not

    :return: string representing repeat state (e.g. "Repeat On").
    """
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]

    buffer = BytesIO()
    c = aiocurl.Curl()
    status = None
    c.setopt(c.URL, "https://api.spotify.com/v1/me/player")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, authHeader)
    try:   
        await c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()        
    except pycurl.error:
        print("getRepeatState pycurl exception: ", pycurl.error)
        return None

    #http error 401 - refresh tokens
    if status == 401:
        print("getRepeatState - refreshing tokens")
        await auth.getNewTokens()
        return getRepeatState()
    
    elif status == 200 or status == 204:
        if buffer:
            state = json.loads(buffer.getvalue().decode('utf-8'))['repeat_state'] 
            return state
        else:
            print("Buffer Error")
            return None
        
    #catch http errors
    else:
        print("getRepeatState: ", status, " - ", buffer.getvalue().decode('utf-8'))
        return None

async def toggleRepeat() -> bool:
    """
    Toggles repeat

    :return: bool representing if toggling repeat was successful.
    """
    status = None
    acces_token = await auth.getAuthToken()
    authHeader =  [f"Authorization: Bearer {acces_token}"]
    playingType = await getCurrentPlayingType()
    if playingType == "track":
        buffer = BytesIO()
        c = aiocurl.Curl()

        headers = []
        headers.append(authHeader[0])
        headers.append("Content-Type: application/json")
        
        state = await getRepeatState()
        id = await getActiveDeviceID()
        id = id[0] 
        
        #no device found, return none.
        if id == None:
            print("nextPlayback error: no device found.")
            return False
        
        params = {
                'device_id': id,
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
            return False
        
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.POSTFIELDS, urllib.parse.urlencode(params))
        c.setopt(c.HTTPHEADER, headers)
        c.setopt(c.CUSTOMREQUEST, "PUT")
        try:   
            await c.perform()
            status = c.getinfo(c.RESPONSE_CODE)
            c.close()        
            #print("status - ", status)
        except pycurl.error:
            print("toggleRepeat pycurl exception: ", pycurl.error)
            return False
        
        #http 401 error - refresh tokens
        if status == 401:
            print("toggleRepeat - refreshing tokens")
            await auth.getNewTokens()
            return toggleRepeat()
        
        elif status == 204 or status == 200:
            print("toggleRepeatn - Changing repeat mode...")
            return True
        
        #catch http errors
        else:
            print("toggleRepeat error: ", status, " - ", buffer.getvalue().decode('utf-8'))
            return False
    
    #couldnt repeat because track is not a song.
    else:
        print("toggleRepeat - cant repeat, current track is not a song: ")
        return False

async def refreshTokens():
    
    while True:
        await asyncio.sleep(3000)
        print("Getting new tokens")  
        await auth.getNewTokens()