import time
import auth
import requests
import threading


acces_token = auth.getToken()

header =  {
    'Authorization': "Bearer " + acces_token
}

def getActiveDeviceID():
    devices = requests.get(url="https://api.spotify.com/v1/me/player/devices", headers=header)

    if devices.status_code == 401:
        auth.getNewtokens()
        getActiveDeviceID()

    else:
        devices = devices.json()['devices']

        for dev in devices:
            if dev['is_active'] == True:
                return (dev['id'], True)
            
        if len(devices) > 0:
            return (devices[0]['id'], False)
        else:
            return(None, False)

def getActiveDevice():
    devices = requests.get(url="https://api.spotify.com/v1/me/player/devices", headers=header)

    if devices.status_code == 401:
        auth.getNewtokens()
        getActiveDeviceID()

    else:
        devices = devices.json()['devices']

        for dev in devices:
            if dev['is_active'] == True:
                return (dev, True)
            
        if len(devices) > 0:
            return (devices[0], False)
        else:
            return(None, False)

def restartDevice():
    params = {
        'device_id': getActiveDeviceID()[0],
    }

    restart = requests.put(url="https://api.spotify.com/v1/me/player", params=params, headers=header)
    if restart.status_code == 401:
        print("refreshing token")
        auth.getNewtokens()
        restartDevice()

def getPlaybackState():
    response = requests.get(url="https://api.spotify.com/v1/me/player", headers=header)

    if response.status_code == 401:
        auth.getNewtokens()
        getPlaybackState()
    elif response.status_code == 200:
        playbackState = response.json()['is_playing']        
        #print("PLAYBACK STATE: ", playbackState)
        return playbackState
    else:
        print("Cant get playback state")
        return None

def startPlayback():
    params = {
        'device_id': getActiveDeviceID()[0],
    }

    start = requests.put(url="https://api.spotify.com/v1/me/player/play", params=params, headers=header)

    if start.status_code == 401:
        print("refreshing token")
        auth.getNewtokens()
        startPlayback()

def pausePlayback():
    params = {
        'device_id': getActiveDeviceID()[0],
    }

    pause = requests.put(url="https://api.spotify.com/v1/me/player/pause", params=params, headers=header)
    if pause.status_code == 401:
        print("refreshing token")
        auth.getNewtokens()
        pausePlayback()

def togglePlayback():
    if getPlaybackState() == True:
        pausePlayback()
    else:
        startPlayback()

def nextPlayback():
    params = {
        'device_id': getActiveDeviceID()[0],
    }

    next = requests.post(url="https://api.spotify.com/v1/me/player/next", params=params, headers=header)
    if next.status_code == 401:
        print("refreshing token")
        auth.getNewtokens()
        nextPlayback()

def previousPlayback():
    params = {
        'device_id': getActiveDeviceID()[0],
    }

    previous = requests.post(url="https://api.spotify.com/v1/me/player/previous", params=params, headers=header)
    if previous.status_code == 401:
        print("refreshing token")
        auth.getNewtokens()
        previousPlayback()

def volumeChanageable():
    return getActiveDevice()[0]['supports_volume']

def volumeDown():
    if volumeChanageable() == True:

        params = {
            'device_id': getActiveDeviceID()[0],
            'volume_percent': getActiveDevice()[0]['volume_percent'] - 10
        }
        
        response = requests.put(url="https://api.spotify.com/v1/me/player/volume", params=params, headers=header)

        if response.status_code == 401:
            auth.getNewtokens()
            volumeDown()

def volumeUp():
    if volumeChanageable() == True:

        params = {
            'device_id': getActiveDeviceID()[0],
            'volume_percent': getActiveDevice()[0]['volume_percent'] + 10
        }
        
        response = requests.put(url="https://api.spotify.com/v1/me/player/volume", params=params, headers=header)

        if response.status_code == 401:
            auth.getNewtokens()
            volumeDown()

def getShuffleState():
    response = requests.get(url="https://api.spotify.com/v1/me/player", headers=header)

    if response.status_code == 401:
        auth.getNewtokens()
        getShuffleState()
    elif response.status_code == 200:
        shuffleState = response.json()['shuffle_state']
        #print("SHUFFLE STATE: ", shuffleState)
        
        return shuffleState
    else:
        return None

def shuffleOn():
    params = {
        'state': True
    }
    response = requests.put(url="https://api.spotify.com/v1/me/player/shuffle", params=params, headers=header)

    if response.status_code == 401:
        auth.getNewtokens()
        shuffleOn()
    
def shuffleOff():
    params = {
        'state': False
    }
    response = requests.put(url="https://api.spotify.com/v1/me/player/shuffle", params=params, headers=header)

    if response.status_code == 401:
        auth.getNewtokens()
        shuffleOff()
    
def toggleShuffle():
    state = getShuffleState()
    if state == True:
        shuffleOff()
        print("shuffle off")
    elif state == False:
        shuffleOn()        
        print("shuffle on")

    else:
        print("Cant turn shuffle on or off")

