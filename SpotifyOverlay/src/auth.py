import json
import pycurl
from io import BytesIO

buffer = BytesIO()
c = pycurl.Curl()

import base64
import os
import random
import base64
import hashlib
import webbrowser
import requests
import urllib.parse
from threading import Thread
import server

###auth, print function names that call refresh token.

clientId = "b7c8bd0c72dc41afa22f2749bfb9ceef"
redirectUri = 'http://localhost:4070/callback'
scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing user-library-modify user-library-read"
authUrl = "https://accounts.spotify.com/authorize"
tokenUrl = "https://accounts.spotify.com/api/token"
apiBaseUrl ="https://api.spotify.com/v1/"

auth_token = None
refresh_token = None
verifier = None
auth_code = None
refreshing = False
def getCodeVerifier():
    global verifier
    length = random.randint(64, 64)
    rand_bytes = os.urandom(length)
    verifier =  base64.urlsafe_b64encode(rand_bytes).decode('utf-8').replace('=', '').replace('+', '-').replace('/', '_')
    #print("VERIFIER: ", verifier)
    return verifier

def getCodeChallenge():
    code_challenge_digest = hashlib.sha256(getCodeVerifier().encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge_digest).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')

    #print("CODE CHALLENGE", code_challenge)
    return code_challenge

def getAuthCode():
    global authUrl
    authCodeParams =  {
      'response_type': 'code',
      'client_id': clientId,
      'scope': scope,
      'code_challenge_method': 'S256',
      'code_challenge': getCodeChallenge(),
      'redirect_uri': redirectUri,
      'show_dialog': False
    }

    auth_request_url = f"{authUrl}?{urllib.parse.urlencode(authCodeParams)}&allow_redirects=False"
    
    #authRequestThread = Thread(target=lambda : webbrowser.open_new(auth_request_url))
    #authRequestThread.daemon = True
    #authRequestThread.start()
    #authRequestThread.join()
    
    
    webbrowser.open_new(auth_request_url)
    code = server.get_auth_code()
    return code

def getTokens():
    global auth_token, refresh_token, auth_code
  
    buffer = BytesIO()
    c = pycurl.Curl()
    auth_code = getAuthCode()

    if(auth_code == 'Declined'):
        return exit(0)


    tokenParams = {
      'grant_type': "authorization_code",
      'code': auth_code,
      'redirect_uri': redirectUri,
      'client_id': clientId,
      'code_verifier': verifier
    }

    tokenHeaders = ["Content-Type: application/x-www-form-urlencoded"]

    c.setopt(c.URL, tokenUrl)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POSTFIELDS, urllib.parse.urlencode(tokenParams))
    
    try:
        c.setopt(c.HTTPHEADER, tokenHeaders)
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()
    except pycurl.error:
        print("token request exception", pycurl.error)
        return None
     
    #print("TOKENS REQUEST STATUS: ", status)
    if status == 500:
        return None

    tokens = json.loads(buffer.getvalue().decode('utf-8'))
    #print(tokens)

    try:
        auth_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
    except KeyError:
        print("key error")
        return None
    
    #print("ACCESS TOKEN: ", tokens['access_token'])

    #print("REFRESH TOKEN: ", tokens['refresh_token'])

    return auth_token

def getNewTokens():
   global auth_token, refresh_token
   if refresh_token != None:
        #get new token using refresh token
    
        buffer = BytesIO()
        c = pycurl.Curl()

        refreshTokenParams = {
            'grant_type': "refresh_token",
            'refresh_token': refresh_token,
            'client_id': clientId,
        }

        tokenHeaders = ["Content-Type: application/x-www-form-urlencoded"]

        c.setopt(c.URL, tokenUrl)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.POSTFIELDS, urllib.parse.urlencode(refreshTokenParams))
        c.setopt(c.HTTPHEADER, tokenHeaders)
        try:
            c.perform()
            status = c.getinfo(c.RESPONSE_CODE)
            c.close()
        except pycurl.error:
            print("auth exception")
            return None
        print("TOKENS REQUEST STATUS: ", status)
        tokens = json.loads(buffer.getvalue().decode('utf-8'))
        #print(tokens)


        try:
            auth_token = tokens['access_token']
            refresh_token = tokens['refresh_token']
        except KeyError:
            print("key error")
            return None

        #print("ACCESS TOKEN: ", tokens['access_token'])

        #print("REFRESH TOKEN: ", tokens['refresh_token'])
  
        return auth_token
   else:
        print("get new auth and refresh token")
            #getTokens()
      
def getAuthToken():
   global auth_token
   if auth_token == None:
        return getTokens()
   elif auth_code == 'Declined':
      quit()
   else:
      return auth_token