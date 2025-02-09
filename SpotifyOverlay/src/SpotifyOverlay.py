import threading
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget
import time
import getSpotify
import psutil
#pyqt.configure(text=text)

app = QApplication([])

running = True
threads = []
msPerHour = 3600000
msPerMinute = 60000
msPerSecond = 1000


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
           
class Button(QPushButton):
    
    def __init__(self, text, function, parent = None):
        QPushButton.__init__(self)
        self.setText(text)
        self.function = function
        if self.function != None:
            self.clicked.connect(function)
            self.setParent(parent)

    def setFunction(self, function):
        self.function = function
        
        if self.function != None:
            self.clicked.connect(function)



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

        updateBarValueTh = threading.Thread(target=lambda: (seekToPosition(event.pos().x()/(self.width() - text_width + 3))))
        #updateBarValueTh.int_signal.connect(self.setValue)
        updateBarValueTh.start()       
        

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


class LabelThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        while running == True:
            data = self.func()

            self.signal.emit(data)


class ButtonLabelThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        while running == True:
            data = self.func()

            self.signal.emit(data)


class ButtonThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, clickFunction):
        super().__init__()
        self.clickFunction = clickFunction

    def run(self):
        data = self.clickFunction()

        if type(data) is str:
            self.signal.emit(data)

class BarThread(QThread):
    int_signal = pyqtSignal(int)
    str_signal = pyqtSignal(str)

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        while running == True:
            data = self.func()

            if type(data) is int:
                self.int_signal.emit(data)
            elif type(data) is str:
                self.str_signal.emit(data)
 
class SingleRunWorkerThread(QThread):
    int_signal = pyqtSignal(int)
    str_signal = pyqtSignal(str)

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        data = self.func()

        self.signal.emit(data)

class Window(QMainWindow):
    mysignal = pyqtSignal(str)

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
        
        #labels
        self.currentSong = Labels("Current Song", Qt.AlignmentFlag.AlignCenter, self.myWidget)
        self.currentDevice = Labels("Playing on...",  Qt.AlignmentFlag.AlignCenter, self.myWidget)
        
        #dynamic value buttons
        self.likeButton = Button("Like",lambda: self.dynamicBtnWork(toggleLike, self.likeButton.setText), self.myWidget)
        self.pauseButton = Button("Pause", lambda: self.dynamicBtnWork(togglePlayback, self.pauseButton.setText), self.myWidget)
        self.shuffleButton = Button("Shuffle", lambda: self.dynamicBtnWork(toggleShuffle, self.shuffleButton.setText), self.myWidget)
        self.repeatButton = Button("Repeat", lambda: self.dynamicBtnWork(toggleRepeat, self.repeatButton.setText), self.myWidget)


        #static value buttons.
        self.restartButton = Button("Restart", lambda: self.staticBtnWork(getSpotify.restartSong, self.restartButton), self.myWidget)
        self.volumePlusButton = Button("Vol +", lambda: self.staticBtnWork( lambda: (changeVolume('up')), self.volumePlusButton), self.myWidget)
        self.volumeMinusButton = Button("Vol -", lambda: self.staticBtnWork( lambda: (changeVolume('down')), self.volumeMinusButton), self.myWidget)


        self.previousButton = Button("<<", lambda: self.staticBtnWork(getSpotify.previousPlayback, self.previousButton), self.myWidget)
        
        
        self.nextButton = Button(">>", lambda: self.staticBtnWork(getSpotify.nextPlayback, self.nextButton), self.myWidget)
        
        
        

        self.minimzeButton = Button("-", self.minimizeWindow, self.myWidget)
        self.quitButton = Button("X", self.closeWindow, self.myWidget)
        
        self.progressbar = Bar(parent=self.myWidget)

        #color label and buttons
        buttonList = [self.likeButton, self.restartButton, self.volumeMinusButton, self.volumePlusButton, 
                      self.previousButton, self.pauseButton, self.nextButton, self.shuffleButton, self.repeatButton,
                      self.minimzeButton]

        for btn in buttonList:
            Button.colorButton(btn, "#06F00F", "black")

        Button.colorButton(self.quitButton, "#D80A22", "white")

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

    def initThreads(self):
        
        self.updateSongTh = LabelThread(updateSongLabelText)
        self.updateSongTh.signal.connect(self.currentSong.setText)
        self.updateSongTh.start()

        self.updateDevTh = LabelThread(updateDeviceLabelText)
        self.updateDevTh.signal.connect(self.currentDevice.setText)
        self.updateDevTh.start()
        
        self.updateSongProgTh = BarThread(updateSongProgress)
        self.updateSongProgTh.int_signal.connect(self.progressbar.setValue)
        self.updateSongProgTh.start()

        self.updateSongTimeTh = BarThread(lambda: updateSongTime(self.progressbar))
        self.updateSongTimeTh.str_signal.connect(self.progressbar.setFormat)
        self.updateSongTimeTh.start()

        self.updateLikeButtonTh = ButtonLabelThread(updateLikeButtonText)
        self.updateLikeButtonTh.signal.connect(self.likeButton.setText)
        self.updateLikeButtonTh.start()

        self.updatePauseButtonTh = ButtonLabelThread(updatePauseButtonText)
        self.updatePauseButtonTh.signal.connect(self.pauseButton.setText)
        self.updatePauseButtonTh.start()

        self.updateShuffleButtonTh = ButtonLabelThread(updateShuffleButtonText)
        self.updateShuffleButtonTh.signal.connect(self.shuffleButton.setText)
        self.updateShuffleButtonTh.start()

        self.updateRepeatButtonTh = ButtonLabelThread(updateRepeatButtonText)
        self.updateRepeatButtonTh.signal.connect(self.repeatButton.setText)
        self.updateRepeatButtonTh.start()

    def dynamicBtnWork(self, btnclickFunction, btntextfunction):
        self.worker = ButtonThread(btnclickFunction)
        self.worker.signal.connect(btntextfunction)
        
        self.worker.start()
        
    def staticBtnWork(self, btnclickFunction, widget):
        self.worker = ButtonThread(btnclickFunction)
        self.worker.start()

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
    t = None
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
    
    if (seconds < 10):
        seconds = "0" + str(seconds)

    
    if (milliseconds > msPerHour and minutes < 10):
        minutes = "0" + str(minutes)

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
    duration = getSpotify.getProgressAndDuration()[1]

    newPosition = int(position * duration);

    getSpotify.seekToPosition(newPosition)   

