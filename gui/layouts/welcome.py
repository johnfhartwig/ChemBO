import pickle as pkl
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from .new_proj import NewProject
from .main import ChemBOMain
from .utils import *

class Welcome(object):
    def __init__(self, config):
        self.config = config
        recents = set()
        self.config.recents = [x for x in self.config.recents if not (x in recents or recents.add(x))]
        self.config.write()

    def setupUi(self, mainWindow):
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(16)

        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(500, 400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        mainWindow.setSizePolicy(sizePolicy)
        mainWindow.setMinimumSize(QtCore.QSize(500, 400))
        mainWindow.setMaximumSize(QtCore.QSize(500, 400))
        mainWindow.setWindowTitle("Welcome to ChemBO!")

        self.centralwidget = QtWidgets.QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.newBtn = QtWidgets.QPushButton(self.centralwidget)
        self.newBtn.setGeometry(QtCore.QRect(0, 0, 300, 50))
        self.newBtn.setFont(font)
        self.newBtn.setObjectName("newBtn")
        self.newBtn.setText("New ChemBO project")
        self.newBtn.clicked.connect(lambda: self.newProject(mainWindow))

        self.loadBtn = QtWidgets.QPushButton(self.centralwidget)
        self.loadBtn.setGeometry(QtCore.QRect(0, 40, 300, 50))
        self.loadBtn.setFont(font)
        self.loadBtn.setObjectName("loadBtn")
        self.loadBtn.setText("Load ChemBO project")
        self.loadBtn.clicked.connect(lambda: self.loadProject(mainWindow))

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(15, 110, 300, 30))
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label.setText("Recent ChemBO projects")

        self.recents = QtWidgets.QListWidget(self.centralwidget)
        self.recents.setGeometry(QtCore.QRect(10, 140, 480, 210))
        self.recents.setObjectName("recents")
        self.recents.setFont(font)
        self.recents.itemDoubleClicked.connect(lambda: self.loadRecent(mainWindow))

        self.openBtn = QtWidgets.QPushButton(self.centralwidget)
        self.openBtn.setGeometry(QtCore.QRect(375, 350, 120, 40))
        self.openBtn.setObjectName("openBtn")
        self.openBtn.setFont(font)
        self.openBtn.setText("Open")
        self.openBtn.clicked.connect(lambda: self.loadRecent(mainWindow))

        self.config.recents = [x for x in self.config.recents if os.path.exists(x)]
        self.config.write()

        for i, fname in enumerate(self.config.recents):
            self.recents.addItem(fname.split(os.sep)[-1])

        mainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def newProject(self, mainWindow):
        dlg = QtWidgets.QDialog()
        new_proj = NewProject()
        new_proj.setupUi(dlg)
        if dlg.exec():
            fname = new_proj.expt.save('')
            self.config.cbo_path = fname.rsplit(os.sep, 1)[0]
            self.config.recents.insert(0, os.path.abspath(fname))
            self.config.write()
            self.runMain(mainWindow, new_proj.expt, os.path.abspath(fname))

    def loadProject(self, mainWindow):
        fname = QtWidgets.QFileDialog.getOpenFileName(None,
                'Open...',
                self.config.cbo_path,
                "ChemBO files (*.cbo)")[0]
        if not fname:
            return
        try:
            with open(fname, 'rb') as f:
                expt = pkl.load(f)
            assert isinstance(expt, Experiment)
        except pkl.UnpicklingError or AssertionError:
            err = QtWidgets.QErrorMessage(mainWindow)
            err.showMessage(f'{fname} is not a valid ChemBO experiment file.')
            return
        
        self.config.cbo_path = fname.rsplit(os.sep, 1)[0]
        self.config.recents.insert(0, os.path.abspath(fname))
        self.config.write()
        self.runMain(mainWindow, expt, fname)

    def loadRecent(self, mainWindow):
        selected = self.recents.selectedIndexes()
        if len(selected) == 0:
            return
        idx = selected[0].row()
        fname = self.config.recents.pop(idx)
        try:
            with open(fname, 'rb') as f:
                expt = pkl.load(f)
            assert isinstance(expt, Experiment)
        except pkl.UnpicklingError or AssertionError:
            err = QtWidgets.QErrorMessage(mainWindow)
            err.showMessage(f'{fname} is not a valid ChemBO experiment file.')
            return
        self.config.recents.insert(0, fname)
        self.config.write()
        self.runMain(mainWindow, expt, fname)

    def runMain(self, mainWindow, expt, fname):
        if expt is None:
            return
        main = ChemBOMain(expt, fname, self.config)
        main.setupUi(mainWindow)

if __name__ == "__main__":
    import sys

    try:
        with open('.ChemBO_config.pkl', 'rb') as f:
            config = pkl.load(f)
        assert(isinstance(config, ChemBOConfig))
    except FileNotFoundError or pkl.UnpicklingError or AssertionError:
        print(f'Creating new ChemBO config file in {os.getcwd()}.')
        config = ChemBOConfig()
        config.write()

    app = QtWidgets.QApplication(sys.argv)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("gui/assets/tray.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    app.setWindowIcon(icon)

    mainWindow = QtWidgets.QMainWindow()
    ui = Welcome(config)
    ui.setupUi(mainWindow)

    mainWindow.show()
    sys.exit(app.exec_())

