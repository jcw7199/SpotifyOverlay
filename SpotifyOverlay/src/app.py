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
msPerHour = 3600000
msPerMinute = 60000
msPerSecond = 1000



class WorkerThread(QThread):
    # Signal to update progress
    message_signal = pyqtSignal(str)
    def __init__(self, bar, parent = ...):
        super().__init__(parent)
        self.bar = bar


    def run(self):
        while True:
            updateSongProgress(bar=self.bar)  # To avoid flooding with too many "Hello"s
            self.message_signal.emit("Hello")


class Labels(QLabel):   
    
    def __init__(self, text, alignment, parent=None):
        QLabel.__init__(self)
        self.setText(text)
        self.setAlignment(alignment)
        self.setParent(parent)
    


    def colorLabel(label=QLabel, background_color=str, textColor=str):
        style = "background-color : " + background_color  

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

class Bar(QProgressBar):

    def __init__(self, parent = ...):
        super().__init__(parent)
        self.setRange(0, 100)
        

    def mouseReleaseEvent(self, event):
        self.position = event.pos()
        self.position

        text = self.text()
        font = self.font()
        metrics = QFontMetrics(font)
        text_width = metrics.width(text)

        #print(text_width)
        seekToPosition(event.pos().x()/(self.width() - text_width))

    def colorBar(bar=QProgressBar, background_color=str, textColor=str):
            style = "background-color : " + background_color  
            if textColor != str:
                style += str("; color: " + textColor)
            
            bar.setStyleSheet(style)

class Widget(QWidget):
    def __init__(self):
        super().__init__()   

        #self.

class Layout(QGridLayout):
    def __init__(self):
        super().__init__()

class WorkerThread(QThread):
    progress_updated = pyqtSignal(int)

    def __init__(self, bar):
        super().__init__()
        self.bar = bar

    def do_work(self):
        while running == True:
            prog = updateSongProgress(bar=self.bar)
            self.progress_updated.emit(prog)
            
    def run(self):
        """Override run method
        """
        self.do_work()
        

class Window(QMainWindow):

    def __init__(self, flags):
        super().__init__()

        self.setWindowFlags(flags)
        self.setWindowOpacity(0.7)
        self.setStyleSheet("background-color: black")
        self.offset = None
        self.initUI()   
    
    def initUI(self):

        self.myWidget = Widget()
        self.myLayout = Layout()
        self.myWidget.setLayout(self.myLayout)

        self.setCentralWidget(self.myWidget)
        
        #initialize buttons and widgets
        self.currentSong = Labels("Current Song", Qt.AlignmentFlag.AlignCenter, self.myWidget)
        self.currentDevice = Labels("Playing on...",  Qt.AlignmentFlag.AlignCenter, self.myWidget)

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
        
        self.progressbar = Bar(parent=self.myWidget)
        

        #color label and buttons
        buttonList = [self.likeButton, self.restartButton, self.volumeMinusButton, self.volumePlusButton, 
                      self.previousButton, self.pauseButton, self.nextButton, self.shuffleButton, self.repeatButton,
                      self.minimzeButton]

        for btn in buttonList:
            Buttons.colorButton(btn, "#06F00F", "black")

        Buttons.colorButton(self.quitButton, "#D80A22", "white")

        Labels.colorLabel(self.currentSong, "black", "#06F00F")
        Labels.colorLabel(self.currentDevice, "black", "#06F00F")
        
        Bar.colorBar(self.progressbar, "#D80A22", "white")
        #add widgets to layout
        self.myLayout.addWidget(self.currentSong, 0, 0, 1, 11)
        self.myLayout.addWidget(self.currentDevice, 0, 7, 1, 3)
        
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

        self.myLayout.addWidget(self.progressbar, 3, 0, 1, 11)

        self.progressbar.setRange(0, 100)
        self.progressbar.setValue(0)
        self.progressbar.setFormat("0:00")
        self.progressbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def start_work(self):
        self.thread = WorkerThread(self.progressbar)
        self.thread.progress_updated.connect(self.progressbar.setValue)
        self.thread.start()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            
    def mouseMoveEvent(self, event):
        if self.offset != None:
            self.move(self.pos() - self.offset + event.pos())    

    def mouseReleaseEvent(self, event):
        self.offset = None
    
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

