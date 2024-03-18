import threading
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget
import time
import getSpotify


app = QApplication([])
window = QMainWindow()
centralWidget = QWidget()
layout = QGridLayout()
running = True
threads = []
offset = None

def closeWindow():
    global running
    running = False
    window.close()

def moveWindow_mousePress(self=QMainWindow, event=QMouseEvent):
    global offset
    if event.button() == Qt.LeftButton:
        offset = event.pos()
        #print(event.pos())

def moveWindow_mouseMove(self=QMainWindow, event=QMouseEvent):
    if offset != None:
        self.move(self.pos() - offset + event.pos())    

def moveWindow_mouseRelease(self=QMainWindow, event=QMouseEvent):
    global offset
    offset = None
    
QMainWindow.mouseReleaseEvent = moveWindow_mouseRelease
QMainWindow.mousePressEvent = moveWindow_mousePress
QMainWindow.mouseMoveEvent = moveWindow_mouseMove

def updateSongLabelText(label=QLabel):
    global running
    x = 0
    while running == True:
        time.sleep(3)
        text = getSpotify.getCurrentSongAndArtist()
        print(x , " = updating song", text)
        if text != None:
            if len(text) > 70:
                text = text[0:70] + "..."
            label.pyqtConfigure(text=text)
            x += 1
        else:
            label.pyqtConfigure(text="Can't get current song or no song is currently playing")

def updatePauseButtonText(button=QPushButton):
    global running
    x = 0
    while running == True:
        time.sleep(3)
        is_playing = getSpotify.getPlaybackState()
        print(x, " = updating pause ", is_playing)
        if is_playing == True:
            button.pyqtConfigure(text="Pause")
        else:
            button.pyqtConfigure(text="Play")
        
 
        x += 1

def updateLikeButtonText(button=QPushButton):
    global running
    x = 0
    while running == True:
        time.sleep(3)
        state =  getSpotify.getSongLikedState() 
        print(x, " = updating like ", state)
        if state == True:
            button.pyqtConfigure(text="Unlike")
        elif state == False:
            button.pyqtConfigure(text="Like")
        else:
            button.pyqtConfigure(text="Cant Like")

        x += 1

def updateShuffleButtonText(button=QPushButton):
    global running
    x = 0
    while running == True:
        time.sleep(3)
        state = getSpotify.getShuffleState()
        if state  == False:
            button.pyqtConfigure(text="Shuffle")
        elif state == True:
            button.pyqtConfigure(text="Unshuffle")
        else:
            button.pyqtConfigure(text="Can't shuffle")
        x += 1

def updateRepeatButtonText(button=QPushButton):
    global running
    x = 0
    while running == True:
        time.sleep(3)
        state = getSpotify.getRepeatState()
        print(x, " = updating repeat: ", state)

        if state == "off":
            button.pyqtConfigure(text="Repeat On")
        elif state == "context":
            button.pyqtConfigure(text="Repeat 1")
        elif state == "track":
            button.pyqtConfigure(text="Repeat Off")
        else:
            button.pyqtConfigure(text="Can't Repeat")
        x += 1

class Labels:
    currentSong = QLabel(centralWidget, text="Current Song")    
    
    def initLabels():
        Labels.currentSong.setAlignment(Qt.AlignCenter)
        layout.addWidget(Labels.currentSong, 0, 0, 1, 9)
        Labels.colorLabels(Labels.currentSong, "black", "#06F00F")

        
    def colorLabels(label=QLabel, background_color=str, textColor=str):
        style = "background-color : " + background_color  
        print(textColor)
        if textColor != str:
            style += str("; color: " + textColor)
          
        label.setStyleSheet(style)
           
