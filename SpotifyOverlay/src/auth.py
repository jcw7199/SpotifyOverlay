import json
import time
import pycurl
from io import BytesIO
import base64
import os
import random
import base64
import hashlib
import webbrowser
import requests
import urllib.parse
import server
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import *

buffer = BytesIO()
c = pycurl.Curl()

###auth, print function names that call refresh token.

clientId = "b7c8bd0c72dc41afa22f2749bfb9ceef"
redirectUri = 'https://jcw7199.pythonanywhere.com/storeAuthCode'
scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing user-library-modify user-library-read"
authUrl = "https://accounts.spotify.com/authorize"
tokenUrl = "https://accounts.spotify.com/api/token"
apiBaseUrl ="https://api.spotify.com/v1/"

INVALID_CODE_ERROR_MSG = 'Invalid authorization code'


auth_token = None
refresh_token = None
verifier = None
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
    global authUrl, auth_token
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

    #open window asking for user authentication.
    webbrowser.open_new(auth_request_url)


    #request auth code from my website
    getToken_url = "https://jcw7199.pythonanywhere.com/getAuthCode"
    
    try:
        response = requests.get(getToken_url)
    except requests.exceptions.ConnectionError:

        msg = QMessageBox()

        #add flag so that window pops up
        flags = Qt.WindowFlags(Qt.WindowStaysOnTopHint)
        msg.setWindowTitle("Error: Connection Error")
        msg.setText("Please connect to the internet and try again.")
        msg.setWindowFlags(flags)
        msg.show()
        flags = msg.windowFlags() 
        
        #remove flag after initial pop up.
        flags &= ~Qt.WindowStaysOnTopHint
        msg.setWindowFlags(flags)

        msg.exec_()
        return exit(1)

    if response.status_code >= 400 or response.status_code == None:
        msg = QMessageBox()

        #add flag so that window pops up
        flags = Qt.WindowFlags(Qt.WindowStaysOnTopHint)
        msg.setWindowTitle(f"Error: {response.status_code} Connection Error")
        msg.setText("Trouble connecting to server.\nIf issue persists, try updating the app to the latest version at github.com/jcw7199/SpotifyOverlay")
        msg.setWindowFlags(flags)
        msg.show()
        flags = msg.windowFlags() 
        
        #remove flag after initial pop up.
        flags &= ~Qt.WindowStaysOnTopHint
        msg.setWindowFlags(flags)

        msg.exec_()
        return exit(1)


    code = None
    attempts = 0
    failures = 0
    while(code == None or attempts < 100):
        print("STATUS: ", response.status_code)
        time.sleep(2)
        if response.status_code == 200:
            data = dict(json.loads(response.content.decode('utf-8')))
            print("AUTH DATA", data)
            if data != None:
                code = data.get('code')
                print("AUTH CODE", code)

                if code != None:
                    auth_token = getTokens(code)
                    print("AUTH TOKENS: ", auth_token)
                    if auth_token != False:
                        return auth_token
                    elif auth_token == False:
                        failures += 1

                        if failures % 10 == 0:
                            msg = QMessageBox()

                            #add flag so that window pops up
                            flags = Qt.WindowFlags(Qt.WindowStaysOnTopHint)
                            msg.setWindowTitle("Error: Spotify Overlay Error")
                            msg.setText("Trouble connecting to account, please authenticate again or close this window to quit the application.")
                            msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Close)
                            msg.setWindowFlags(flags)
                            msg.show()
                            flags = msg.windowFlags() 
                            
                            #remove flag after initial pop up.
                            flags &= ~Qt.WindowStaysOnTopHint
                            msg.setWindowFlags(flags)

                            #get popup result.
                            result = msg.exec_()
                            if result == QMessageBox.Retry:
                                webbrowser.open_new(auth_request_url)
                            else:
                                return exit(1)
        attempts += 1
        response = requests.get(getToken_url)

    if attempts == 100:
        return exit(1)

    print("RETURNING CODE: ", code)
    return code

def getTokens(auth_code):
    global auth_token, refresh_token
    
    buffer = BytesIO()
    c = pycurl.Curl()
    print("----------------GETTING TOKEN WITH CODE: ", auth_code, "--------------------")
    if(auth_code == 'access_denied'):
        return exit(1)


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
    print("TOKENS: ", dict(tokens))

    wrong_code_error = dict(tokens).get('error') == 'invalid_grant'

    if (wrong_code_error == True):
        print("INVALID CODE")
        return False
    

    try:
        auth_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
    except KeyError:
        print("getTokens - key error")
        
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
            print("getNewTokens - key error")
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
        return getAuthCode()
   elif auth_token == False:
      quit()
   else:
      return auth_token