def updateSongLabelText():
    time.sleep(3)
    
    songInfo = list(getSpotify.getCurrentSongAndArtist())

    if len(songInfo) == 2:
        song = songInfo[0]
        artist = songInfo[1]
    
        txt = ""


        if song != None:
            if len(song) > 50:
                song = song[0:50] + "..."
            
        if artist != None:
            if len(artist) > 50:
                artist = artist[0:50] + "..."
        else:
            return "Can't get current song or no song is currently playing"

        txt = song + " - " + artist

        return txt
    else:
        return "Error: Can't get current song or no song is currently playing"

def updateDeviceLabelText(): 
    time.sleep(5)
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
            return name
        else:
            return "Can't get current device"
    else:
        return "Can't get current device"

def updateSongProgress():
    time.sleep(1)
    progress = list(getSpotify.getProgressAndDuration())
    duration = None
    #print(progress)
    
    if(len(progress) == 2):
        duration = progress[1]
        progress = progress[0]
            
        #print("P: ", progress, " D: ", duration)   
        if (progress != None and duration != None):
            
            return (int(round((progress/duration) * 100)))
    else:
        print("ERROR - PROG: ", progress)
        return 0

def updateSongTime(bar):
    time.sleep(.5)
    progress = list(getSpotify.getProgressAndDuration())
    duration = None
    #print(progress)
    formattedTime = "0:00"

    if(len(progress) == 2):
        duration = progress[1]
        progress = progress[0]
            
        #print("P: ", progress, " D: ", duration)   
        if (progress != None and duration != None):
            if (duration > msPerHour and progress < msPerHour):
                formattedTime = " 00:"
                if (progress < msPerMinute * 10):
                    formattedTime += " 0"
                
                formattedTime += formatTime(progress) + " / " + formatTime(duration)

            else:
                formattedTime = formatTime(progress) + " / " + formatTime(duration)

            return formattedTime
    else:
        print("ERROR - PROG: ", progress)
        return formattedTime

