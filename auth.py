import base64
import os
import random
import base64
import hashlib
import webbrowser
import requests
import urllib.parse
from threading import Thread
import time
import server


clientId = "b7c8bd0c72dc41afa22f2749bfb9ceef"
redirectUri = 'http://localhost:8888/callback'
scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing user-library-modify user-library-read"
authUrl = "https://accounts.spotify.com/authorize"
tokenUrl = "https://accounts.spotify.com/api/token"
apiBaseUrl ="https://api.spotify.com/v1/"

auth_token = None
refresh_token = None
verifier = None

def getCodeVerifier():
  global verifier
  length = random.randint(64, 64)
  rand_bytes = os.urandom(length)
  verifier =  base64.urlsafe_b64encode(rand_bytes).decode('utf-8').replace('=', '').replace('+', '-').replace('/', '_')
  print("VERIFIER: ", verifier)
  return verifier

def getCodeChallenge():
  code_challenge_digest = hashlib.sha256(getCodeVerifier().encode('utf-8')).digest()
  code_challenge = base64.urlsafe_b64encode(code_challenge_digest).decode('utf-8')
  code_challenge = code_challenge.replace('=', '')

  print("CODE CHALLENGE", code_challenge)
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
  }

  auth_request_url = f"{authUrl}?{urllib.parse.urlencode(authCodeParams)}&allow_redirects=False"
  
  authRequestThread = Thread(target=lambda : webbrowser.open_new(auth_request_url))
  authRequestThread.daemon = True
  authRequestThread.start()
  authRequestThread.join()

  code = server.get_auth_code()
  return code

def getToken():
  global auth_token, refresh_token
  tokenParams = {
    'grant_type': "authorization_code",
    'code': getAuthCode(),
    'redirect_uri': redirectUri,
    'client_id': clientId,
    'code_verifier': verifier
  }

  tokenHeaders = {
    'Content-Type': 'application/x-www-form-urlencoded',
  }

  tokens = requests.post(url=tokenUrl, params=tokenParams, headers=tokenHeaders)
  print("TOKENS REQUEST STATUS: ", tokens.status_code)
  tokens = tokens.json()
  #print(tokens)


  auth_token = tokens['access_token']
  refresh_token = tokens['refresh_token']

  #print("ACCESS TOKEN: ", tokens['access_token'])

  #print("REFRESH TOKEN: ", tokens['refresh_token'])

  return auth_token

def getNewtokens():
  global auth_token, refresh_token
  print("TOKWNS AT BEHINGIG", refresh_token)
  if refresh_token != None:
    refreshParams = {
      'grant_type': 'refresh_token',
      'refresh_token': refresh_token,
      'client_id': clientId
    }

    refreshHeaders = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }

    tokens = requests.post(url=tokenUrl, params=refreshParams, headers=refreshHeaders)
    auth_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    print("PRINTING TOKENS JSON ", tokens)
    return auth_token
  else:
    print("Refresh Token Missing, getting new auth code and new token")
    return getToken()
  
def tokenRefresh():
  while True:
    print("refreshing token")
    getNewtokens()
