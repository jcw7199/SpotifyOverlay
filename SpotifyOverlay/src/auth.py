import asyncio
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
from PyQt6 import QtCore
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import *
import string
import secrets

buffer = BytesIO()
c = pycurl.Curl()

###auth, print function names that call refresh token.

clientId = "b7c8bd0c72dc41afa22f2749bfb9ceef"
redirectUri = 'https://jordancw.pythonanywhere.com/storeAuthCode'
scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing user-library-modify user-library-read"
authUrl = "https://accounts.spotify.com/authorize"
tokenUrl = "https://accounts.spotify.com/api/token"
apiBaseUrl ="https://api.spotify.com/v1/"
codeUrl = "https://jordancw.pythonanywhere.com/getAuthCode"


INVALID_CODE_ERROR_MSG = 'Invalid authorization code'

class Auth():
    auth_token = None
    refresh_token = None
    verifier = []
    refreshing = None
    token_error = None

def getCodeVerifier():
    
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(possible[secrets.randbelow(len(possible))] for _ in range(64))



def getCodeChallenge():
    Auth.verifier = getCodeVerifier()

    code_challenge_digest = hashlib.sha256(str(Auth.verifier).encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge_digest).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')

    #print("CODE CHALLENGE", code_challenge)
    return code_challenge

def getAuthCode():
    state = ''.join(getCodeVerifier())

    authCodeParams =  {
      'response_type': 'code',
      'client_id': clientId,
      'scope': scope,
      'code_challenge_method': 'S256',
      'code_challenge': getCodeChallenge(),
      'redirect_uri': redirectUri,
      'show_dialog': True,
      'state': state #use random string for state
    }

    print("getting auth code")
    #url to make authorization request to spotify for token
    auth_request_url = f"{authUrl}?{urllib.parse.urlencode(authCodeParams)}"

    #open window asking for user authentication.
    webbrowser.open_new(auth_request_url)

    getCodeParams = {
        'state': state
    }
    #request auth code from my website
    getCode_url = f"{codeUrl}?{urllib.parse.urlencode(getCodeParams)}"
    
    print(getCode_url)

    try:
        response = requests.get(getCode_url)

        print("Response: ", response.content.decode('utf-8'))

        if response.status_code >= 400 or response.status_code == None:
            msg = QMessageBox()
            #display connection error due to server message

            #add flag so that window pops up
            flags = QtCore.Qt.WindowType.WindowStaysOnTopHint
            msg.setWindowTitle(f"Error: {response.status_code} Connection Error")
            msg.setText("Trouble connecting to server.\nIf issue persists, try updating the app to the latest version at github.com/jcw7199/SpotifyOverlay")
            msg.setWindowFlags(flags)
            msg.show()
            flags = msg.windowFlags() 
            
            #remove flag after initial pop up.
            flags &= ~QtCore.Qt.WindowType.WindowStaysOnTopHint
            msg.setWindowFlags(flags)

            return exit(1)


        code = None
        attempts = 0
        failures = 0
        timeout = 0

        # try to get token 100 times, letting the user know, every 10th attempt, 
        # to try re authenticating or restart the app 
        while(code == None and attempts < 100 and timeout < 60):
            print("STATUS: ", response.status_code)
            time.sleep(2)
            if response.status_code == 200 and response.content:
                data = dict(json.loads(response.content.decode('utf-8')))
                print("AUTH DATA", data)
                if data != None:
                    code = data.get('code')
                    state = data.get('state')
                    print("AUTH CODE", code)

                    if code != None:
                        # 'state' variable is sent to redirect uri when user authenticates app.
                        # this will be compared against the state variable currently stored on my server.
                        # if they dont match, continue to query the server for 60 seconds for this to change, 
                        # checking the data once per second until they match.

                        # The idea is to make sure the user has actually interacted with browser tab that has been opened.
                        # If they haven't, the state wont match, even if their is an old code there.
                        # Once the user authenticates, the state on my server will update to match.
                        
                        if state != authCodeParams["state"]:

                            while state != authCodeParams["state"] and timeout < 60:
                                time.sleep(1)
                                print("Old state - current state: ", state)
                                try:
                                    response = requests.get(getCode_url)
                                    print("Response: ", response.content.decode('utf-8'))

                                    data = dict(json.loads(response.content.decode('utf-8')))
                                except requests.exceptions.ConnectionError:

                                    #display connection error message
                                    msg = QMessageBox()

                                    #add flag so that window pops up
                                    flags = QtCore.Qt.WindowType.WindowStaysOnTopHint
                                    msg.setWindowTitle("Error: Connection Error")
                                    msg.setText("Please connect to the internet and try again.")
                                    msg.setWindowFlags(flags)
                                    msg.show()
                                    flags = msg.windowFlags() 
                                    
                                    #remove flag after initial pop up.
                                    flags &= ~QtCore.Qt.WindowType.WindowStaysOnTopHint
                                    msg.setWindowFlags(flags)

                                    msg.exec_()
                                    return exit(1)
                            

                                code = data.get('code')
                                state = data.get('state')
                                print("AUTH CODE", code)
                                print("State: ", state)
                                timeout += 1
                            #web browser opens on every call of get tokens -- FIX
                        
                        tokens = generateTokens(code)
                        print("AUTH TOKENS: ", tokens)
                        
                        if tokens["error"] != None:
                            failures += 1
                                #every 10 failures, display error message to user
                            if failures % 10 == 0:
                                msg = QMessageBox()

                                #add flag so that window pops up
                                flags = QtCore.Qt.WindowType.WindowStaysOnTopHint
                                msg.setWindowTitle("Error: Spotify Overlay Error")
                                msg.setText("Trouble connecting to account, please authenticate again or close this window to quit the application.")
                                msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Close)
                                msg.setWindowState(flags)
                                msg.show()
                                flags = msg.windowState() 
                                
                                #remove flag after initial pop up.
                                flags &= ~QtCore.Qt.WindowType.WindowStaysOnTopHint
                                msg.setWindowFlags(flags)

                                #get popup result. if they closed the window instead of retrying, exit app.
                                result = msg.exec_()
                                if result == QMessageBox.Retry:
                                    webbrowser.open_new(auth_request_url)
                                else:
                                    return exit(1)
            attempts += 1
            response = requests.get(getCode_url)

        #after 100 attempts, exit the app.
        if attempts == 100:
            return exit(1)
        
         #return code
        print("RETURNING CODE: ", code)
    except requests.exceptions.ConnectionError:
        print("CONNECTION ERROR")
        #display connection error message
        msg = QMessageBox()

        #add flag so that window pops up
        flags = msg.windowFlags() & QtCore.Qt.WindowType.WindowStaysOnTopHint
        msg.setWindowTitle("Error: Connection Error")
        msg.setText("Please connect to the internet and try again.")
        msg.setWindowFlags(flags)
        msg.show() 
        flags = msg.windowFlags() 
        
        #remove flag after initial pop up.
        flags &= ~QtCore.Qt.WindowType.WindowStaysOnTopHint
        msg.setWindowFlags(flags)
        #return exit(1)
    


   

