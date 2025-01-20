import threading
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget
import time
import getSpotify


app = QApplication([])

running = True
threads = []
offset = None





class Worker(QObject):
    finished = pyqtSignal(int)
    progress = pyqtSignal(int)


    def __init__(self, target_function):
        super().__init__()
        self.target_function = target_function

    def run(self):
        # Call the target function when the thread starts
        self.target_function()

class Labels(QLabel):   
    
    def __init__(self, text, alignment, parent=None):
        QLabel.__init__(self)
        self.setText(text)
        self.setAlignment(Qt.AlignCenter)
        self.setParent(parent)
    


    def colorLabel(label=QLabel, background_color=str, textColor=str):
        style = "background-color : " + background_color  
        #print(textColor)
        if textColor != str:
            style += str("; color: " + textColor)
          
        label.setStyleSheet(style)
           
class Buttons(QPushButton):
    
    def __init__(self, text, function, parent = None):
        QPushButton.__init__(self)
        self.setText(text)
        self.clicked.connect(function)
        self.setParent(parent)

    def colorButton(button=QPushButton, background_color=str, textColor=str):
        style = "background-color : " + background_color  
        if textColor != str:
            style += str("; color: " + textColor)
          
        button.setStyleSheet(style) 

class Widget(QWidget):
    def __init__(self):
        super().__init__()   

        #self.

class Layout(QGridLayout):
    def __init__(self):
        super().__init__()

class Window(QMainWindow):

    def __init__(self, flags):
        super().__init__()

        self.setWindowFlags(flags)
        self.setWindowOpacity(0.7)
        self.setStyleSheet("background-color: black")
        self.initUI()

    def initUI(self):

        self.myWidget = Widget()
        self.myLayout = Layout()
        self.myWidget.setLayout(self.myLayout)

        self.setCentralWidget(self.myWidget)
        
        #initialize buttons and widgets
        self.currentSong = Labels("Current Song", Qt.AlignCenter, self.myWidget)

        self.likeButton = Buttons("Like", getSpotify.toggleLikeSong, self.myWidget)
        self.restartButton = Buttons("Restart", getSpotify.restartSong, self.myWidget)
        self.volumePlusButton = Buttons("Vol +", (lambda: changeVolume('up')), self.myWidget)
        self.volumeMinusButton = Buttons("Vol -", (lambda: changeVolume('down')), self.myWidget)
        self.previousButton = Buttons("<<", getSpotify.previousPlayback, self.myWidget)
        self.pauseButton = Buttons("Pause", getSpotify.togglePlayback, self.myWidget)
        self.nextButton = Buttons(">>", getSpotify.nextPlayback, self.myWidget)
        self.shuffleButton = Buttons("Shuffle", getSpotify.toggleShuffle, self.myWidget)
        self.repeatButton = Buttons("Repeat", getSpotify.toggleRepeat, self.myWidget)
        self.minimzeButton = Buttons("-", self.minimizeWindow, self.myWidget)
        self.quitButton = Buttons("X", self.closeWindow, self.myWidget)
        
        #color label and buttons
        buttonList = [self.likeButton, self.restartButton, self.volumeMinusButton, self.volumePlusButton, 
                      self.previousButton, self.pauseButton, self.nextButton, self.shuffleButton, self.repeatButton,
                      self.minimzeButton]

        for btn in buttonList:
            Buttons.colorButton(btn, "#06F00F", "black")

        Buttons.colorButton(self.quitButton, "#D80A22", "white")

        Labels.colorLabel(self.currentSong, "black", "#06F00F")
        
        #add widgets to layout
        self.myLayout.addWidget(self.currentSong, 0, 0, 1, 10)

        self.myLayout.addWidget(self.likeButton, 2, 0)
        self.myLayout.addWidget(self.restartButton, 2, 1)
        self.myLayout.addWidget(self.volumeMinusButton, 2, 2)
        self.myLayout.addWidget(self.volumePlusButton, 2, 3)
        self.myLayout.addWidget(self.previousButton, 2, 4)
        self.myLayout.addWidget(self.pauseButton, 2, 5)
        self.myLayout.addWidget(self.nextButton, 2, 6)
        self.myLayout.addWidget(self.shuffleButton, 2, 7)
        self.myLayout.addWidget(self.repeatButton, 2, 8)
        self.myLayout.addWidget(self.minimzeButton, 2, 9)
        self.myLayout.addWidget(self.quitButton, 2, 10)

    def mousePressEvent(self, event):
        global offset
        if event.button() == Qt.LeftButton:
            offset = event.pos()
    
    def mouseMoveEvent(self, event):
        if offset != None:
            self.move(self.pos() - offset + event.pos())    

    def mouseReleaseEvent(self, event):
        global offset
        offset = None
    
    def setGeometry(self, x, y, w, h):
        super().setGeometry(x, y, w, h)

    def minimizeWindow(self):
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.showNormal()
        self.showMinimized()

    def closeWindow(self):
        global running
        running = False
        getSpotify.pausePlayback()
        self.close()

