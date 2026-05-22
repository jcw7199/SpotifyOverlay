import os
import sys
import threading
import asyncio
from PyQt6 import QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QMessageBox
import qasync
from qasync import QEventLoop, asyncClose, asyncSlot

import time
import getSpotify
import psutil
#pyqt.configure(text=text)

msg = None
running = True
threads = []
msPerHour = 3600000
msPerMinute = 60000
msPerSecond = 1000


class Labels(QLabel):   
    
    def __init__(self, text, alignment, parent=None):
        super().__init__()
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
        super().__init__()
        self.setText(text)
        self.function = function
        if self.function != None:
            self.clicked.connect(lambda _: function())
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
        asyncio.ensure_future(seekToPosition(event.pos().x()/(self.width() - 3)))

        #updateBarValueTh.int_signal.connect(self.setValue)
        

    def colorBar(bar=QProgressBar, background_color=str, textColor=str):
            style = "background-color : " + background_color  
            if textColor != str:
                style += str("; color: " + textColor)
            
            bar.setStyleSheet(style)

class MsgBox(QMessageBox):
    def __init__(self, message, title, icon):
        super().__init__()

        self.setText(message)
        self.setWindowTitle(title)
        self.setIcon(icon)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

    def showMsg(self):
        self.show()
        self.raise_()
        self.activateWindow()
    
    def execMsg(self):
        self.exec()

    def closeEvent(self, event):
        print("Message box closed")
        event.accept()

class Widget(QWidget):
    def __init__(self):
        super().__init__()   

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
    
    @asyncClose
    async def closeEvent(self, event: QCloseEvent):
        """
        Use async code in a closeEvent by decorating it with @asyncClose.
        """
        pass

    def initUI(self):

        self.myWidget = Widget()
        self.myLayout = Layout()
        self.myWidget.setLayout(self.myLayout)

        self.setCentralWidget(self.myWidget)
        
        #labels
        self.currentSong = Labels("Current Song", Qt.AlignmentFlag.AlignCenter, self.myWidget)
        self.currentDevice = Labels("Playing on...",  Qt.AlignmentFlag.AlignCenter, self.myWidget)
        self.currentTime = Labels("0:00", Qt.AlignmentFlag.AlignCenter, self.myWidget)

        #dynamic value buttons
        self.likeButton = Button("Like", toggleLikeSlot, self.myWidget)
        self.pauseButton = Button("Pause", togglePlaybackSlot, self.myWidget)
        self.shuffleButton = Button("Shuffle", toggleShuffleSlot, self.myWidget)
        self.repeatButton = Button("Repeat", toggleRepeatSlot, self.myWidget)


        #static value buttons.
        self.restartButton = Button("Restart", toggleRestart, self.myWidget)
        self.volumePlusButton = Button("Vol +", lambda: toggleVolume('up'), self.myWidget)
        self.volumeMinusButton = Button("Vol -", lambda: toggleVolume('down'), self.myWidget)


        self.previousButton = Button("<<", togglePrevious, self.myWidget)
        self.nextButton = Button(">>", toggleNext, self.myWidget)
        

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
        Labels.colorLabel(self.currentTime, "black", "#06F00F")


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

        self.myLayout.addWidget(self.progressbar, 3, 0, 1, 10)
        self.myLayout.addWidget(self.currentTime, 3, 10, 1, 1)

        self.progressbar.setRange(0, 100)
        self.progressbar.setValue(0)
        #self.progressbar.setFormat("0:00")
        self.progressbar.setTextVisible(False)
        self.progressbar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def initThreads(self):
        
        asyncio.ensure_future(updateSongLabelText(self.currentSong))
        asyncio.ensure_future(updateDeviceLabelText(self.currentDevice))
        asyncio.ensure_future(updateSongProgress(self.progressbar))
        asyncio.ensure_future(updateSongTime(self.currentTime))

        
        asyncio.ensure_future(updateLikeButtonText(self.likeButton))
        asyncio.ensure_future(updatePauseButtonText(self.pauseButton))
        asyncio.ensure_future(updateShuffleButtonText(self.shuffleButton))
        asyncio.ensure_future(updateRepeatButtonText(self.repeatButton))
    
        
        '''
        self.updateDevTh = threading.Thread(target=lambda: updateDeviceLabelText(self.currentDevice))
        self.updateDevTh.start()
        
        self.updateSongProgTh = threading.Thread(target=lambda: updateSongProgress(self.progressbar))
        self.updateSongProgTh.start()

        self.updateSongTimeTh = threading.Thread(target=lambda: updateSongTime(self.currentTime))
        self.updateSongTimeTh.start()

        
        self.updateLikeButtonTh = threading.Thread(target=lambda: updateLikeButtonText(self.likeButton))
        self.updateLikeButtonTh.start()

        self.updatePauseButtonTh = threading.Thread(target=lambda: updatePauseButtonText(self.pauseButton))
        self.updatePauseButtonTh.start()

        self.updateShuffleButtonTh = threading.Thread(target=lambda: updateShuffleButtonText(self.shuffleButton))
        self.updateShuffleButtonTh.start()

        self.updateRepeatButtonTh = threading.Thread(target=lambda: updateRepeatButtonText(self.repeatButton))
        self.updateRepeatButtonTh.start()
        '''
    def dynamicBtnWork(self, btnclickFunction, btntextfunction):
        self.worker = ButtonThread(btnclickFunction)
        self.worker.signal.connect(btntextfunction)
        
        self.worker.start()
        
    def staticBtnWork(self, btnclickFunction, widget):
        self.worker = ButtonThread(btnclickFunction)
        self.worker.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()
            
    def mouseMoveEvent(self, event):
        if self.offset != None:
            self.move(self.pos() - self.offset + event.pos())    

    def mouseReleaseEvent(self, event):
        self.offset = None
    
    def setGeometry(self, x, y, w, h):
        super().setGeometry(x, y, w, h)

    def minimizeWindow(self):
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.showNormal()
        self.showMinimized()

    def closeWindow(self):
        global running
        running = False
        self.close()
        exit(1)
        #await getSpotify.pausePlayback()

