import socket
import time
import urllib.request
import webbrowser

HEADER = 64
PORT = 4070
HOST ="127.0.0.1"
ADDR = (HOST, PORT)
auth_code = ""

def get_auth_code():
    #print("starting server")
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(ADDR)
    serv.listen(5)
    #print("server listening")
    serv.settimeout(15)
    while True:
        communication_socket, address = serv.accept()
        #print("connected to ", address )
        message = communication_socket.recv(1024).decode('utf-8')
        #print("Message: ", message)
        auth_code = message.split("code=")[1]
        auth_code = auth_code.split(' ')[0]
        reply = "<html><script> window.close() </script></html>"

        #print("---------SENDING-------")
        response = 'HTTP/1.1 200 OK\nConnection: close\n\n' + reply
        
        
        communication_socket.send(response.encode('utf-8'))
        #print("SENT--------------")
        time.sleep(2)
        communication_socket.close()
        #print("Connection ended", address)
        serv.settimeout(1)
        serv.close()
        return auth_code