def formatTime(milliseconds):

    
    seconds = 0
    minutes = 0
    hours = 0
    if (milliseconds > msPerHour):
    
        hours = milliseconds / msPerHour

        minutes = hours - int(hours)
        minutes *= 60

        seconds = minutes - int(minutes)
        seconds *= 60
        
        hours = int (hours)
        minutes = int (minutes)
        seconds = int (seconds)
    else:
        hours = 0
        if (milliseconds > msPerMinute):
            minutes = (milliseconds / 60000)
            seconds = minutes - int(minutes)
            seconds *= 60

            minutes = int(minutes)
            seconds = int(seconds)


        else:
            minutes = 0
            seconds = int(milliseconds/msPerSecond)

    #print("HOUR", hours, " Min", minutes, " SEC", seconds)
    
    
    if (seconds < 10):
        seconds = "0" + str(seconds)

    
    if (milliseconds > msPerHour and minutes < 10):
        minutes = "0" + str(minutes)
        print('MINUTES', minutes)


    if (milliseconds >= msPerHour):
        t = str(hours) + ":" + str(minutes) + ":" + str(seconds)
    else:
        t = str(minutes) + ":" + str(seconds)

    return t

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

def seekToPosition(position):
    duration = getSpotify.getProgress()[1]

    newPosition =int(position * duration);

    getSpotify.seekToPosition(newPosition)   

def updateSongLabelText(label=Labels):
    global running
    x = 0
    while running == True:
        time.sleep(3)
        song, artist = getSpotify.getCurrentSongAndArtist()
        
        txt = ""


        if song != None:
            if len(song) > 50:
                song = song[0:50] + "..."
            
        if artist != None:
            if len(artist) > 50:
                artist = artist[0:50] + "..."
        else:
            label.pyqtConfigure(text="Can't get current song or no song is currently playing")

        txt = song + " - " + artist

        label.pyqtConfigure(text=txt)

def updateDeviceLabelText(label=Labels):
    global running
    x = 0
    while running == True:
        time.sleep(3)
        device = getSpotify.getActiveDevice()
        #print(device)
        name = "Playing on "
        if device != None:
            devName = device[0]['name']

            if devName != None:
                if len(devName) > 10:
                    devName = devName[0:10] + "..."
                
                name += devName
                #print("NAME: " + name)
                label.pyqtConfigure(text=name)
            else:
                label.pyqtConfigure(text="Can't get current device")

def updateSongProgress(bar=Bar):
       
    progress, duration = getSpotify.getProgress()
    
    #print("P: ", progress, " D: ", duration)   
    if (progress != None and duration != None):
        if (duration > msPerHour and progress < msPerHour):
            formattedTime = " 00:"
            if (progress < msPerMinute * 10):
                formattedTime += " 0"
            
            formattedTime += formatTime(progress) + " / " + formatTime(duration)

        else:
            formattedTime = formatTime(progress) + " / " + formatTime(duration)

        bar.setFormat(formattedTime)
        
        if (bar.value() >= 100):
            return 0
        else:
            return (int(round((progress/duration) * 100)))


def updatePauseButtonText(button=Buttons):
    global running
    x = 0
    while running == True:
        time.sleep(3)
        is_playing = getSpotify.getPlaybackState()
        if is_playing == True:
            button.pyqtConfigure(text="Pause")
        else:
            button.pyqtConfigure(text="Play")
        
 
        x += 1

def updateLikeButtonText(button=Buttons):
    global running
    x = 0
    while running == True:
        time.sleep(3)
        state =  getSpotify.getSongLikedState() 
        if state == True:
            button.pyqtConfigure(text="Unlike")
        elif state == False:
            button.pyqtConfigure(text="Like")
        else:
            button.pyqtConfigure(text="Cant Like")

        x += 1

def updateShuffleButtonText(button=Buttons):
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

def updateRepeatButtonText(button=Buttons):
    global running
    x = 0
    while running == True:
        time.sleep(3)
        state = getSpotify.getRepeatState()

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

    myWindow.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    myWindow.show()
        
    myWindow.start_work()

    updateSongTh = threading.Thread(target=updateSongLabelText, kwargs={'label': myWindow.currentSong})
    updateSongTh.daemon = True
    updateSongTh.start()

    updateDeviceTh = threading.Thread(target=updateDeviceLabelText, kwargs={'label': myWindow.currentDevice})
    updateDeviceTh.daemon = True
    updateDeviceTh.start()

    #updateProgressTh = threading.Thread(target=updateSongProgress, kwargs={'bar': myWindow.progressbar})
    #updateProgressTh.daemon = True
    #updateProgressTh.start()


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