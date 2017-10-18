import maya.api.OpenMaya as om2
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2 import __version__
    from shiboken2 import wrapInstance
except ImportError:
    from PySide.QtCore import *
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide import __version__
    from shiboken import wrapInstance

# custom maya util
from util import node
import container

# reload while developing
reload(container)
reload(node)


class SELECTION_TYPE(object):
    """
    Selection constants
    """
    DependNode = 1
    Component = 2
    DagPath = 3
    Plug = 4
    Strings = 5


class ContainerManager(MayaQWidgetDockableMixin, QWidget):
    # Holds all the containers in a dictionary
    containerDictionary = {}

    def __init__(self, parent=None):
        super(ContainerManager, self).__init__(parent=parent)
        #self.setText('Push Me')
        self.setWindowTitle('Container Manager')
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred )

        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        self.setMinimumWidth(300)
        self.setMinimumHeight(200)

        self.resize(QSize(500,300))

        # Create Qt Objects
        self.addContainerBtn = QPushButton("Create Container")
        self.removeContainerBtn = QPushButton("Delete Container")
        self.putinContainerBtn = QPushButton("Add to container")
        self.removeFromContainerBtn = QPushButton("Remove from container")
        self.refreshBtn = QPushButton("refresh")
        self.showContainerBtn = QPushButton("Is Selected Object in Container")
        self.containerList = QListWidget()
        self.exposeBtn = QPushButton("expose Selected")
        self.unexposeBtn = QPushButton("unexpose Selected")
        self.toggleContainer = QPushButton("close/open Container")
        # TODO: implement toggle of container
        # TODO: implement exposure/hide object/parameter selection

        # Custom styling
        # TODO: Need to make the refreshh button stay as a square

        # Event connection
        self.addContainerBtn.clicked.connect(self.createContainer)
        self.removeContainerBtn.clicked.connect(self.removeContainer)
        self.putinContainerBtn.clicked.connect(self.addToContainer)
        self.removeFromContainerBtn.clicked.connect(self.removeFromContainer)
        self.refreshBtn.clicked.connect(self.refreshContainerList)
        self.showContainerBtn.clicked.connect(self.showContainerFromSelection)
        self.exposeBtn.clicked.connect(self.exposeDAGObject)
        self.unexposeBtn.clicked.connect(self.hideExposedDagObject)
        self.toggleContainer.clicked.connect(self.toggleCloseContainer)

        # Layouts
        self.layout = QHBoxLayout()
        self.layoutV = QVBoxLayout()
        self.lytHBlackBox = QHBoxLayout()

        # Add to layouts
        self.layout.addWidget(self.addContainerBtn)
        self.layout.addWidget(self.removeContainerBtn)
        self.layout.addWidget(self.putinContainerBtn)
        self.layout.addWidget(self.removeFromContainerBtn)
        self.layoutV.addWidget(self.refreshBtn)
        self.layoutV.addWidget(self.showContainerBtn)
        self.layoutV.addWidget(self.containerList)

        self.lytHBlackBox.addWidget(self.exposeBtn)
        self.lytHBlackBox.addWidget(self.unexposeBtn)
        self.lytHBlackBox.addWidget(self.toggleContainer)

        self.layoutV.addLayout(self.layout)
        self.layoutV.addLayout(self.lytHBlackBox)
        self.setLayout(self.layoutV)

        self.refreshContainerList()


    # TODO: if object is not attached to container then attach and expose
    def exposeDAGObject(self):
        """
        Exposes the object on the container it is already connected to
        """
        for selObj in self.pythonicSelection():
            container.exposeDagObject(selObj)

    def hideExposedDagObject(self):
        for selObj in self.pythonicSelection():
            container.concealExposedObject(selObj)

    def toggleCloseContainer(self):
        for _container in self.getContainerFromUISelection():
            if container.isContainerClosed(_container):
                container.openContainer(_container)
            else:
                container.closeContainer(_container)

    def getContainerFromUISelection(self):
        _selectedContainers = []
        for item in self.containerList.selectedItems():
            _selectedContainers.append(self.containerDictionary[item.text()])
        return _selectedContainers

    def createContainer(self):
        # TODO: Add name input dialog
        containerObj = container.createContainer()
        containerMfn = om2.MFnContainerNode(containerObj)
        containerName = containerMfn.name()
        # Add to dictionary, for easy interaction
        self.containerDictionary[containerName] = containerObj
        # Add container to ui
        self.containerList.addItems([containerName])
        self.containerList.sortItems()

    def removeContainer(self):
        """
        Removes all the selected containers from the maya scene
        """
        for item in self.containerList.selectedItems():
            containerName = item.text()
            containerObj = self.containerDictionary[containerName]
            # remove container from dictionary
            del (self.containerDictionary[containerName])
            self.containerDictionary.pop(containerName, None)
            container.deleteContainer(containerObj)
            # remove ui entry
            _rowIndex = self.containerList.row(item)
            self.containerList.takeItem(_rowIndex)

    def removeFromContainer(self):
        _containerName = self.containerList.currentItem().text()
        _containerMo = self.containerDictionary[_containerName]

        _hyperLayoutDG = container.getContainerHyperLayout(_containerMo)
        _hyperLayoutMfn = om2.MFnDependencyNode(_hyperLayoutDG)

        _dagMod = om2.MDGModifier()
        _mfnNode = om2.MFnDependencyNode()
        for dn in self.pythonicSelection(SELECTION_TYPE.DependNode):
            _mfnNode.setObject(dn)
            _msgPlug = _mfnNode.findPlug('message', True)
            for _destPlug in _msgPlug.destinations():
                if om2.MFnDependencyNode(_destPlug.node()).namespace == _hyperLayoutMfn.namespace:
                    _dagMod.disconnect(_msgPlug, _destPlug)
                    _dagMod.doIt()

    def addToContainer(self):
        if len(self.containerList.selectedItems()) != 1:
            print("ERROR: Please Select one container")
            return False

        _containerName = self.containerList.currentItem().text()
        _containerMo = self.containerDictionary[_containerName]

        for dn in self.pythonicSelection(SELECTION_TYPE.DependNode):
            container.addToContainer(dn, _containerMo)

    def refreshContainerList(self):
        self.containerList.clear()
        self.containerDictionary = {}
        containerFn = om2.MFnContainerNode()
        containerList = container.getAllDagContainers()
        containerNames = [str(containerFn.setObject(a).name()) for a in containerList]

        for containerObject in containerList:
            containerFn.setObject(containerObject)
            self.containerDictionary[containerFn.name()] = containerObject

        self.containerList.addItems(containerNames)
        self.containerList.sortItems()

    def showContainerFromSelection(self):
        mObjects = self.pythonicSelection()
        containerDict = container.getObjectsContainers(mObjects)
        # Clear selection
        self.containerList.clearSelection()
        # Multi Selection Activated
        self.containerList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # Selects the items
        for name in containerDict.keys():
            items = self.containerList.findItems(name, Qt.MatchExactly)
            for item in items:
                item.setSelected(True)

    def pythonicSelection(self, filterType=SELECTION_TYPE.DependNode):
        """
        Returns a list of the objects selected, This may cause a small slowdown, but was implemented to keep code 'Pythonic'

        Note: This is meant to be used by users for external use and not to be used inside of this API, as we want the API
        to be as fast as possible.

        @param returnType: The type of object you want returned from selection list
        @return: of selected Objects
        @rtype: []
        """
        pyList = []
        selList = om2.MGlobal.getActiveSelectionList()
        selIter = om2.MItSelectionList(selList)

        while (not selIter.isDone()):
            if filterType == SELECTION_TYPE.DagPath:
                pyList.append(selIter.getDagPath())
            elif filterType == SELECTION_TYPE.Component:
                pyList.append(selIter.getComponent())
            elif filterType == SELECTION_TYPE.DependNode:
                pyList.append(selIter.getDependNode())
            elif filterType == SELECTION_TYPE.Plug:
                pyList.append(selIter.getPlug())
            elif filterType == SELECTION_TYPE.Strings:
                pyList.append(selIter.getStrings())

            selIter.next()
        return pyList

def CreateContainerManager():
    containerManager = ContainerManager()
    containerManager.show(dockable=True)
