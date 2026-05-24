import asyncio
import json
import socket
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
from PyQt6.QtWidgets import QMessageBox, QApplication, QMainWindow, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import *
import string
import secrets
import threading

buffer = BytesIO()
c = pycurl.Curl()


clientId = "b7c8bd0c72dc41afa22f2749bfb9ceef"
redirectUri = 'http://127.0.0.1:50000'
#redirectUri = 'https://jordancw.pythonanywhere.com/storeAuthCode'
scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing user-library-modify user-library-read user-follow-modify playlist-modify-public"
authUrl = "https://accounts.spotify.com/authorize"
tokenUrl = "https://accounts.spotify.com/api/token"
apiBaseUrl ="https://api.spotify.com/v1/"
codeUrl = "https://jordancw.pythonanywhere.com/getAuthCode"


INVALID_CODE_ERROR_MSG = 'Invalid authorization code'
ACCESS_DENIED_ERROR_MSG = 'access_denied'
class Auth():
    auth_token = None
    refresh_token = None
    verifier = []
    refreshing = None
    token_error = None
    window = None

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

async def getAuthCode():
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
    
    serverThread = threading.Thread(target=server.startServer)
    serverThread.start()
    
    await asyncio.sleep(3)
    #open window asking for user authentication.
    webbrowser.open_new(auth_request_url)
    
    while server.Server.auth_code == "" and server.Server.timeOutStatus == False:
        print("Code: ", server.Server.auth_code)
        await asyncio.sleep(3)
        
    
    server.closeServer()

    if server.Server.timeOutStatus == True:
        print("Server timed out")
        return await retryConnection()        
        

    if server.Server.auth_code != "":
        if server.Server.auth_code == 'declined':
            print("Declined")
            exit(1)
        else:
            #try to use auth code to get tokens.
            tokens = generateTokens(server.Server.auth_code)
            print("AUTH TOKENS: ", tokens["error"])
             
            if tokens["error"] != None:
                return await retryConnection()           

    return True


                
async def retryConnection():
    dlg = QMessageBox(Auth.window)
    dlg.setWindowTitle(f"Error: Account Connection Error")
    dlg.setText("Trouble connecting to account. Please authenticate again." + 
                "\n\nClick \"Retry\" to reauthenticate or close this window to quit the application.")
    dlg.setStandardButtons(
        QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Close
    )
    dlg.setDefaultButton(QMessageBox.StandardButton.Retry)
    dlg.setWindowFlags(
        dlg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
    )
    
    result = dlg.exec()
    if result == QMessageBox.StandardButton.Close:
        print("Closing")
        exit(1)
    else:
        print("Retrying")
        return await getAuthCode()




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
            await getAuthCode()
        
        return Auth.auth_token

async def initWindow(window):
    Auth.window = window
   
        