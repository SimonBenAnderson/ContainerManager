import maya.api.OpenMaya as om2

def createDGNode(name, nodeType):
    """

    @param name:
    @param nodeType:
    @return:
    @rtype:
    """
    pass

def connectDGNode(NodeFrom, fromPort, NodeTo, toPort):
    """

    @param NodeFrom:
    @param fromPort:
    @param NodeTo:
    @param toPort:
    @return:
    """

def getNextAvailablePlug(Node, plugName):
    """
    Iteratively search for a plug name in a node, and return the next available plug

    :param Node:
    :param plugName:
    :return:
    """

def deleteNode(node):
    """
    Delete the node that is passed in
    @param node:
    """
    _dgMod = om2.MDGModifier()
    _dgMod.deleteNode(node)
    _dgMod.doIt()

def disconnectAllPlugsOnNode(mobj):
    """
    Disconnects all connected plugs
    @param mobj: Dependency Node you wish to have all its plugs disconnected
    """
    _dgMod = om2.MDGModifier()
    _depNode = om2.MFnDependencyNode(mobj)
    for connPlug in _depNode.getConnections():
        if connPlug.isSource:
            for destPlug in connPlug.destinations():
                _dgMod.disconnect(connPlug, destPlug)
        else:
            _dgMod.disconnect(connPlug.source(), connPlug)
        _dgMod.doIt()

def getNextAvailablePlugInPlug(plug, childPlugName):
    """
    Searches through a compound or array plug for an open plug that has the specified name

    @param om2.MPlug plug: plug that we will be searching through
    @param basestring childPlugName: name of child plug, that will be looked for

    @return: the plug found
    @rtype: MPlug
    """
    returnPlug = plug
    availablePlug = None
    _plugName = plug.name().split('.')[-1]
    if _plugName == childPlugName:
        return plug

    if plug.isArray:
        i=0
        # for i in xrange(plug.numElements()):
        for i in xrange(plug.evaluateNumElements()):
            tempP = plug.elementByPhysicalIndex(i)
            if not tempP.isConnected:
                plugResult = getNextAvailablePlugInPlug(tempP, childPlugName)
                if plugResult:
                    _plugName = plugResult.name().split('.')[-1]
                    if _plugName == childPlugName:
                        return plugResult

        print(i, i+1)
        print(plug.evaluateNumElements(), plug.isArray)

        if i == plug.evaluateNumElements() and plug.isArray:
            print(childPlugName, plug.elementByLogicalIndex(i+1))
            plugResult = getNextAvailablePlugInPlug(plug.elementByLogicalIndex(i+1), childPlugName)
            return plugResult

    elif plug.isCompound:
        for i in xrange(plug.numChildren()):
            tempP = plug.child(i)
            if not tempP.isConnected:
                _plugName = tempP.name().split('.')[-1]
                # ugly work around, as the compound was returning a child of a virtual plug.
                # The childs parent had an index of -1
                if (tempP.parent().logicalIndex() > -1): # can try use isNetwork instead
                    plugResult = getNextAvailablePlugInPlug(tempP, childPlugName)
                    if plugResult:
                        _plugName = plugResult.name().split('.')[-1]
                        if _plugName == childPlugName:
                            return plugResult
    # return None


def isSourceConnectedTo(plug, nodeType=None, nodeName=None):
    """
    Check to see if the port is connected to any specific node types or node name
    :param node:
    @param nodeType:
    @type nodeType: maya node type name
    @param nodeName:

    @return: True - match found, False no match found
    @rtype: boolean
    """
    # TODO: ERROR: When selecting multiple objected/controls, multiple hypergraph get created, instead of aadding them all to the one hypergraph
    # TODO: TEST THIS
    if plug.isSource and plug.isConnected:

        for destPlug in plug.destinations():
            if nodeName:
                if nodeName in destPlug.name():
                    return True

            if nodeType:
                node = destPlug.node()
                nodeMfn = om2.MFnDependencyNode(node)
                if nodeMfn.typeName == nodeType:
                    return True
    return False
# TODO: Make this more generic method