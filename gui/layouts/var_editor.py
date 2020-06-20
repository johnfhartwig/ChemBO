from collections import OrderedDict
import re

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from .utils import *

PC_RE = re.compile('(.+) \(\d+\)')

class VarEditor(object):
    def __init__(self, var=None):
        if var is None:
            self.variable = None
            self.type = 0
        else:
            self.variable = var
            if isinstance(var, FCVariable):
                self.type = 0
            elif isinstance(var, PCVariable):
                self.type = 1
            elif isinstance(var, CCVariable):
                self.type = 2

    def setupUi(self, Dialog):
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(16)

        self.dialog = Dialog

        Dialog.setObjectName("Dialog")
        Dialog.resize(600, 480)
        Dialog.setMinimumSize(QtCore.QSize(600, 480))
        Dialog.setMaximumSize(QtCore.QSize(600, 480))
        Dialog.setSizeIncrement(QtCore.QSize(0, 0))
        Dialog.setWindowTitle("New variable...")

        self.centralwidget = QtWidgets.QWidget(Dialog)
        self.centralwidget.setObjectName("centralwidget")

        self.nameLabel = QtWidgets.QLabel(self.centralwidget)
        self.nameLabel.setGeometry(QtCore.QRect(10, 15, 125, 20))
        self.nameLabel.setFont(font)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Variable Name:")
        self.nameEditor = QtWidgets.QLineEdit(self.centralwidget)
        self.nameEditor.setGeometry(QtCore.QRect(140, 10, 450, 30))
        self.nameEditor.setFont(font)
        self.nameEditor.setObjectName("nameEditor")

        self.doneBtn = QtWidgets.QPushButton(self.centralwidget)
        self.doneBtn.setGeometry(QtCore.QRect(470, 450, 120, 30))
        self.doneBtn.setFont(font)
        self.doneBtn.setObjectName("doneBtn")
        self.doneBtn.setText("Done!")
        self.doneBtn.clicked.connect(lambda: self.submit())
        self.cancelBtn = QtWidgets.QPushButton(self.centralwidget)
        self.cancelBtn.setGeometry(QtCore.QRect(360, 450, 120, 30))
        self.cancelBtn.setFont(font)
        self.cancelBtn.setObjectName("cancelBtn")
        self.cancelBtn.setText("Cancel")
        self.cancelBtn.clicked.connect(lambda: self.cancel())

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 50, 600, 400))
        self.tabWidget.setObjectName("tabWidget")
        self.fc_tab = QtWidgets.QWidget()
        self.fc_tab.setObjectName("fc_tab")

        self.fc_list = QtWidgets.QListWidget(self.fc_tab)
        self.fc_list.setGeometry(QtCore.QRect(25, 10, 550, 300))
        self.fc_list.setFont(font)
        self.fc_list.setDragEnabled(True)
        self.fc_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.fc_list.setMovement(QtWidgets.QListView.Snap)
        self.fc_list.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked | QtWidgets.QAbstractItemView.AnyKeyPressed)
        self.fc_list.setObjectName("fc_list")

        self.fc_new = QtWidgets.QPushButton(self.fc_tab)
        self.fc_new.setGeometry(QtCore.QRect(20, 310, 150, 35))
        self.fc_new.setFont(font)
        self.fc_new.setObjectName("fc_new")
        self.fc_new.setText("New value")
        self.fc_new.clicked.connect(lambda: self.fcNewValue())

        self.fc_del = QtWidgets.QPushButton(self.fc_tab)
        self.fc_del.setGeometry(QtCore.QRect(20, 335, 150, 35))
        self.fc_del.setFont(font)
        self.fc_del.setObjectName("fc_del")
        self.fc_del.setText("Remove value")
        self.fc_del.setEnabled(False)
        self.fc_del.clicked.connect(lambda: self.fcDelValue())

        self.fc_list.currentItemChanged.connect(lambda curr, _: self.fcSelection(curr))

        self.tabWidget.addTab(self.fc_tab, "")

        self.pc_tab = QtWidgets.QWidget()
        self.pc_tab.setObjectName("pc_tab")

        self.pc_tree = QtWidgets.QTreeWidget(self.pc_tab)
        self.pc_tree.setGeometry(QtCore.QRect(25, 10, 550, 300))
        self.pc_tree.setFont(font)
        self.pc_tree.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.pc_tree.setUniformRowHeights(True)
        self.pc_tree.setAnimated(True)
        self.pc_tree.setHeaderHidden(True)
        self.pc_tree.setObjectName("pc_tree")
        self.pc_tree.headerItem().setText(0, "Name")
        self.pc_tree.currentItemChanged.connect(lambda curr, prev: self.pcRepaint(curr, prev))

        self.pc_newgrp = QtWidgets.QPushButton(self.pc_tab)
        self.pc_newgrp.setGeometry(QtCore.QRect(20, 310, 150, 35))
        self.pc_newgrp.setFont(font)
        self.pc_newgrp.setObjectName("pc_newgrp")
        self.pc_newgrp.setText("New group")
        self.pc_newgrp.clicked.connect(lambda: self.pcNewGroup())

        self.pc_delgrp = QtWidgets.QPushButton(self.pc_tab)
        self.pc_delgrp.setGeometry(QtCore.QRect(20, 335, 150, 35))
        self.pc_delgrp.setFont(font)
        self.pc_delgrp.setObjectName("pc_delgrp")
        self.pc_delgrp.setText("Remove group")
        self.pc_delgrp.setEnabled(False)
        self.pc_delgrp.clicked.connect(lambda: self.pcDelGroup())

        self.pc_newval = QtWidgets.QPushButton(self.pc_tab)
        self.pc_newval.setGeometry(QtCore.QRect(175, 310, 150, 35))
        self.pc_newval.setFont(font)
        self.pc_newval.setObjectName("pc_newval")
        self.pc_newval.setText("New value")
        self.pc_newval.setEnabled(False)
        self.pc_newval.clicked.connect(lambda: self.pcNewValue())

        self.pc_delval = QtWidgets.QPushButton(self.pc_tab)
        self.pc_delval.setGeometry(QtCore.QRect(175, 335, 150, 35))
        self.pc_delval.setFont(font)
        self.pc_delval.setObjectName("pc_delval")
        self.pc_delval.setText("Remove value")
        self.pc_delval.setEnabled(False)
        self.pc_delval.clicked.connect(lambda: self.pcDelValue())

        self.tabWidget.addTab(self.pc_tab, "")

        self.cc_tab = QtWidgets.QWidget()
        self.cc_tab.setObjectName("cc_tab")
        self.cc_adjLabel = QtWidgets.QLabel(self.cc_tab)
        self.cc_adjLabel.setGeometry(QtCore.QRect(10, 10, 200, 30))
        self.cc_adjLabel.setFont(font)
        self.cc_adjLabel.setObjectName("cc_adjLabel")
        self.cc_adjLabel.setText("Adjacency matrix path:")

        self.cc_browse = QtWidgets.QPushButton(self.cc_tab)
        self.cc_browse.setGeometry(QtCore.QRect(200, 10, 100, 35))
        self.cc_browse.setFont(font)
        self.cc_browse.setObjectName("cc_browse")
        self.cc_browse.setText("Browse...")
        self.cc_browse.clicked.connect(lambda: self.ccBrowse())

        self.cc_fileLabel = QtWidgets.QLabel(self.cc_tab)
        self.cc_fileLabel.setGeometry(QtCore.QRect(300, 10, 300, 30))
        self.cc_fileLabel.setFont(font)
        self.cc_fileLabel.setObjectName("cc_fileLabel")

        self.cc_namesLabel = QtWidgets.QLabel(self.cc_tab)
        self.cc_namesLabel.setGeometry(QtCore.QRect(10, 40, 200, 30))
        self.cc_namesLabel.setFont(font)
        self.cc_namesLabel.setObjectName("cc_namesLabel")
        self.cc_namesLabel.setText("Names:")
        self.cc_nameList = QtWidgets.QListWidget(self.cc_tab)
        self.cc_nameList.setGeometry(QtCore.QRect(25, 70, 550, 290))
        self.cc_nameList.setFont(font)
        self.cc_nameList.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.cc_nameList.setDragEnabled(True)
        self.cc_nameList.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.cc_nameList.setMovement(QtWidgets.QListView.Snap)
        self.cc_nameList.setObjectName("cc_nameList")
        self.adj_matrix = None
        self.path = None

        self.tabWidget.addTab(self.cc_tab, "")

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.fc_tab), "Fully Connected")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.pc_tab), "Partially Connected")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.cc_tab), "Custom Connected")

        if self.variable is not None:
            self.loadVariable(self.variable)
        self.tabWidget.setCurrentIndex(self.type)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.variable = None

    def fcSelection(self, curr):
        if curr is None:
            self.fc_del.setEnabled(False)
        else:
            self.fc_del.setEnabled(True)
        self.fc_new.setEnabled(True)
        self.fc_new.repaint()
        self.fc_del.repaint()

    def fcNewValue(self):
        item = QtWidgets.QListWidgetItem("new value (double-click to edit)")
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self.fc_list.addItem(item)
        self.fc_list.clearSelection()
        item.setSelected(True)
        if self.fc_list.state() == self.fc_list.State.EditingState:
            self.fc_list.setState(self.fc_list.State.NoState)
        self.fc_list.editItem(item)
        self.fc_list.repaint()

    def fcDelValue(self):
        if len(self.fc_list.selectedIndexes()) == 0:
            return
        idx = self.fc_list.selectedIndexes()[0]
        self.fc_list.takeItem(idx.row())

    def pcRepaint(self, curr=None, prev=None):
        # Repaint the tree itself
        self.pc_tree.clearSelection()
        if curr is not None:
            curr.setSelected(True)
        self.pc_tree.repaint()

        # Chec prev to see if user clicked away from editing a group name.
        if prev is not None and prev.parent() is None:
            match = PC_RE.findall(prev.text(0))
            if len(match) == 0:
                prev.setText(0, f"{prev.text(0)} ({prev.childCount()})")

        # Change buttons based on curr
        if self.pc_tree.state() == self.pc_tree.State.EditingState:
            self.pc_newgrp.setEnabled(False)
            self.pc_delgrp.setEnabled(False)
            self.pc_newval.setEnabled(False)
            self.pc_delval.setEnabled(False)
        elif curr is None:  # No current selection
            self.pc_newgrp.setEnabled(True)
            self.pc_delgrp.setEnabled(False)
            self.pc_newval.setEnabled(False)
            self.pc_delval.setEnabled(False)
        elif curr.parent() is None:  # Current selection is a group
            match = PC_RE.findall(curr.text(0))
            if len(match) == 0:
                curr.setText(0, f"{curr.text(0)} ({curr.childCount()})")

            self.pc_newgrp.setEnabled(True)
            self.pc_delgrp.setEnabled(True)
            self.pc_newval.setEnabled(True)
            self.pc_delval.setEnabled(False)
        else:  # Current selection is a value
            self.pc_newgrp.setEnabled(True)
            self.pc_delgrp.setEnabled(False)
            self.pc_newval.setEnabled(True)
            self.pc_delval.setEnabled(curr.parent().childCount() > 1)

        self.pc_newgrp.repaint()
        self.pc_delgrp.repaint()
        self.pc_newval.repaint()
        self.pc_delval.repaint()

    def pcNewGroup(self):
        group = QtWidgets.QTreeWidgetItem(self.pc_tree)
        group.setText(0, "new group (double-click to edit) (1)")
        group.setFlags(group.flags() | QtCore.Qt.ItemIsEditable)
        group.setExpanded(True)
        if self.pc_tree.state() == self.pc_tree.State.EditingState:
            self.pc_tree.setState(self.pc_tree.State.NoState)
        self.pc_tree.editItem(group)
        item = QtWidgets.QTreeWidgetItem(group)
        item.setText(0, "new value (double-click to edit)")
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self.pcRepaint(group)

    def pcDelGroup(self):
        idx = self.pc_tree.selectedIndexes()[0]
        group = self.pc_tree.itemFromIndex(idx)
        if group.parent() is not None:
            return
        self.pc_tree.takeTopLevelItem(idx.row())
        self.pcRepaint()

    def pcNewValue(self):
        group = self.pc_tree.selectedItems()[0]
        if group.parent() is not None:
            group = group.parent()
        group_name = group.text(0)
        match = PC_RE.findall(group_name)
        if match:
            group_name = match[0]
        item = QtWidgets.QTreeWidgetItem(group)
        group.setText(0, f"{group_name} ({group.childCount()})")
        item.setText(0, "new value (double-click to edit)")
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self.pcRepaint(item, None)
        if self.pc_tree.state() == self.pc_tree.State.EditingState:
            self.pc_tree.setState(self.pc_tree.State.NoState)
        self.pc_tree.editItem(item)
        
    def pcDelValue(self):
        item = self.pc_tree.selectedItems()[0]
        group = item.parent()
        if group is None:
            return
        idx = group.indexOfChild(item)
        group.takeChild(idx)
        group_name = PC_RE.findall(group.text(0))[0]
        group.setText(0, f"{group_name} ({group.childCount()})")
        self.pcRepaint()

    def ccBrowse(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', '~', "Numpy array files (*.npy)")[0]
        if not fname:
            return

        try:
            arr = np.load(fname, allow_pickle=True)
        except ValueError or OSError:
            err = QtWidgets.QErrorMessage(self.dialog)
            err.showMessage(f'Could not read {fname}. Please check that it is a Numpy array saved in the npy file format.')
            return
        if len(arr.shape) != 2 or arr.shape[0] != arr.shape[1] or (arr != arr.T).any():
            err = QtWidgets.QErrorMessage(self.dialog)
            err.showMessage(f'{fname} must contain a 2-D symmetric array.')
            return

        self.path = fname
        if len(fname.split('/')) > 1:
            self.cc_fileLabel.setText(fname.split('/')[-1])
        else:
            self.cc_fileLabel.setText(fname.split('\\')[-1])
        
        for i in range(arr.shape[0]):
            item = QtWidgets.QListWidgetItem(f"Item {i} (double-click to edit)")
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            self.cc_nameList.addItem(item)

        self.adj_matrix = arr
            
    def loadVariable(self, var):
        self.nameEditor.setText(var.name)
        if isinstance(var, FCVariable):
            for name in var.values:
                item = QtWidgets.QListWidgetItem(name)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
                self.fc_list.addItem(item)
        elif isinstance(var, PCVariable):
            for group, names in var.groups.items():
                group_item = QtWidgets.QTreeWidgetItem(self.pc_tree)
                group_item.setText(0, f"{group} ({len(names)})")
                group_item.setFlags(group_item.flags() | QtCore.Qt.ItemIsEditable)
                group_item.setExpanded(True)
                for name in names:
                    item = QtWidgets.QTreeWidgetItem(group_item)
                    item.setText(0, name)
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        elif isinstance(var, CCVariable):
            if var.path is not None:
                self.cc_fileLabel.setText(var.path)
            for name in var.labels:
                item = QtWidgets.QListWidgetItem(name)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
                self.cc_nameList.addItem(item)
            self.adj_matrix = var.adj_matrix

    def cancel(self):
        box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Cancel",
                "Are you sure you want to cancel? You will lose all of your changes!",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        reply = box.exec()

        if reply == QtWidgets.QMessageBox.Yes:
            self.dialog.reject()
        else:
            return

    def submit(self):
        name = self.nameEditor.text()
        if not name:
            err = QtWidgets.QErrorMessage(self.dialog)
            err.showMessage('The variable must have a name.')
            self.nameEditor.setFocus()
            return
        tab_idx = self.tabWidget.currentIndex()
        if tab_idx == self.tabWidget.indexOf(self.fc_tab):
            count = self.fc_list.count()
            if count == 0:
                err = QtWidgets.QErrorMessage(self.dialog)
                err.showMessage('The fully connected variable must contain values.')
                return
            values = [self.fc_list.item(i).text() for i in range(count)]
            self.variable = FCVariable(name, values)
            self.dialog.accept()
        elif tab_idx == self.tabWidget.indexOf(self.pc_tab):
            group_count = self.pc_tree.topLevelItemCount()
            if group_count == 0:
                err = QtWidgets.QErrorMessage(self.dialog)
                err.showMessage('The partially connected variable must contain groups.')
                return
            groups = OrderedDict()
            for group_idx in range(group_count):
                group = self.pc_tree.topLevelItem(group_idx) 
                value_count = group.childCount()
                if value_count == 0:
                    err = QtWidgets.QErrorMessage(self.dialog)
                    err.showMessage('Every group must contain at least one item.')
                    return
                group_name = group.text(0)
                match = PC_RE.findall(group_name)
                if match:
                    group_name = match[0]
                
                groups[group_name] = []
                for i in range(value_count):
                    groups[group_name].append(group.child(i).text(0))
            self.variable = PCVariable(name, groups)
            self.dialog.accept()
        elif tab_idx == self.tabWidget.indexOf(self.cc_tab):
            if self.adj_matrix is None:
                err = QtWidgets.QErrorMessage(self.dialog)
                err.showMessage('The custom connected variable must include an adjacency matrix.')
                return
            labels = [self.cc_nameList.item(i).text() for i in range(self.cc_nameList.count())]
            path = self.cc_fileLabel.text()
            path = path if path else None
            self.variable = CCVariable(name, labels, self.adj_matrix, path)
            self.dialog.accept()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = VarEditor()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

