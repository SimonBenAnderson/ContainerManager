import maya.api.OpenMaya as om2
from util import node

def getObjectsContainers(mQueryObject = []):
    """
    Return a list of containers that the passed in objects reside in.

    @param [] mQueryObject: list of objects you are wanting to know, in which container they exists.
    @return: a dictionary, key = container name, value = container MObject.
    @rtype: {},
    """
    containerDict = {}
    nodeFn = om2.MFnContainerNode()
    selNodeFn = om2.MFnDependencyNode()
    selList = mQueryObject
    containerObjs = getAllDagContainers()

    for selObj in mQueryObject:
        for obj in containerObjs:
            nodeFn.setObject(obj)
            if selObj in nodeFn.getMembers():
                selNodeFn.setObject(selObj)
                containerName = str(nodeFn.name())

                # Adds the object to a dictionary, using the container as the key
                if containerDict.has_key(nodeFn.name()):
                    containerDict[containerName].append(selNodeFn.object())
                else:
                    containerDict[containerName] = [selNodeFn.object()]

    return containerDict


def getAllDagContainers():
    """
    Will return all containers in the scene

    @return: list of objects comprised of containers and DAGContainers
    @rtype: []
    """

    # Holds all the containers
    containerObjs = []
    # Search the root hierarchy for container types
    # Some containers live in the DAG while others ar DG Nodes
    dagIterator = om2.MItDag(om2.MItDag.kDepthFirst, om2.MFn.kDagContainer)
    dgIterator = om2.MItDependencyNodes(om2.MFn.kContainer)

    # TODO: Look at optomising by returning the allPaths, instead of looping
    #dagArray = om.MDagPathArray(dagIterator.getAllPaths())
    #return dagArray

    # Node helpers
    dagNodeFn = om2.MFnDagNode()
    dgNodeFn = om2.MFnDependencyNode()

    # Loop throught the DAG Graph (Scene)
    while (not dagIterator.isDone()):
        # get ths current dag node
        dag_mObject = dagIterator.currentItem()
        # updates dag function
        dagNodeFn.setObject(dag_mObject)
        containerObjs.append(dagNodeFn.object())
        # gets the next item
        dagIterator.next()

    # Loop through the Dependency Nodes
    while (not dgIterator.isDone()):
        dgNodeFn.setObject(dgIterator.thisNode())
        containerObjs.append(dgNodeFn.object())
        dgIterator.next()

    return containerObjs

def exposeSelection():
    """
    NOT IMPLEMENTED YET
    """
    #TODO: expose objects and parameters and look at creating input and output nodes
    pass

def unexposeSelection():
    """
    NOT IMPLEMENTED YET
    """
    pass

def concealExposedObject(mobj):
    """
    Hides the selected object, so it will no longer appear in the outliner when the container is black boxed
    @param mobj: Object you wish to remove from being exposed
    """
    mfnDepNode = om2.MFnDependencyNode(mobj)
    msgPlug = mfnDepNode.findPlug("message", True)

    for _plug in msgPlug.destinations():
        # selected object is not connected to anything
        if _plug.isNull:
            continue
        connectedNode = _plug.node()
        if connectedNode.apiType() == om2.MFn.kContainer:
            dgMod = om2.MDGModifier()
            dgMod.disconnect(msgPlug, _plug)
            dgMod.doIt()

def isContainerClosed(mobj):
    """
    returns true is the container is closed

    @param mobj: Container object
    @type mobj: MObject
    @return: True is container is cloased, False if open
    @rtype: Boolean
    """
    _mfnCont = om2.MFnContainerNode(mobj)
    bbPlug = _mfnCont.findPlug("blackBox", True)
    return bbPlug.asInt() == 1

def closeContainer(mobj):
    """
    Close the container passed in
    @param mobj: The container object, you wich to close
    @type mobj: om.MObject
    """
    _mfnCont = om2.MFnContainerNode(mobj)
    bbPlug = _mfnCont.findPlug("blackBox", True)
    bbPlug.setInt(1)

def openContainer(mobj):
    """
    open the container passed in
    @param mobj: The container object, you wich to open
    @type mobj: om.MObject
    """
    _mfnCont = om2.MFnContainerNode(mobj)
    bbPlug = _mfnCont.findPlug("blackBox", True)
    bbPlug.setInt(0)

def createContainer(name="unnamedContainer"):
    """
    Creates and names the container
    @param string name: The name of the container, that will be created
    @return: The newly created container
    @rtype: MObject
    """
    dgMod = om2.MDGModifier()
    containerObj = dgMod.createNode("container")
    dgMod.doIt()
    containerMfn = om2.MFnContainerNode(containerObj)
    containerMfn.setName(name)
    return containerObj