def updatePauseButtonText():
    time.sleep(2)
    is_playing = getSpotify.getPlaybackState()
    if is_playing == True:
        return "Pause"
    else:
        return "Play"
    
def updateLikeButtonText():
    time.sleep(2)
    state =  getSpotify.getSongLikedState() 

    if state == True:
        return "Unlike"
    elif state == False:
        return "Like"
    else:
        return "Can't Like"


def updateShuffleButtonText():
    time.sleep(2)
    state = getSpotify.getShuffleState()

    if state  == "Shuffled" or state == "Smart Shuffled":
        return "Unshuffle"
    elif state == "Unshuffled":
        return "Shuffle"
    else:
        return "Can't Shuffle"
    

def updateRepeatButtonText():
    time.sleep(2)
    state = getSpotify.getRepeatState()

    if state == "off":
        return "Repeat On"
    elif state == "context":
        return "Repeat 1"
    elif state == "track":
        return "Repeat Off"
    else:
        return "Can't Repeat"

def toggleLike():
    getSpotify.toggleLikeSong()
    state = getSpotify.getSongLikedState()

    if state == True:
        return "Unlike"
    else:
        return "Like"

def toggleRestart():
    getSpotify.restartSong()
    return "Restart"

def togglePlayback():
    getSpotify.togglePlayback()
    state = getSpotify.getPlaybackState()
    if state == True:
        return "Pause"
    else:
        return "Play"

def toggleShuffle():
    getSpotify.toggleShuffle()

def toggleRepeat():

    getSpotify.toggleRepeat()

    state = getSpotify.getRepeatState()

    if state == "off":
        return "Repeat On"
    elif state == "context":
        return "Repeat 1"
    elif state == "track":
        return "Repeat Off"
    else:
        return "Can't Repeat"
    

def startSpotify():
    restart = getSpotify.getActiveDevice()
    startAttempts = 0
    if restart[0] != None:
        ("starting spotify... ", restart)
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
            startAttempts += 1
            time.sleep(3)
            if startAttempts > 100:
                msg = QMessageBox()
                flags = Qt.WindowFlags(Qt.WindowStaysOnTopHint)
                msg.setText("No device found, closing overlay.")
                msg.setWindowFlags(flags)
                msg.show()
                msg.exec_()
                return False

        startSpotify()



def checkIfAppIsRunning():

    processes =  []

    for p in psutil.process_iter():
        try:
            if("python.exe" in p.name().lower()):
                if('SpotifyOverlay.py' in p.cmdline()):
                    processes.append(p)
        except Exception as e:
            print("Error: ", e)


    if len(processes) > 1:
        p = psutil.Process()
        for child in p.children():
            p.kill()
        p.kill()
        exit(0)
    '''
    processes =  [p in psutil.process_iter() if p.name().lower() in ['python.exe']]
    
    #the number of times the script appears in the processes list.
    scriptIterations = 0
    print(processes)

    #list of processes that correspond to the script
    proc_list = []
    for p_list in processes:
        for p in p_list:
            print("App running: ", p)
            if p == 'SpotifyOverlay.py':
                proc_list.append(p)

    while len(proc_list) > 1:
        p = proc_list.pop()
        p.kill()

    if scriptIterations > 1:
        print("App is already running")
        time.sleep(3)
        exit(0)
    '''

def main():
    global threads
    checkIfAppIsRunning()

    flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

    myWindow = Window(flags)
    myWindow.setGeometry(500, 500, 50, 30)
    
    start = startSpotify()
    if start == False:
        print("closing application")
        exit(1)


    myWindow.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    myWindow.show()

    myWindow.initThreads()
    #myWindow.start_work()
        
    '''
    myWindow.start_work(myWindow.progressbar, int, updateSongProgress)

    myWindow.start_work(myWindow.progressbar, str, updateSongTime)

    myWindow.start_work(myWindow.currentSong, str, updateSongLabelText)

    myWindow.start_work(myWindow.currentDevice, str, updateDeviceLabelText)
    '''

    '''
    
    
  
    threads.append(updateLikeTh)
    threads.append(updatePauseTh)
    threads.append(updateShuffleTh)
    threads.append(updateRepeatTh)
    threads.append(refreshTokenTh)
    '''''''''
    app.exec_()

if __name__ == '__main__':
    main()