class Buttons:
    
    likeButton = QPushButton("Like", centralWidget)

    volumeMinusButton = QPushButton("Vol-", centralWidget)
    
    volumePlusButton = QPushButton("Vol+", centralWidget)
    
    previousButton = QPushButton("<<", centralWidget)
    
    pauseButton = QPushButton("Play", centralWidget)

    nextButton = QPushButton(">>", centralWidget)

    shuffleButton = QPushButton("Shuffle", centralWidget)

    repeatButton = QPushButton("Repeat", centralWidget)
    
    quitButton = QPushButton("Quit", centralWidget)

    def initButtons():
        layout.addWidget(Buttons.likeButton, 2, 0)
        Buttons.likeButton.clicked.connect(getSpotify.toggleLikeSong)

        layout.addWidget(Buttons.volumeMinusButton, 2, 1)
        Buttons.volumeMinusButton.clicked.connect(getSpotify.volumeDown)

        layout.addWidget(Buttons.volumePlusButton, 2, 2)
        Buttons.volumePlusButton.clicked.connect(getSpotify.volumeUp)

        layout.addWidget(Buttons.previousButton, 2, 3)
        Buttons.previousButton.clicked.connect(getSpotify.previousPlayback)

        layout.addWidget(Buttons.pauseButton, 2, 4)
        Buttons.pauseButton.clicked.connect(getSpotify.togglePlayback)

        layout.addWidget(Buttons.nextButton, 2, 5)
        Buttons.nextButton.clicked.connect(getSpotify.nextPlayback)

        layout.addWidget(Buttons.shuffleButton, 2, 6)
        Buttons.shuffleButton.clicked.connect(getSpotify.toggleShuffle)

        layout.addWidget(Buttons.repeatButton, 2, 7)
        Buttons.repeatButton.clicked.connect(getSpotify.toggleRepeat)

        layout.addWidget(Buttons.quitButton, 2, 8)
        Buttons.quitButton.clicked.connect(closeWindow)

        buttonList = [Buttons.likeButton, Buttons.volumeMinusButton, Buttons.volumePlusButton, Buttons.previousButton, 
                      Buttons.pauseButton, Buttons.nextButton, Buttons.shuffleButton, Buttons.repeatButton]

        for btn in buttonList:
            Buttons.colorButtons(btn, "#06F00F", "black")

        Buttons.colorButtons(Buttons.quitButton, "#D80A22", "white" )

    def colorButtons(button=QPushButton, background_color=str, textColor=str):
        style = "background-color : " + background_color  
        print(textColor)
        if textColor != str:
            style += str("; color: " + textColor)
          
        button.setStyleSheet(style)  

def startSpotify():
    restart = getSpotify.getActiveDevice()
    
    if restart[1] != True:
        if restart[0] != None:
            print("starting spotify... ", restart)
            if restart[1] == True:
                getSpotify.startPlayback()
            else:
                getSpotify.restartDevice()
        else:
            #wait for a device.
            #popup sayinng to start spotify 
            print("Message")
            msg = QMessageBox()
            flags = Qt.WindowFlags(Qt.WindowStaysOnTopHint)
            msg.setText("No device found, please start spotify")
            msg.setWindowFlags(flags)
            #msg.show()
            msg.exec_()
            while getSpotify.getActiveDevice()[0] == None:
                print("waiting for spotify to start...")
        
            startSpotify()


def main():
    global threads, loop
    window.setCentralWidget(centralWidget)
    window.setGeometry(500 , 500, 50, 30)
    centralWidget.setLayout(layout)
   
    flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    window.setWindowFlags(flags)
    window.setWindowOpacity(0.7)
    window.setStyleSheet("background-color: black")
    

    Labels.initLabels()
    Buttons.initButtons()
    startSpotify()

    window.show()
    #PAUSE threadds if device goes inactive
    #toss updates into event loop that resets labels at the beginning of every song. i.e, update like button at the start of the next song
    updateSongTh = threading.Thread(target=updateSongLabelText, kwargs={'label': Labels.currentSong})
    updateSongTh.daemon = True
    updateSongTh.start()

    updatePauseTh = threading.Thread(target=updatePauseButtonText, kwargs={'button': Buttons.pauseButton})
    updatePauseTh.daemon = True
    updatePauseTh.start()
    
    updateLikeTh = threading.Thread(target=updateLikeButtonText, kwargs={'button': Buttons.likeButton})
    updateLikeTh.daemon = True
    updateLikeTh.start()

    updateShuffleTh = threading.Thread(target=updateShuffleButtonText, kwargs={'button': Buttons.shuffleButton})
    updateShuffleTh.daemon = True
    updateShuffleTh.start()

    updateRepeatTh = threading.Thread(target=updateRepeatButtonText, kwargs={'button': Buttons.repeatButton})
    updateRepeatTh.daemon = True
    updateRepeatTh.start()

    refreshTokenTh = threading.Thread(target=getSpotify.refreshTokens)
    refreshTokenTh.daemon = True
    refreshTokenTh.start()

    app.exec_()

if __name__ == '__main__':
    main()