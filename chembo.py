import sys
import os
import pickle as pkl

from PyQt5 import QtCore, QtGui, QtWidgets

from gui.layouts.welcome import Welcome
from gui.layouts.utils import *

def main():
    try:
        with open('.ChemBO_config.pkl', 'rb') as f:
            config = pkl.load(f)
        assert(isinstance(config, ChemBOConfig))
    except FileNotFoundError or pkl.UnpicklingError or AssertionError:
        config = ChemBOConfig()
        print(f'Creating new ChemBO config file in {os.getcwd()}')
        config.write()

    set_config(config)

    app = QtWidgets.QApplication(sys.argv)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("gui/assets/tray.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    app.setWindowIcon(icon)

    mainWindow = QtWidgets.QMainWindow()
    ui = Welcome(config)
    ui.setupUi(mainWindow)

    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

