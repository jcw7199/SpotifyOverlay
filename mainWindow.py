import tkinter
import getSpotify
from threading import Thread

exit = 0


root = tkinter.Tk()

def center_window(width, height):
    # get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = 0
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def start_move(event):
    global lastx, lasty
    lastx = event.x_root
    lasty = event.y_root

def move_window(event):
    global lastx, lasty
    deltax = event.x_root - lastx
    deltay = event.y_root - lasty
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry("+%s+%s" % (x, y))
    lastx = event.x_root
    lasty = event.y_root

def close_window ():
    global exit

    exit = -1
    root.destroy()

def updateShuffle(button=tkinter.Button):
    state = getSpotify.getShuffleState()
    #print("updating shuffle: ", state)
    
    if state  == False:
        button.configure(text="Shuffle")
    elif state == True:
        button.configure(text="Unshuffle")
    else:
        button.configure(text="Can't shuffle")

def updateRepeat(button=tkinter.Button):
    state = getSpotify.getRepeatState()
    if state == "off":
        button.configure(text="Repeat On")
    elif state == "context":
        button.configure(text="Repeat 1")
    elif state == "track":
        button.configure(text="Repeat Off")
    else:
        button.configure(text="Can't Repeat")

def updateLike(button=tkinter.Button):
    state =  getSpotify.getSongLikedState() 
    if state == True:
        button.configure(text="Unlike")
    else:
        button.configure(text="Like")

def updatePause(button=tkinter.Button):
    is_playing = getSpotify.getPlaybackState()
    if is_playing == True:
        button.configure(text="Pause")
    else:
        button.configure(text="Play") 

def updateSong(label=tkinter.Label):
    text = getSpotify.getCurrentSongAndArtist()
    #print("updating song", text)
    if len(text) > 70:
        text = text[0:70] + "..."
    label.configure(text = text)

def updateWindow(like=tkinter.Button, pause=tkinter.Button, shuffle=tkinter.Button, repeat=tkinter.Button, song=tkinter.Label):
    while True:
        updateLike(button=like)
        updatePause(button=pause)
        updateShuffle(button=shuffle)
        updateRepeat(button=repeat)
        updateSong(label=song)   

def supportsVolume():
    if getSpotify.volumeChanageable() == False:
        newWindow = tkinter.Toplevel()
        device = getSpotify.getActiveDevice()[0]['type']

        label = tkinter.Label(newWindow, text = str("Can't change volume because device does not support it.\n Device: " + device), bg="green", fg="white")
        label.pack()
        close = tkinter.Button(newWindow, text="close window", command=newWindow.destroy, bg="black", fg="white")
        close.pack()

class Labels:
    currentSong = tkinter.Label(root, text = getSpotify.getCurrentSongAndArtist(), bg="green", fg="white")
    currentSong.place(x = 0,y = 0)

class Buttons:
    
    quitButton = tkinter.Button(root, text = "Quit", anchor="ne", command = close_window, bg="red", fg="white")
    quitButton.place(x = 460, y = 0)
    
    likeButtonText = ""
    if getSpotify.getSongLikedState() == True:
        likeButtonText = "Unlike"
    else:
        likeButtonText = "Like"

    likeButton = tkinter.Button(root, text = likeButtonText, command = lambda : [getSpotify.toggleLikeSong(), updateLike(button=Buttons.likeButton)], bg="green", fg="white")
    likeButton.place(x = 0, y = 30)

    volumeMinusButton = tkinter.Button(root, text ="Vol -", command = lambda: [supportsVolume(), getSpotify.volumeDown()], bg="green", fg="white")
    volumeMinusButton.place(x = 55, y = 30)

    volumePlusButton = tkinter.Button(root, text ="Vol +", command = lambda: [supportsVolume(), getSpotify.volumeUp()], bg="green", fg="white")
    volumePlusButton.place(x = 100, y = 30)

    prevButton = tkinter.Button(root, text = " << ", command = lambda : [getSpotify.previousPlayback(), updateSong(label=Labels.currentSong)], bg="green", fg="white")
    prevButton.place(x = 165, y = 30)

    pauseButtonText = ""
    if getSpotify.getPlaybackState() == True:
        pauseButtonText = "Pause"
    else:
        pauseButtonText = "Play"

    pauseButton = tkinter.Button(root, text = pauseButtonText, command = lambda : [getSpotify.togglePlayback(), updatePause(button=Buttons.pauseButton)], bg="green", fg="white")
    pauseButton.place(x = 200, y = 30)

    nextButton = tkinter.Button(root, text = " >> ", command = lambda : [getSpotify.nextPlayback(), updateSong()], bg="green", fg="white")
    nextButton.place(x = 245, y = 30)
    

    shuffleButtonText = ""
    if getSpotify.getShuffleState() == True:
        shuffleButtonText = "Unshuffle"
    else:
        shuffleButtonText = "Shuffle"

    shuffleButton = tkinter.Button(root, text = shuffleButtonText, command = lambda : [getSpotify.toggleShuffle(), updateShuffle(button=Buttons.shuffleButton)], bg="green", fg="white")
    shuffleButton.place(x = 300, y = 30)

    repeatButtonText = ""
    if getSpotify.getRepeatState() == "off":
        repeatButtonText = "Repeat On"
    elif getSpotify.getRepeatState() == "context":
        repeatButtonText = "Repeat 1"
    elif getSpotify.getRepeatState() == "track":
        repeatButtonText = "Repeat Off"
    else:
        repeatButtonText = "Can't Repeat"

    repeatButton = tkinter.Button(root, text = repeatButtonText, command = lambda : [getSpotify.toggleRepeat(), updateRepeat(button=Buttons.repeatButton) ], bg="green", fg="white")
    repeatButton.place(x = 380, y = 30)


root.overrideredirect(True)
root.configure(background='black')



root.attributes('-topmost',True)
root.attributes('-alpha', 0.7)

center_window(500, 60)
root.bind("<ButtonPress-1>", start_move)
root.bind('<B1-Motion>', move_window)

"""
updatePauseThread = Thread(target = updatePauseThreadMethod, kwargs={'button': Buttons.pauseButton})
updatePauseThread.daemon = True

updateRepeatThread = Thread(target = updateRepeatThreadMethod, kwargs={'button': Buttons.repeatButton})
updateRepeatThread.daemon = True

updateLikeThread = Thread(target = updateLikeThreadMethod,  kwargs={'button': Buttons.likeButton})
updateLikeThread.daemon = True


updateShuffleThread = Thread(target = updateShuffleThreadMethod,  kwargs={'button': Buttons.shuffleButton})
updateShuffleThread.daemon = True


updateSongThread = Thread(target = updateSong,  kwargs={'label': Labels.currentSong})
updateSongThread.daemon = True


updatePauseThread.start()
updateRepeatThread.start()
updateLikeThread.start()
updateShuffleThread.start()
updateSongThread.start()
"""
updateThread = Thread(target=updateWindow, kwargs={'like': Buttons.likeButton, 'pause': Buttons.pauseButton, 
                                                   'shuffle': Buttons.shuffleButton, 'repeat': Buttons.repeatButton,
                                                   'song': Labels.currentSong}
                    )

updateThread.daemon = True
updateThread.start()
root.mainloop()