def formatTime(milliseconds):
    seconds = 0
    minutes = 0
    hours = 0
    time = None
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
        time = str(hours) + ":" + str(minutes) + ":" + str(seconds)
    else:
        time = str(minutes) + ":" + str(seconds)

    return time

async def seekToPosition(position):
    duration = await getSpotify.getProgressAndDuration()
    duration = duration[1]

    newPosition = int(position * duration);

    await getSpotify.seekToPosition(newPosition)   

async def updateSongLabelText(label):
    """
    Updates the song title text every 3 seconds

    """
    while True:
        await asyncio.sleep(2)
        songInfo = await getSpotify.getCurrentSongAndArtist()
        songInfo = list(songInfo)

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
            if song == None or artist == None:
                txt = "Can't get current song or no song is currently playing"
            else:
                txt = song + " - " + artist

        else:
            txt = "Error: Can't get current song or no song is currently playing"

        label.setText(txt)

async def updateDeviceLabelText(label): 

    while True:
        await asyncio.sleep(5)
        device = await getSpotify.getActiveDevice()
        name = "Playing on "
        if device != None:
            devName = device[0]['name']

            if devName != None:
                if len(devName) > 10:
                    devName = devName[0:10] + "..."
                
                name += devName
                #print("NAME: " + name)
            else:
                name = "Can't get current device"
        else:
            name = "Can't get current device"
        
        label.setText(name)

async def updateSongProgress(progressBar):

    while True:
        await asyncio.sleep(1)
        progress = await getSpotify.getProgressAndDuration()

        duration = None
        value = 0
        #print(progress)
        
        if(len(progress) == 2):
            duration = progress[1]
            progress = progress[0]
                
            #print("P: ", progress, " D: ", duration)   
            if (progress != None and duration != None):
                
                value = (int(round((progress/duration) * 100)))
        else:
            print("ERROR - PROG: ", progress)
        
        progressBar.setValue(value)

async def updateSongTime(label):
    
    while True:
        await asyncio.sleep(1)
        progress = await getSpotify.getProgressAndDuration()
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

        else:
            print("ERROR - PROG: ", progress)
        
        label.setText(formattedTime)

async def updatePauseButtonText(label):

    while True:
        await asyncio.sleep(1)
        is_playing = await getSpotify.getPlaybackState()
        txt = ""
        if is_playing == True:
            txt = "Pause"
        else:
            txt = "Play"

        label.setText(txt)

async def updateLikeButtonText(label):
    while True:
        await asyncio.sleep(1)
        state = await getSpotify.getSongLikedState()
        txt = ""
        if state == True:
            txt = "Unlike"
        elif state == False:
            txt = "Like"
        else:
            txt = "Can't Like"

        label.setText(txt)

async def updateShuffleButtonText(label):
    while True:
        await asyncio.sleep(1)

        state = await getSpotify.getShuffleState()
        txt = ""

        if state  == "Shuffled" or state == "Smart Shuffled":
            txt = "Unshuffle"
        elif state == "Unshuffled":
            txt = "Shuffle"
        else:
            txt = "Can't Shuffle"
        
        label.setText(txt)

async def updateRepeatButtonText(label):
    
    while True:
        await asyncio.sleep(1)
        txt = ""
        state = await getSpotify.getRepeatState()

        if state == "off":
            txt = "Repeat On"
        elif state == "context":
            txt = "Repeat 1"
        elif state == "track":
            txt = "Repeat Off"
        else:
            txt = "Can't Repeat"

        label.setText(txt)

def toggleVolume(upOrDown):
    asyncio.ensure_future(changeVolume(upOrDown))