def generateTokens(auth_code):
    buffer = BytesIO()
    c = pycurl.Curl()
    print("----------------GETTING TOKEN WITH CODE: ", auth_code, "--------------------")

    #exit app if user denies access
    if(auth_code == 'access_denied'):
        print("User denied access. Exiting app...")
        return exit(1)


    tokenParams = {
      'grant_type': "authorization_code",
      'code': auth_code,
      'redirect_uri': redirectUri,
      'client_id': clientId,
      'code_verifier': Auth.verifier
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
        Auth.token_error = "token request exception"
        return {"token": None, "refresh": None,  "error": Auth.token_error}
     
   

    tokens = json.loads(buffer.getvalue().decode('utf-8'))
    print("TOKENS: ", dict(tokens))

#############
    wrong_code_error = dict(tokens).get('error') == 'invalid_grant'

    if (wrong_code_error == True):
        #print("INVALID CODE")
        Auth.token_error = "auth error, invalid grant"

        return {"token": None, "refresh": None, "error": Auth.token_error}
#############

    
    try:
        Auth.auth_token = tokens['access_token']
        Auth.refresh_token = tokens['refresh_token']
    except KeyError:
        print("generateTokens - key error")
        print(tokens)
        Auth.token_error = "key error"
        return {"token": None, "refresh": None, "error": Auth.token_error}
    
    #print("ACCESS TOKEN: ", tokens['access_token'])

    #print("REFRESH TOKEN: ", tokens['refresh_token'])
    
    Auth.token_error = None
    return {"token": Auth.auth_token, "refresh": Auth.refresh_token, "error": Auth.token_error}

async def getNewTokens():
   #get new token using refresh token

   lock = asyncio.Lock()
   
   async with lock:
       if Auth.refresh_token != None:
            buffer = BytesIO()
            c = pycurl.Curl()

            refreshTokenParams = {
                'grant_type': "refresh_token",
                'refresh_token': Auth.refresh_token,
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
                print("getNewTokens - auth exception, status code: ", status)
                return None


            tokens = json.loads(buffer.getvalue().decode('utf-8'))
            #print(tokens)


            try:
                Auth.auth_token = tokens['access_token']
                Auth.refresh_token = tokens['refresh_token']
            except KeyError:
                print("getNewTokens - key error")
                return None

            #print("ACCESS TOKEN: ", tokens['access_token'])

            #print("REFRESH TOKEN: ", tokens['refresh_token'])

            return Auth.auth_token
       else:
            print("get new auth and refresh token")
            code = getAuthCode()
            return Auth.auth_token
      
async def getAuthToken():
    lock = asyncio.Lock()

    async with lock:
        #print("get token!!!!!!")
        if Auth.auth_token == None: 
            getAuthCode()
        
        return Auth.auth_token
            
   
        