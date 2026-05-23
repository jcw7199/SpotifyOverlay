import socket
import time
import urllib.request
import webbrowser

HEADER = 64
PORT = 50000
HOST ="127.0.0.1"
ADDR = (HOST, PORT)

class Server():
    auth_code = ""
    timeOutStatus = False
    serv = socket.socket()

def startServer():
    #print("starting server")
    Server.timeOutStatus = False
    Server.serv = socket.socket()
    Server.serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    Server.serv.bind(ADDR)
    Server.serv.listen(2)
    Server.serv.settimeout(10)
    #print("server listening")

    try:
        communication_socket, address = Server.serv.accept()
        #print("connected to ", address )
        communication_socket.settimeout(10)
    
        #MAKE SURE MESSAGE IS FROM SPOTIFY
        message = communication_socket.recv(4096).decode('utf-8')
        #print("Message: ", message)
        code = None
        if "code" in message:
            code = message.split("code=")[1]
            code = code.split('&')[0]

        else:
            code = "declined"

        print("AUTH CODE: ", code)

        reply = "<script> window.close() </script>"
        #print("---------SENDING-------")
        response = 'HTTP/1.1 200 OK\nConnection: close\n\n' + reply
        communication_socket.send(response.encode('utf-8'))

        communication_socket.close()
        Server.serv.close()

        Server.auth_code = code
    except socket.timeout:
        print("Server timed out")
        Server.timeOutStatus = True

def closeServer():
    print("closing server")
    Server.serv.close()