def changeVolume(upOrDown):
    changeable = getSpotify.volumeChanageable()

    if changeable == False:
        print("Device does not support changing volume through this app.")
        msg = QMessageBox()
        flags = Qt.WindowFlags(Qt.WindowStaysOnTopHint)
        msg.setWindowTitle("Error: Volume cant be changed")
        msg.setText("Device does not support changing volume through this app. Devices such as smartphones " +
                    "usually dont allow for volume changes.")
        msg.setWindowFlags(flags)
        msg.show()
        msg.exec_()
    else:
        if upOrDown == 'up':
            getSpotify.volumeUp()
        else:
            getSpotify.volumeDown()


def updateSongLabelText(label=QLabel):
    global running
    x = 0
    while running == True:
        time.sleep(3)
        text = getSpotify.getCurrentSongAndArtist()
        #print(x , " = updating song", text)
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
        #print(x, " = updating pause ", is_playing)
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
        #print(x, " = updating like ", state)
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
        #print(x, " = updating repeat: ", state)

        if state == "off":
            button.pyqtConfigure(text="Repeat On")
        elif state == "context":
            button.pyqtConfigure(text="Repeat 1")
        elif state == "track":
            button.pyqtConfigure(text="Repeat Off")
        else:
            button.pyqtConfigure(text="Can't Repeat")
        x += 1

def startSpotify():
    restart = getSpotify.getActiveDevice()
    #print(restart)

    if restart[0] != None:
        #("starting spotify... ", restart)
        if restart[1] == True:
            getSpotify.startPlayback()
        else:
            getSpotify.restartDevice()
    else:
        #wait for a device.
        #popup saying to start spotify 
        print("No device found")
        msg = QMessageBox()
        flags = Qt.WindowFlags(Qt.WindowStaysOnTopHint)
        msg.setText("No device found, please start spotify on one of your devices")
        msg.setWindowFlags(flags)
        msg.show()
        msg.exec_()
        while getSpotify.getActiveDevice()[0] == None:
            print("waiting for spotify to start...")
    
        startSpotify()

def main():
    global threads
    
    flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

    myWindow = Window(flags)
    myWindow.setGeometry(500, 500, 50, 30)


    startSpotify()

    myWindow.show()

    #updateSongTh = Worker(updateSongLabelText)
    #updateSongTh.start()
    #threads.append(updateSongTh)

    updateSongTh = threading.Thread(target=updateSongLabelText, kwargs={'label': myWindow.currentSong})
    updateSongTh.daemon = True
    updateSongTh.start()

    
    updatePauseTh = threading.Thread(target=updatePauseButtonText, kwargs={'button': myWindow.pauseButton})
    updatePauseTh.daemon = True
    updatePauseTh.start()
    
    updateLikeTh = threading.Thread(target=updateLikeButtonText, kwargs={'button': myWindow.likeButton})
    updateLikeTh.daemon = True
    updateLikeTh.start()

    updateShuffleTh = threading.Thread(target=updateShuffleButtonText, kwargs={'button': myWindow.shuffleButton})
    updateShuffleTh.daemon = True
    updateShuffleTh.start()

    updateRepeatTh = threading.Thread(target=updateRepeatButtonText, kwargs={'button': myWindow.repeatButton})
    updateRepeatTh.daemon = True
    updateRepeatTh.start()

    refreshTokenTh = threading.Thread(target=getSpotify.refreshTokens)
    refreshTokenTh.daemon = True
    refreshTokenTh.start()
    '''
    threads.append(updateLikeTh)
    threads.append(updatePauseTh)
    threads.append(updateShuffleTh)
    threads.append(updateSongTh)
    threads.append(updateRepeatTh)
    threads.append(refreshTokenTh)
    '''
    app.exec_()

if __name__ == '__main__':
    main()