def getCurrentSongID():
        if getCurrentPlayingType() == 'track': 
            response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=header)
            if response.status_code == 401:
                auth.getNewtokens()
                getCurrentSongID()
            return response.json()['item']['id']
        elif getCurrentPlayingType() == 'episode':
            response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", params={"additional_types": "episode" }, headers=header)
            if response.status_code == 401:
                auth.getNewtokens()
                getCurrentSongID()
            return response.json()['item']['id']
        else:
            return None
            
def getCurrentPlayingType():
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=header)

    if response.status_code == 401:
        auth.getNewtokens()
        getCurrentPlayingType()
    elif response.status_code == 200: 
        return response.json()['currently_playing_type']
    else:
        print("error: ", response.status_code, response.content.decode('utf-8'))
        return None

def getCurrentSongAndArtist():
    response = ""
    if getCurrentPlayingType() == "episode":
        response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", params= {"additional_types": "episode"}, headers=header)
    else:
        response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=header)

    if response.status_code == 401:
        auth.getNewtokens()
        getCurrentSongAndArtist()
    elif response.status_code == 200:
        if getCurrentPlayingType() == "track":
            return response.json()['item']['name'] + " - " + response.json()['item']['artists'][0]['name']
        elif getCurrentPlayingType() == "episode":
            return response.json()['item']['name'] + " - " + response.json()['item']['show']['name']
    else:
        print("Can't get current song")
        return "Can't get current song or no song is currently playing"
    


def getSongLikedState():
    params = {
        'ids': getCurrentSongID()
    }
  
    if getCurrentPlayingType() == "track":
        containsTrack = requests.get("https://api.spotify.com/v1/me/tracks/contains", params=params, headers=header)
        
        if containsTrack.status_code == 401:
            auth.getNewtokens()
            getSongLikedState()
        else:
            return containsTrack.json()[0] 

    elif getCurrentPlayingType() == 'episode':
        id = getCurrentSongID()
        containsEpisode = requests.get("https://api.spotify.com/v1/me/episodes/contains", params=params, headers=header)

        if containsEpisode.status_code == 401:
            auth.getNewtokens()
            getSongLikedState()
        else:
            return containsEpisode.json()[0]
        
    else:
        print("Can't like current track type")
        return None
        
def likeSong():
    params = {
            'ids': getCurrentSongID()
    }
    
    if getCurrentPlayingType() == "track":
        response = requests.put("https://api.spotify.com/v1/me/tracks", params=params, headers=header)
        if response.status_code == 401:
            auth.getNewtokens()
            likeSong()
        elif response.status_code != 200:
            print("like track error: ", response.status_code)
        else:
            pass
    elif getCurrentPlayingType() == "episode":
        response = requests.put("https://api.spotify.com/v1/me/episodes", params=params, headers=header)
        if response.status_code == 401:
            auth.getNewtokens()
            likeSong()
        elif response.status_code != 200:
            print("like episode error: ", response.status_code)
        else:
            pass
    else:
        print("Cant like current song")

def unlikeSong():
    params = {
            'ids': getCurrentSongID()
    }
    
    if getCurrentPlayingType() == "track":
        response = requests.delete("https://api.spotify.com/v1/me/tracks", params=params, headers=header)
        if response.status_code == 401:
            auth.getNewtokens()
            unlikeSong()
        elif response.status_code != 200:
            print("unlike track error: ", response.status_code)
        else:
            pass
    elif getCurrentPlayingType() == "episode":
        response = requests.delete("https://api.spotify.com/v1/me/episodes", params=params, headers=header)
        if response.status_code == 401:
            auth.getNewtokens()
            unlikeSong()
        elif response.status_code != 200:
           print("unlike episode error: ", response.status_code)
        else:
            pass
    else:
        print("Cant like current song")

def toggleLikeSong():
    state = getSongLikedState()

    if state == True:
        unlikeSong()
    elif state == False:
        likeSong()
    else:
        print("Can't like/unlike current track")

def getRepeatState():
    state = requests.get(url="https://api.spotify.com/v1/me/player", headers=header)
    state = state.json()['repeat_state']
    
    if state != None:
        return state
    else:
        print("Can't get repeat state")
        return None

def toggleRepeat():
    if getCurrentPlayingType() == "track":
        state = getRepeatState()
        params = {
            'state': 'off'
        }
        
        if state == "off":
            params['state'] = 'context'
            response = requests.put(url="https://api.spotify.com/v1/me/player/repeat", params=params, headers=header)
            if response.status_code == 401:
                auth.getNewtokens()
                toggleRepeat()
            elif response.status_code == 204:
                print("Turning on normal repeat mode")
        elif state == "context":
            params['state'] = 'track'
            response = requests.put(url="https://api.spotify.com/v1/me/player/repeat", params=params, headers=header)
            if response.status_code == 401:
                auth.getNewtokens()
                toggleRepeat()
            elif response.status_code == 204:
                print("Turning on repeat song mode")
        elif state == "track":
            params['state'] = 'off'
            response = requests.put(url="https://api.spotify.com/v1/me/player/repeat", params=params, headers=header)
            if response.status_code == 401:
                auth.getNewtokens()
                toggleRepeat()
            elif response.status_code == 204:
                print("Turning off repeat mode")
    else:
        print("Cant repeat current track/podcast episode.")

