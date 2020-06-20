from PyQt5 import QtCore, QtGui, QtWidgets

from .utils import *
from .var_editor import VarEditor
from .main import ChemBOMain

class NewProject(object):
    fc_icon = None
    pc_icon = None
    cc_icon = None

    def __init__(self):
        NewProject.fc_icon = QtGui.QIcon()
        NewProject.fc_icon.addPixmap(QtGui.QPixmap("fc.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        NewProject.pc_icon = QtGui.QIcon()
        NewProject.pc_icon.addPixmap(QtGui.QPixmap("pc.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        NewProject.cc_icon = QtGui.QIcon()
        NewProject.cc_icon.addPixmap(QtGui.QPixmap("cc.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

    def setupUi(self, Dialog):
        self.dialog = Dialog

        # Main window + widget
        Dialog.setObjectName("Dialog")
        Dialog.resize(750, 500)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(750, 500))
        Dialog.setMaximumSize(QtCore.QSize(750, 500))
        Dialog.setWindowTitle("New ChemBO project")
        
        self.centralwidget = QtWidgets.QWidget(Dialog)
        self.centralwidget.setObjectName("centralwidget")

        # Font
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(16)

        # Name label
        self.nameLabel = QtWidgets.QLabel(self.centralwidget)
        self.nameLabel.setGeometry(QtCore.QRect(10, 5, 120, 30))
        self.nameLabel.setFont(font)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Project Name:")

        # Name input
        self.nameEditor = QtWidgets.QLineEdit(self.centralwidget)
        self.nameEditor.setGeometry(QtCore.QRect(130, 5, 400, 30))
        self.nameEditor.setFont(font)
        self.nameEditor.setObjectName("nameEditor")

        # Batch size label
        self.bsLabel = QtWidgets.QLabel(self.centralwidget)
        self.bsLabel.setGeometry(QtCore.QRect(570, 5, 120, 30))
        self.bsLabel.setFont(font)
        self.bsLabel.setObjectName("bsLabel")
        self.bsLabel.setText("Batch size:")

        # Batch size spinbox
        self.bsInput = QtWidgets.QSpinBox(self.centralwidget)
        self.bsInput.setGeometry(QtCore.QRect(670, 5, 50, 30))
        self.bsInput.setFont(font)
        self.bsInput.setMinimum(1)
        self.bsInput.setMaximum(50)
        self.bsInput.setObjectName("bsInput")

        self.doneBtn = QtWidgets.QPushButton(self.centralwidget)
        self.doneBtn.setGeometry(QtCore.QRect(540, 390, 200, 50))
        self.doneBtn.setMinimumSize(QtCore.QSize(50, 50))
        self.doneBtn.setMaximumSize(QtCore.QSize(16777215, 50))
        self.doneBtn.setFont(font)
        self.doneBtn.setObjectName("doneBtn")
        self.doneBtn.setText("Done!")
        self.doneBtn.clicked.connect(lambda: self.done())

        self.cancelBtn = QtWidgets.QPushButton(self.centralwidget)
        self.cancelBtn.setGeometry(QtCore.QRect(540, 440, 200, 50))
        self.cancelBtn.setMinimumSize(QtCore.QSize(50, 50))
        self.cancelBtn.setMaximumSize(QtCore.QSize(16777215, 50))
        self.cancelBtn.setFont(font)
        self.cancelBtn.setObjectName("cancelBtn")
        self.cancelBtn.setText("Cancel")
        self.cancelBtn.clicked.connect(lambda: self.cancel())

        # Separating line
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(10, 40, 730, 3))
        self.line.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line.setLineWidth(2)
        self.line.setMidLineWidth(1)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")

        # Variables
        self.variables = []

        self.variableTree = QtWidgets.QTreeWidget(self.centralwidget)
        self.variableTree.setGeometry(QtCore.QRect(10, 50, 520, 440))
        self.variableTree.setFont(font)
        self.variableTree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.variableTree.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.variableTree.setIconSize(QtCore.QSize(20, 20))
        self.variableTree.setAnimated(True)
        self.variableTree.setColumnCount(1)
        self.variableTree.setObjectName("variableTree")
        self.variableTree.headerItem().setText(0, "Variable")
        self.variableTree.currentItemChanged.connect(lambda curr, _: self.repaint(curr))

        self.addBtn = QtWidgets.QPushButton(self.centralwidget)
        self.addBtn.setGeometry(QtCore.QRect(540, 50, 200, 50))
        self.addBtn.setMinimumSize(QtCore.QSize(50, 50))
        self.addBtn.setMaximumSize(QtCore.QSize(16777215, 50))
        self.addBtn.setFont(font)
        self.addBtn.setObjectName("addBtn")
        self.addBtn.setText("Add...")
        self.addBtn.clicked.connect(lambda: self.newVar())

        self.editBtn = QtWidgets.QPushButton(self.centralwidget)
        self.editBtn.setGeometry(QtCore.QRect(540, 100, 200, 50))
        self.editBtn.setMinimumSize(QtCore.QSize(50, 50))
        self.editBtn.setMaximumSize(QtCore.QSize(16777215, 50))
        self.editBtn.setFont(font)
        self.editBtn.setObjectName("editBtn")
        self.editBtn.setText("Edit...")
        self.editBtn.setEnabled(False)
        self.editBtn.clicked.connect(lambda: self.editVar())

        self.deleteBtn = QtWidgets.QPushButton(self.centralwidget)
        self.deleteBtn.setGeometry(QtCore.QRect(540, 150, 200, 50))
        self.deleteBtn.setMinimumSize(QtCore.QSize(50, 50))
        self.deleteBtn.setMaximumSize(QtCore.QSize(16777215, 50))
        self.deleteBtn.setFont(font)
        self.deleteBtn.setObjectName("deleteBtn")
        self.deleteBtn.setText("Delete")
        self.deleteBtn.setEnabled(False)
        self.deleteBtn.clicked.connect(lambda: self.deleteVar())

        self.expt = None

        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def newVar(self):
        dlg = QtWidgets.QDialog()
        var_editor = VarEditor()
        var_editor.setupUi(dlg)
        if dlg.exec():
            self.addVariable(var_editor.variable)

    def editVar(self):
        var = self.variableTree.selectedItems()[0]
        if var is None:
            return
        if var.parent() is not None:
            var = var.parent()
        if var.parent() is not None:
            var = var.parent()
        idx = self.variableTree.indexOfTopLevelItem(var)

        dlg = QtWidgets.QDialog()
        var_editor = VarEditor(self.variables[idx])
        var_editor.setupUi(dlg)
        if dlg.exec():
            self.variableTree.takeTopLevelItem(idx)
            self.variables.pop(idx)
            self.addVariable(var_editor.variable, idx)

    def deleteVar(self):
        var = self.variableTree.selectedItems()[0]
        if var is None:
            return
        if var.parent() is not None:
            var = var.parent()
        if var.parent() is not None:
            var = var.parent()

        idx = self.variableTree.indexOfTopLevelItem(var)
        box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Cancel",
                f"Are you sure you want to delete the variable named {self.variables[idx].name}?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        reply = box.exec()
        if reply == QtWidgets.QMessageBox.Yes:
            self.variableTree.takeTopLevelItem(idx)
            self.variables.pop(idx)

    def addVariable(self, var, idx=None):
        if var is None:
            return
        if idx is None:
            idx = len(self.variables)
        self.variables.insert(idx, var)
        root_item = QtWidgets.QTreeWidgetItem()
        self.variableTree.insertTopLevelItem(idx, root_item)
        if isinstance(var, FCVariable):
            root_item.setIcon(0, NewProject.fc_icon)
            for name in var.values:
                item = QtWidgets.QTreeWidgetItem(root_item)
                item.setText(0, name)
        elif isinstance(var, PCVariable):
            root_item.setIcon(0, NewProject.pc_icon)
            for group, names in var.groups.items():
                group_item = QtWidgets.QTreeWidgetItem(root_item)
                group_item.setText(0, group)
                for name in names:
                    item = QtWidgets.QTreeWidgetItem(group_item)
                    item.setText(0, name)
        elif isinstance(var, CCVariable):
            root_item.setIcon(0, NewProject.cc_icon)
            for name in var.labels:
                item = QtWidgets.QTreeWidgetItem(root_item)
                item.setText(0, name)
        else:
            raise ValueError('var be one of [FCVariable, PCVariable, or CCVariable]')

        root_item.setText(0, f'{var.name} ({len(var)})')
    
    def repaint(self, curr=None):
        self.variableTree.clearSelection()
        if curr is not None:
            curr.setSelected(True)
        self.variableTree.repaint()

        self.addBtn.setEnabled(True)
        self.editBtn.setEnabled(curr is not None)
        self.deleteBtn.setEnabled(curr is not None)
        self.addBtn.repaint()
        self.editBtn.repaint()
        self.deleteBtn.repaint()

    def cancel(self):
        box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Cancel",
                "Are you sure you want to cancel? You will lose all of your changes!",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        reply = box.exec()

        if reply == QtWidgets.QMessageBox.Yes:
            self.dialog.reject()
        else:
            return

    def done(self):
        name = self.nameEditor.text()
        if not name:
            err = QtWidgets.QErrorMessage(self.dialog)
            err.showMessage('The experiment must have a name.')
            self.nameEditor.setFocus()
            return
        var_count = self.variableTree.topLevelItemCount()
        if var_count == 0:
            err = QtWidgets.QErrorMessage(self.dialog)
            err.showMessage('The experiment must contain at least one variable.')
            return
        batch_size = self.bsInput.value()
        self.expt = Experiment(name, batch_size, self.variables)

        box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Ready?",
                "Are you sure your experiment is set up correctly? These settings CANNOT be changed!",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        reply = box.exec()

        if reply == QtWidgets.QMessageBox.Yes:
            self.dialog.accept()
        else:
            return


if __name__ == "__main__":
    import sys
    from collections import OrderedDict

    app = QtWidgets.QApplication(sys.argv)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("../assets/tray.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    app.setWindowIcon(icon)

    Dialog = QtWidgets.QDialog()
    ui = NewProject()
    ui.setupUi(Dialog)

    Dialog.show()
    sys.exit(app.exec_())