async def changeVolume(upOrDown):
    global msg
    changeable = await getSpotify.volumeChanageable()

    if changeable == False:
        
        print("Device does not support changing volume through this app.")
        if msg == None:
            msg = MsgBox("Device does not support changing volume through this app. Devices such as smartphones " +
                        "usually dont allow for volume changes.", "Error: Volume cant be changed", QMessageBox.Icon.Information)
        else:
            msg.setText("Device does not support changing volume through this app. Devices such as smartphones " +
                        "usually dont allow for volume changes.")
            msg.setWindowTitle("Error: Volume cant be changed")
            msg.setIcon(QMessageBox.Icon.Information)
        msg.showMsg()           
        
            
    else:
        if upOrDown == 'up':
            await getSpotify.volumeUp()
        else:
            await getSpotify.volumeDown()


def toggleNext():
    asyncio.ensure_future(getSpotify.nextPlayback())

def togglePrevious():
    asyncio.ensure_future(getSpotify.previousPlayback())

def toggleRestart():
    asyncio.ensure_future(getSpotify.restartSong())

def toggleLikeSlot():
    asyncio.ensure_future(toggleLike())

async def toggleLike():
    await getSpotify.toggleLikeSong()
    state = await getSpotify.getSongLikedState()

    if state == True:
        return "Unlike"
    else:
        return "Like"

def togglePlaybackSlot():
    asyncio.ensure_future(togglePlayback())

async def togglePlayback():
    print("Toggle playback")
    
    await getSpotify.togglePlayback()
    state = await getSpotify.getPlaybackState()
    if state == True:
        return "Pause"
    else:
        return "Play"
    
def toggleShuffleSlot():
    asyncio.ensure_future(toggleShuffle())

async def toggleShuffle():
    await getSpotify.toggleShuffle()

def toggleRepeatSlot():
    asyncio.ensure_future(toggleRepeat())

async def toggleRepeat():

    await getSpotify.toggleRepeat()

    state = await getSpotify.getRepeatState()

    if state == "off":
        return "Repeat On"
    elif state == "context":
        return "Repeat 1"
    elif state == "track":
        return "Repeat Off"
    else:
        return "Can't Repeat"
    
async def startSpotify(attempts):
    global msg
    dev = await getSpotify.getActiveDevice()
    device, deviceActive = dev
    if device != None:
        print("starting spotify on", device['name'], " ...")
        if deviceActive == True:
            await getSpotify.startPlayback()
        else:
            await getSpotify.restartDevice()
    else:
        #wait for a device.
        #popup saying to start spotify

        if attempts == 0:
            print("No device found")
            if msg == None:
                msg = MsgBox("No device found, please start spotify on one of your devices.", "Error: No device found", QMessageBox.Icon.Warning)
            else:
                msg.setText("No device found, please start spotify on one of your devices.")
                msg.setWindowTitle("Error: No device found")
                msg.setIcon(QMessageBox.Icon.Warning)
            
            msg.showMsg()  
        
        if device == None:
            print("waiting for spotify to start...")
            attempts += 1
            await asyncio.sleep(1)
            dev = await getSpotify.getActiveDevice()
            device, deviceActive = dev
            if attempts > 60:
                print("No device found, closing app...")
                msg.setText("No device found, closing overlay.")
                msg.setWindowTitle("Error: No device found")
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.execMsg()
                return False
                
            return await startSpotify(attempts)


'''
def checkIfAppIsRunning():

    processes =  []
    current_proc = psutil.Process(os.getpid())

    #look for process with the same cmdline.
    for p in psutil.process_iter():
        try:
            if(current_proc.name() == p.name()):
                    if(current_proc.cmdline() == p.cmdline()):
                        
                        processes.append(p)
                        print("PROC FOUND: CMD=", p.cmdline())
                        print("Name: ", p.name())
                        print("EXE:  ", p.exe())
                        print("CWD: ", p.cwd())
        except Exception as e:
            print("Error: ", e)


    #if there is a proc with this cmdline running, cancel this process.
    if len(processes) > 1:
        

        msg = QMessageBox()

        #add flag so that window pops up
        flags = Qt.WindowFlags(Qt.WindowStaysOnTopHint)
        msg.setWindowTitle(f"Error: APP IS ALREADY RUNNING.")
        msg.setText("App is already running.\nIf you're having issues, end the process from the task manager and restart the app.")
        msg.setWindowFlags(flags)
        msg.show()
        flags = msg.windowFlags() 
        
        #remove flag after initial pop up.
        flags &= ~Qt.WindowStaysOnTopHint
        msg.setWindowFlags(flags)

        msg.exec_()

        p = psutil.Process(os.getpid())
        for child in p.children():
            child.kill()
        p.kill()
        exit(0)
'''

async def main(app):
    global threads
    #checkIfAppIsRunning()

    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    myWindow = Window(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
    myWindow.setGeometry(500, 500, 50, 30)
    

    myWindow.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    
    myWindow.show()
    start = await startSpotify(0)
    if start == False:
        print("closing application")
        exit(1)

    print("moving on")

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
    await app_close_event.wait()
    print("moving on")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    asyncio.run(main(app), loop_factory=QEventLoop)
