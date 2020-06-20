from PyQt5 import QtCore, QtGui, QtWidgets

from .utils import *

class ChemBOMain(object):
    fc_icon = None
    pc_icon = None
    cc_icon = None

    def __init__(self, expt, save_path, config):
        ChemBOMain.fc_icon = QtGui.QIcon()
        ChemBOMain.fc_icon.addPixmap(QtGui.QPixmap("../assets/fc.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ChemBOMain.pc_icon = QtGui.QIcon()
        ChemBOMain.pc_icon.addPixmap(QtGui.QPixmap("../assets/pc.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ChemBOMain.cc_icon = QtGui.QIcon()
        ChemBOMain.cc_icon.addPixmap(QtGui.QPixmap("../assets/cc.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.expt = expt
        self.save_path = save_path
        self.saved = True
        self.config = config

    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.setMinimumSize(QtCore.QSize(500, 400))
        mainWindow.setMaximumSize(QtCore.QSize(10000, 10000))
        mainWindow.resize(800, 540)

        self.centralwidget = QtWidgets.QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.mainVLayout = QtWidgets.QVBoxLayout()
        self.mainVLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.mainVLayout.setObjectName("mainVLayout")

        self.topHLayout = QtWidgets.QHBoxLayout()
        self.topHLayout.setObjectName("topHLayout")

        self.ulLayout = QtWidgets.QVBoxLayout()
        self.ulLayout.setObjectName("ulLayout")

        self.titleText = QtWidgets.QLabel(self.centralwidget)
        self.titleText.setMinimumSize(QtCore.QSize(0, 25))
        self.titleText.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.titleText.setFont(font)
        self.titleText.setObjectName("titleText")
        self.titleText.setText(self.expt.name)

        self.ulLayout.addWidget(self.titleText)

        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setMinimumSize(QtCore.QSize(50, 10))
        self.progressBar.setMaximumSize(QtCore.QSize(500, 10))
        self.progressBar.setProperty("value", 100)
        self.progressBar.setObjectName("progressBar")
        self.ulLayout.addWidget(self.progressBar)

        self.progressText = QtWidgets.QLabel(self.centralwidget)
        self.progressText.setMinimumSize(QtCore.QSize(0, 20))
        self.progressText.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        self.progressText.setFont(font)
        self.progressText.setObjectName("progressText")
        self.ulLayout.addWidget(self.progressText)
        self.topHLayout.addLayout(self.ulLayout)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.topHLayout.addItem(spacerItem)
        self.urLayout = QtWidgets.QVBoxLayout()
        self.urLayout.setObjectName("urLayout")

        self.bestValue = QtWidgets.QLabel(self.centralwidget)
        self.bestValue.setMinimumSize(QtCore.QSize(0, 20))
        self.bestValue.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        self.bestValue.setFont(font)
        self.bestValue.setObjectName("bestValue")
        self.urLayout.addWidget(self.bestValue)

        self.bestText = QtWidgets.QLabel(self.centralwidget)
        self.bestText.setMinimumSize(QtCore.QSize(0, 20))
        self.bestText.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        self.bestText.setFont(font)
        self.bestText.setObjectName("bestText")
        self.urLayout.addWidget(self.bestText)

        self.logBtn = QtWidgets.QPushButton(self.centralwidget)
        self.logBtn.setMinimumSize(QtCore.QSize(100, 30))
        self.logBtn.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        self.logBtn.setFont(font)
        self.logBtn.setObjectName("logBtn")
        self.logBtn.setText("View log")
        self.logBtn.clicked.connect(lambda: self.log())
        self.urLayout.addWidget(self.logBtn)

        self.topHLayout.addLayout(self.urLayout)
        self.mainVLayout.addLayout(self.topHLayout)
        self.bottomHLayout = QtWidgets.QHBoxLayout()
        self.bottomHLayout.setObjectName("bottomHLayout")
        
        self.variableTree = QtWidgets.QTreeWidget(self.centralwidget)
        self.variableTree.setMinimumSize(QtCore.QSize(200, 300))
        self.variableTree.setMaximumSize(QtCore.QSize(300, 16777215))
        self.variableTree.setObjectName("variableTree")
        self.variableTree.headerItem().setText(0, "Variables")
        for var in self.expt.variables:
            self.addVariable(var)
        self.bottomHLayout.addWidget(self.variableTree)

        self.brLayout = QtWidgets.QVBoxLayout()
        self.brLayout.setObjectName("brLayout")

        self.nextText = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.nextText.setFont(font)
        self.nextText.setObjectName("nextText")
        self.nextText.setText("Next batch:")
        self.brLayout.addWidget(self.nextText)

        self.nextTable = QtWidgets.QTableWidget(self.centralwidget)
        self.nextTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.nextTable.setWordWrap(False)
        self.nextTable.setCornerButtonEnabled(False)
        self.nextTable.setObjectName("nextTable")
        self.nextTable.setColumnCount(3)
        self.nextTable.setRowCount(self.expt.batch_size)
        
        self.batchValues = []
        self.batchChecks = []
        self.batchText = []
        for i in range(self.expt.batch_size):
            item = QtWidgets.QTableWidgetItem()
            self.nextTable.setVerticalHeaderItem(i, item)

            spinBox = QtWidgets.QDoubleSpinBox()
            spinBox.setObjectName(f"spinBox{i}")
            spinBox.setMaximum(100.0)
            spinBox.setMinimum(-100.0)
            self.batchValues.append(spinBox)
            self.nextTable.setCellWidget(i, 0, spinBox)

            widget = QtWidgets.QWidget()
            checkBox = QtWidgets.QCheckBox()
            checkBox.setObjectName(f"checkBox{i}")
            self.batchChecks.append(checkBox)
            layout = QtWidgets.QHBoxLayout(widget)
            layout.addWidget(checkBox)
            layout.setAlignment(QtCore.Qt.AlignCenter)
            self.nextTable.setCellWidget(i, 1, widget)

            label = QtWidgets.QLabel()
            label.setObjectName(f"label{i}")
            self.batchText.append(label)
            self.nextTable.setCellWidget(i, 2, label)

        item = QtWidgets.QTableWidgetItem()
        self.nextTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.nextTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.nextTable.setHorizontalHeaderItem(2, item)
        self.nextTable.horizontalHeader().setDefaultSectionSize(55)
        self.nextTable.horizontalHeader().setSortIndicatorShown(False)
        self.nextTable.horizontalHeader().setStretchLastSection(True)
        self.brLayout.addWidget(self.nextTable)

        for i in range(self.expt.batch_size):
            item = self.nextTable.verticalHeaderItem(i)
            item.setText(f"{i+1}")
        item = self.nextTable.horizontalHeaderItem(0)
        item.setText("Value")
        item = self.nextTable.horizontalHeaderItem(1)
        item.setText("Remove")
        item = self.nextTable.horizontalHeaderItem(2)
        item.setText("Variables")

        self.brbLayout = QtWidgets.QHBoxLayout()
        self.brbLayout.setObjectName("brbLayout")

        self.subBtn = QtWidgets.QPushButton(self.centralwidget)
        self.subBtn.setMinimumSize(QtCore.QSize(100, 30))
        self.subBtn.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        self.subBtn.setFont(font)
        self.subBtn.setObjectName("subBtn")
        self.subBtn.setText("Submit")
        self.subBtn.clicked.connect(lambda: self.submit())
        self.brbLayout.addWidget(self.subBtn)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.brbLayout.addItem(spacerItem)

        self.savedLabel = QtWidgets.QLabel(self.centralwidget)
        self.savedLabel.setMinimumSize(QtCore.QSize(100, 40))
        self.savedLabel.setMaximumSize(QtCore.QSize(100, 40))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        self.savedLabel.setFont(font)
        self.savedLabel.setObjectName("savedLabel")
        self.savedLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.brbLayout.addWidget(self.savedLabel)

        self.saveBtn = QtWidgets.QPushButton(self.centralwidget)
        self.saveBtn.setMinimumSize(QtCore.QSize(100, 30))
        self.saveBtn.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(14)
        self.saveBtn.setFont(font)
        self.saveBtn.setObjectName("saveBtn")
        self.saveBtn.setText("Save")
        self.saveBtn.clicked.connect(lambda: self.save())
        self.brbLayout.addWidget(self.saveBtn)

        self.brLayout.addLayout(self.brbLayout)

        self.bottomHLayout.addLayout(self.brLayout)
        self.mainVLayout.addLayout(self.bottomHLayout)
        self.gridLayout.addLayout(self.mainVLayout, 0, 0, 1, 1)

        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuFile.setTitle("File")

        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuHelp.setTitle("Help")
        
        self.actionNew = QtWidgets.QAction(mainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionNew.setText("New...")
        self.actionNew.setShortcut("Ctrl+N")
        self.actionNew.triggered.connect(lambda: self.new(mainWindow))
        self.menuFile.addAction(self.actionNew)

        self.actionSave = QtWidgets.QAction(mainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave.setText("Save")
        self.actionSave.setShortcut("Ctrl+S")
        self.actionSave.triggered.connect(lambda: self.save())
        self.menuFile.addAction(self.actionSave)

        self.actionSaveAs = QtWidgets.QAction(mainWindow)
        self.actionSaveAs.setObjectName("actionSaveAs")
        self.actionSaveAs.setText("Save As...")
        self.actionSaveAs.triggered.connect(lambda: self.save_as())
        self.menuFile.addAction(self.actionSaveAs)

        self.actionOpen = QtWidgets.QAction(mainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen.setText("Open ChemBO project...")
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionOpen.triggered.connect(lambda: self.open(mainWindow))
        self.menuFile.addAction(self.actionOpen)

        self.actionHelp = QtWidgets.QAction(mainWindow)
        self.actionHelp.setObjectName("actionHelp")
        self.actionHelp.setText("Help")
        self.menuHelp.addAction(self.actionHelp)

        self.actionLog = QtWidgets.QAction(mainWindow)
        self.actionLog.setObjectName("actionLog")
        self.actionLog.setText("View ChemBO log...")
        self.menuHelp.addAction(self.actionLog)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        mainWindow.setMenuBar(self.menubar)

        mainWindow.setWindowTitle(f"ChemBO - {self.expt.name}")

        self.repaint()
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def repaint(self):
        self.progressBar.setProperty("value", 100*self.expt.done / self.expt.recommended)
        self.progressText.setText(f"<html><head/><body><p>Finished <b>{self.expt.done}</b> reactions (<b>{self.expt.recommended}</b> recommended)</p></body></html>")
        
        self.bestValue.setText(f"<html><head/><body><p>Best value observed: <b>{self.expt.best}</b></p></body></html>")
        self.bestText.setText(f"<b>{self.expt.best_text}</b>")

        if self.saved:
            self.savedLabel.setText("Saved")
        else:
            self.savedLabel.setText("<b>Not Saved</b>")

        batch = self.expt.get_batch()
        for i in range(self.expt.batch_size):
            self.batchText[i].setText(batch[i])

    def addVariable(self, var):
        root_item = QtWidgets.QTreeWidgetItem(self.variableTree)
        num_values = 0
        if isinstance(var, FCVariable):
            root_item.setIcon(0, ChemBOMain.fc_icon)
            num_values = len(var.values)
            for name in var.values:
                item = QtWidgets.QTreeWidgetItem(root_item)
                item.setText(0, name)
        elif isinstance(var, PCVariable):
            root_item.setIcon(0, ChemBOMain.pc_icon)
            for group, names in var.groups.items():
                group_item = QtWidgets.QTreeWidgetItem(root_item)
                group_item.setText(0, group)
                num_values += len(names)
                for name in names:
                    item = QtWidgets.QTreeWidgetItem(group_item)
                    item.setText(0, name)
        elif isinstance(var, CCVariable):
            root_item.setIcon(0, ChemBOMain.cc_icon)
            num_values = len(var.labels)
            for name in var.labels:
                item = QtWidgets.QTreeWidgetItem(root_item)
                item.setText(0, name)

        root_item.setText(0, f'{var.name} ({num_values})')

    def checkSaved(self):
        if not self.saved:
            box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Are you sure?",
                    f"Are you sure you want to close {self.expt.name} without saving?",
                    QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)
            reply = box.exec()
            if reply == QtWidgets.QMessageBox.Discard:
                return True
            elif reply == QtWidgets.QMessageBox.Save:
                return self.save()
            else:
                return False
        return True

    def new(self, mainWindow):
        from .welcome import Welcome
        if not self.checkSaved():
            return
        welcome = Welcome(self.config)
        welcome.newProject(mainWindow)

    def save(self):
        fname = self.expt.save(self.save_path, self.config.cbo_path)
        if fname:
            self.save_path = fname
            self.config.recents.insert(0, os.path.abspath(fname))
            self.saved = True
        self.repaint()
        return bool(fname)

    def save_as(self):
        fname = self.expt.save('', self.config.cbo_path)
        if fname:
            self.save_path = fname
            self.config.recents.insert(0, os.path.abspath(fname))
            self.saved = True
        self.repaint()
        return bool(fname)

    def open(self, mainWindow):
        from .welcome import Welcome
        if not self.checkSaved():
            return
        welcome = Welcome(self.config)
        welcome.loadProject(mainWindow)

    def submit(self):
        values = []
        for i in range(self.expt.batch_size):
            if self.batchChecks[i].isChecked():
                values.append(None)
            else:
                values.append(float(self.batchValues[i].value()))
        self.expt.input_batch(values)
        self.saved = False
        self.repaint()

    def log(self):
        box = LogBox(QtWidgets.QMessageBox.NoIcon, "ChemBO Log", 
                self.config.get_log(), QtWidgets.QMessageBox.Close, self.centralwidget)

if __name__ == "__main__":
    import sys
    from collections import OrderedDict
    app = QtWidgets.QApplication(sys.argv)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("../assets/tray.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    app.setWindowIcon(icon)

    var0 = FCVariable('Diamine', ['SS-DPEN', 'SS-DACH', 'SS-Bn2-DACH', 'S-DAIPEN', 'SS-bipyrrolidine', 'S-BINAMINE', 'SS-ANDEN', 'en',
            'SS-pNMe2-DPEN', 'SS-pOMe-DPEN', 'SS-1Nap-DPEN', 'SS-pNO2-DPEN', 'SS-TMB-DPEN', 'Me2-en', 'Bn2-en', 'Me2-DAP'])
    names = OrderedDict()
    names['S-biaryl'] = ['S-BINAP', 'S-TolBINAP', 'S-DM-BINAP', 'S-H8-BINAP', 'S-SEGPHOS', 'S-DM-SEGPHOS', 'S-DTBM-SEGPHOS']
    names['R-biaryl'] = ['R-BINAP', 'R-TolBINAP', 'R-DM-BINAP', 'R-H8-BINAP', 'R-SEGPHOS', 'R-DM-SEGPHOS', 'R-DTBM-SEGPHOS']
    names['SS-bisphospholano'] = [str(x) for x in range(2)]
    names['RR-bisphospholano'] = [str(x) for x in range(3)]
    names['S-PHANEPHOS'] = ['1']
    names['R-PHANEPHOS'] = ['1']
    names['BIPHEP'] = ['1']
    names['dppb'] = ['1']
    names['Xantphos'] = ['1']
    var1 = PCVariable('Diphosphine', names)
    expt = Experiment('Noyori', 5, [var0, var1])
    print(expt.get_batch())
    expt.input_batch([1.0, 2.0, 3.0, 4.0, 5.0])
    print(expt.best)
    print(expt.best_text)

    mainWindow = QtWidgets.QMainWindow()
    ui = ChemBOMain()
    ui.setupUi(mainWindow)

    mainWindow.show()
    sys.exit(app.exec_())
