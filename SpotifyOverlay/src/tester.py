import asyncio
import sys

from PyQt6 import QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import qasync
from qasync import QEventLoop, asyncClose, asyncSlot


@asyncSlot()
async def test(button):
    button.setText("Done!")

@asyncSlot()
async def togglePlayback():
    print("Toggle playback")




class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.button = QPushButton("Load", self)
        self.button2 = QPushButton("Load2", self)
        self.button.clicked.connect(self.onButtonClicked)
        self.button2.clicked.connect(lambda: test(self.button2))
        layout.addWidget(self.button)
        self.setLayout(layout)

    @asyncSlot()
    async def onButtonClicked(self):
        """
        Use async code in a slot by decorating it with @asyncSlot.
        """
        self.button.setText("Loading...")
        await asyncio.sleep(1)
        self.button.setText("Load")

    @asyncClose
    async def closeEvent(self, event: QCloseEvent):
        """
        Use async code in a closeEvent by decorating it with @asyncClose.
        """
        self.button.setText("Closing...")
        await asyncio.sleep(1)


async def main(app):
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    main_window = MainWindow()
    main_window.show()
    await app_close_event.wait()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # for python 3.11 or newer
    print(type(togglePlayback))
    print(callable(togglePlayback))    # for python 3.10 or older
    # qasync.run(main(app))
    