def deleteContainer(mobj):
    """
    Deletes the container, and removes the containers hypergraph
    @param mobj: Container that will be deleted
    """
    if not mobj:
        return False

    _hyperLayoutDG = getContainerHyperLayout(mobj, create=False)
    if _hyperLayoutDG:
        node.disconnectAllPlugsOnNode(_hyperLayoutDG)
        node.deleteNode(_hyperLayoutDG)
    node.deleteNode(mobj)

def getContainerHyperLayout(container, create=True):
    """
    Gets the hyperlayout that is connected to the container. If the container has not got one, and create is set to True,
    a hyperlayout will be created and joined to the container.

    @param MObject container: The container object that you want to return its hyperlayout.
    @return: The hyperlayout connected to the container
    @rtype: MObject
    """
    _dgContainer = om2.MFnDependencyNode(container)
    _hyperLPlug = _dgContainer.findPlug('hyperLayout', True)
    _hyperLayoutMo = None
    # check if container has a hyperlayout, is not creates one
    if not _hyperLPlug.isConnected and not _hyperLPlug.isDestination:
        if create:
            _dgMod = om2.MDGModifier()
            _hyperLayoutMo = _dgMod.createNode('hyperLayout')
            _dgMod.doIt()
            _hyperLayoutMfn = om2.MFnDependencyNode(_hyperLayoutMo)
            _hyperLayoutMfn.setName(_dgContainer.name() + "_hyperLayout")

            _dgMod.connect(_hyperLayoutMfn.findPlug("message", True), _hyperLPlug)
            _dgMod.doIt()
    else:
        _hyperLayoutMo = _hyperLPlug.source().node()

    return _hyperLayoutMo

def exposeDAGObject(mobj):
    """
    Exposes the object on the container it is connected to.
    @param om2.MObject mobj: DAG object you wish to expose in the container
    """
    print("Expose DAG Object Called")
    mfnDepNode = om2.MFnDependencyNode(mobj)
    msgPlug = mfnDepNode.findPlug("message",True)

    for _plug in msgPlug.destinations():
        # selected object is not connected to anything
        if _plug.isNull:
            continue
        connectedNode = _plug.node()
        if connectedNode.apiType() == om2.MFn.kHyperLayout:
            print(connectedNode, " is hyperlayout type")
            hyperLayoutDN = om2.MFnDependencyNode(connectedNode)
            hlMsgPlug = hyperLayoutDN.findPlug("message", True)
            # selected object is not connected to anything
            if hlMsgPlug.isNull:
                continue
            # TODO: Need to implement this still
            for _plugDest in hlMsgPlug.destinations():
                contNode = _plugDest.node()
                if contNode.apiType() == om2.MFn.kContainer:
                    contMfn = om2.MFnDependencyNode(contNode)
                    publishNodePlug = contMfn.findPlug("publishedNodeInfo", True)
                    availablePlug = node.getNextAvailablePlugInPlug(publishNodePlug, "publishedNode")
                    if availablePlug is None:
                        print("Error: Could not expose selection")
                        return False
                    print("RETURNED : {0}".format(availablePlug.name()))
                    dgMod = om2.MDGModifier()
                    dgMod.connect(msgPlug, availablePlug)
                    dgMod.doIt()

def addToContainer(mobj, containerObj):
    """
    Add an object to a container.
    @param mobj: Object you wish to add to the container
    @param om2.MObject containerObj: container that have the object added to it
    """
    _hyperLayoutDG = getContainerHyperLayout(containerObj)
    _hyperLayoutMfn = om2.MFnDependencyNode(_hyperLayoutDG)
    _hyperLayoutMessagePlug = _hyperLayoutMfn.findPlug('hyperPosition', True)
    _nextPlugIndex = _hyperLayoutMessagePlug.numElements()

    _dagMod = om2.MDGModifier()
    _mfnNode = om2.MFnDependencyNode()

    _hyperposPlug = _hyperLayoutMessagePlug.elementByLogicalIndex(_nextPlugIndex)
    _availableDependNodePlug = node.getNextAvailablePlugInPlug(_hyperposPlug, 'dependNode')
    print("NEXT AVAILABLE dependNode : {0}".format(_availableDependNodePlug))

    _mfnNode.setObject(mobj)
    _msgPlug = _mfnNode.findPlug('message', True)
    _badConnection = node.isSourceConnectedTo(_msgPlug, nodeType='hyperLayout')
    # TODO: check if you are trying to add the object to the container it is already added to
    if _availableDependNodePlug and not _badConnection:
        _dagMod.connect(_msgPlug, _availableDependNodePlug)
        _dagMod.doIt()
        _nextPlugIndex += 1
    else:
        print("ERROR: Object not added to container!")


def removeFromContainer(mobj, containerObj):
    pass