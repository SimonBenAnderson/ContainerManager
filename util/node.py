import maya.api.OpenMaya as om2

def createDGNode(name, nodeType):
    """
    NOT IMPLEMENTED
    @param name:
    @param nodeType:
    @return:
    @rtype:
    """
    pass

def connectDGNode(NodeFrom, fromPort, NodeTo, toPort):
    """
    NOT IMPLEMENTED
    @param NodeFrom:
    @param fromPort:
    @param NodeTo:
    @param toPort:
    @return:
    """
    pass

def getNextAvailablePlug(Node, plugName):
    """
    NOT IMPLEMENTED

    Iteratively search for a plug name in a node, and return the next available plug
    :param Node:
    :param plugName:
    :return:
    """
    pass

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
    _plugName = plug.name().split('.')[-1]
    if _plugName == childPlugName:
        return plug

    if plug.isArray:
        # for i in xrange(plug.numElements()):
        for i in xrange(plug.evaluateNumElements()):
            tempP = plug.elementByPhysicalIndex(i)
            if not tempP.isConnected:
                plugResult = getNextAvailablePlugInPlug(tempP, childPlugName)
                if plugResult:
                    _plugName = plugResult.name().split('.')[-1]
                    if _plugName == childPlugName:
                        return plugResult

        # if all plugs are occupied, then access the next plug in the array
        nextPlugIndex = plug.evaluateNumElements()+1
        plugResult = getNextAvailablePlugInPlug(plug.elementByLogicalIndex(nextPlugIndex), childPlugName)
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
    return None


def isSourceConnectedTo(plug, nodeType=None, nodeName=None):
    """
    Check to see if the port is connected to any specific node types or node name
    @param nodeType:
    @type nodeType: maya node type name
    @param nodeName:

    @return: True - match found, False no match found
    @rtype: boolean
    """
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
