"""
DMXExport

Automates the process of exporting and sending an FBX to Valve's FBX2DMX tool.

Created by @SediSocks
"""
import os
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import subprocess
import re

def createUI():
    #Window and tab layout
    window0 = pm.window(title="DMX Export")
    rowColumnLayout0 = pm.rowColumnLayout()
    tabs = cmds.tabLayout(p=rowColumnLayout0)
    exportTab = pm.columnLayout(p=tabs)
    settingsTab = pm.columnLayout(p=tabs)
    cmds.tabLayout( tabs, edit=True, tabLabel=((exportTab, 'Export'), (settingsTab, 'Settings')) )

    #DMX path row
    DMXFolderSpacer = pm.text(label="", h=8, p=exportTab, align="left")
    dmxFilePathRow = pm.rowLayout(nc=2, p=exportTab, h=30)
    def dmxPathBrowse():
        basicFilter = "*.fbx"
        dmxPath = cmds.fileDialog2(fm=0, ff=basicFilter, dialogStyle=2)
        dmxFilePath = cmds.textField("dmxFilePath", edit=True, text=str(dmxPath[0]))
        cmds.optionVar( sv=('dmxdmxFilePath', str(dmxPath[0])) )
        return dmxFilePath

    dmxFilePath = dmxPathBrowse
    if cmds.optionVar( exists='dmxdmxFilePath' ):
        dmxFilePath = cmds.optionVar( q='dmxdmxFilePath' )
        qcFilePathField = pm.textField("dmxFilePath", w=270, p=dmxFilePathRow, text=dmxFilePath)
    else:
        qcFilePathField = pm.textField("dmxFilePath", w=270, p=dmxFilePathRow)
    dmxPathIcon = pm.iconTextButton(style="iconAndTextVertical", image1="openLoadGeneric.png", w=30, h=30, p=dmxFilePathRow, c=dmxPathBrowse)

    #Export button row
    def selectedFunc(exportAllVar):
        exportAllVar = 0
        fbx2dmxFunc()

    def allFunc(exportAllVar):
        exportAllVar = 1
        fbx2dmxFunc()

    exportRow = pm.rowLayout(nc=2, p=exportTab, h=50)
    exportSelectedBox = pm.button("exportSelectedBox", label="Export Selected", w=150, h=50, p=exportRow, c=selectedFunc)
    exportallButton = pm.button("exportallButton", label="Export All", w=150, h=50, p=exportRow, c=allFunc)

    #Checkboxes
    checkboxRow = pm.rowLayout(nc=3, p=exportTab, h=30)
    triangulateBox = pm.checkBox("triangulateBox", label="Triangulate", p=checkboxRow, w=100)
    animationBox = pm.checkBox("animationBox", label="Animation", p=checkboxRow, w=100)
    compileBox = pm.checkBox("compileBox", label="Compile QC", p=checkboxRow, w=100)

    #QC Row
    qcRow = pm.rowLayout(nc=3, p=exportTab, h=50)
    qcFolderText = pm.text(label="QC path  ", p=qcRow, align="left")
    def qcPathBrowse():
        basicFilter = "*.qc"
        qcPath = cmds.fileDialog2(fm=1, ff=basicFilter, dialogStyle=2)
        qcFilePath = cmds.textField("qcFilePath", edit=True, text=str(qcPath[0]))
        cmds.optionVar( sv=('dmxqcFilePath', str(qcPath[0])) )
        return qcFilePath

    qcFilePath = qcPathBrowse
    if cmds.optionVar( exists='dmxqcFilePath' ):
        qcFilePath = cmds.optionVar( q='dmxqcFilePath' )
        qcFilePathField = pm.textField("qcFilePath", w=220, p=qcRow, text=qcFilePath)
    else:
        qcFilePathField = pm.textField("qcFilePath", w=220, p=qcRow)

    qcPathIcon = pm.iconTextButton(style="iconAndTextVertical", image1="openLoadGeneric.png", w=30, h=30, p=qcRow, c=qcPathBrowse)

    #HlMV Row
    hlmvRow = pm.rowLayout(nc=2, p=exportTab, h=35)
    hlmvButton = pm.button(label="Open in HLMV", w=150, h=35, p=hlmvRow, c=hlmvFunc)
    compileButton = pm.button(label="Compile", w=150, h=35, p=hlmvRow, c=compileFunc)

    #Bin folder path
    binFolderSpacer = pm.text(label="", h=8, p=settingsTab, align="left")
    binFolderText = pm.text(label="Bin folder path", w=300, p=settingsTab, align="left")
    binPathRow = pm.rowLayout(nc=2, p=settingsTab)
    def binPathBrowse():
        binPath = cmds.fileDialog2(fm=3, dialogStyle=2, okCaption='Accept')
        binFilePath = cmds.textField("binFilePath", edit=True, text=str(binPath[0]))
        cmds.optionVar( sv=('dmxBinFilePath', str(binPath[0])) )
        return binFilePath

    binFilePath = binPathBrowse
    if cmds.optionVar( exists='dmxBinFilePath' ):
        dmxBinFilePath = cmds.optionVar( q='dmxBinFilePath' )
        binPathField = pm.textField("binFilePath", w=270, p=binPathRow, text=dmxBinFilePath)
    else:
        binPathField = pm.textField("binFilePath", w=270, p=binPathRow)

    binPathIcon = pm.iconTextButton(style="iconAndTextVertical", image1="openLoadGeneric.png", w=30, p=binPathRow, c=binPathBrowse)

    #Gameinfo folder path
    gameinfoFolderText = pm.text(label="Gameinfo.txt folder path", p=settingsTab, align="left")
    gameinfoFolderRow = pm.rowLayout(nc=2, p=settingsTab)
    def gameinfoPathBrowse():
        basicFilter = "*.txt"
        gameinfoPath = cmds.fileDialog2(fm=3, ff=basicFilter, dialogStyle=2, okCaption='Accept')
        gameinfoFilePath = cmds.textField("gameinfoFilePath", edit=True, text=str(gameinfoPath[0]))
        cmds.optionVar( sv=('dmxGameinfoFilePath', str(gameinfoPath[0])) )
        return gameinfoFilePath

    gameinfoFilePath = gameinfoPathBrowse
    if cmds.optionVar( exists='dmxGameinfoFilePath' ):
        gameinfoFilePath = cmds.optionVar( q='dmxGameinfoFilePath' )
        gameinfoPathField = pm.textField("gameinfoFilePath", w=270, p=gameinfoFolderRow, text=gameinfoFilePath)
    else:
        binPathField = pm.textField("gameinfoFilePath", w=270, p=gameinfoFolderRow)
    gameinfoPathIcon = pm.iconTextButton(style="iconAndTextVertical", image1="openLoadGeneric.png", w=30, p=gameinfoFolderRow, c=gameinfoPathBrowse)

    shelfRow = pm.rowLayout(nc=1, p=settingsTab)
    shelfButton = pm.button(label="Add to Shelf", w=300, h=25, p=shelfRow, c=dmxExportButton)


    pm.showWindow(window0)

def paths():
    binPath=os.path.normpath(cmds.textField("binFilePath", query=True, text=True))
    gameinfo=os.path.normpath(cmds.textField("gameinfoFilePath", query=True, text=True))
    studiomdl=os.path.join(os.path.normpath(binPath), "studiomdl.exe")
    hlmv=os.path.join(os.path.normpath(binPath), "hlmv.exe")
    mdlDir=os.path.join(os.path.normpath(gameinfo), "models/")
    return binPath, gameinfo, studiomdl, hlmv, mdlDir

def fbx2dmxFunc():
    a = paths()
    binPath = a[0]
    gameinfo = a[1]
    studiomdl = a[2]
    hlmv = a[3]
    mdlDir = a[4]
    #Paths
    scriptlocation = os.path.dirname(__file__)
    fbx2dmxs = os.path.join(scriptlocation, 'DMXExport/fbx2dmx.exe')
    fbx2dmx = os.path.normpath(fbx2dmxs)
    gameinfoExists = os.path.isfile(os.path.join(os.path.normpath(gameinfo), "gameinfo.txt"))

    if not gameinfoExists:
            cmds.error("gameinfo.txt not found, set a gameinfo path in settings")

    # Check if plugins are loaded
    if pm.pluginInfo("fbxmaya", loaded=True, query=True) == False:
        pm.loadPlugin("fbxmaya")

    #FBX Settings
    pm.mel.FBXExportFileVersion(v="FBX201400")
    pm.mel.FBXExportUpAxis("Y")
    pm.mel.FBXExportBakeComplexAnimation(v=False)
    pm.mel.FBXExportConstraints(v=False)
    pm.mel.FBXExportInputConnections(v=False)
    pm.mel.FBXExportUseSceneName(v=True)
    pm.mel.FBXExportInAscii(v=False)
    pm.mel.FBXExportSkins(v=True)
    pm.mel.FBXExportShapes(v=True)
    pm.mel.FBXExportCameras(v=False)
    pm.mel.FBXExportLights(v=False)

    #Check if triangulate checked
    if cmds.checkBox("triangulateBox", query=True, value=True):
        pm.mel.FBXExportTriangulate(v=True)
    else:
        pm.mel.FBXExportTriangulate(v=True)

    #Get file name from text field
    filename = cmds.textField("dmxFilePath", query=True, text=True)

    if filename == "":
        cmds.error("Set an export path")
    #Export FBX
    if exportAllVar == 0:
        cmds.file(filename, es = True, type = "FBX Export")
        print "Exported selected"
    else:
        pm.mel.FBXExport(f=filename)
        print "Exported all"

    #Call FBX2DMX
    print "------------------------------------------------------------------------"
    print "FBX2DMX"
    print "------------------------------------------------------------------------"
    if cmds.checkBox("animationBox", query=True, value=True):
        process = subprocess.Popen([fbx2dmx,
                        '-nop4',
                        '-file', filename,
                        '-a',
                        '%1',
                        '-game',
                        gameinfo,
                        '-v',
                        '-v'],
                        stdout=subprocess.PIPE, shell=True)
    else:
        process = subprocess.Popen([fbx2dmx,
                        '-nop4',
                        '-file', filename,
                        '%1',
                        '-game',
                        gameinfo,
                        '-v',
                        '-v'],
                        stdout=subprocess.PIPE, shell=True)
    #Print output to console
    while True:
        output = process.stdout.readline()
        if process.poll() is not None and output == '':
            break
        if output:
            print (output.strip())
    retval = process.poll()

    if cmds.checkBox("compileBox", query=True, value=True):
        compileFunc(self)

#Compile
def compileFunc(self):
    a = paths()
    binPath = a[0]
    gameinfo = a[1]
    studiomdl = a[2]
    hlmv = a[3]
    mdlDir = a[4]
    #Send qc to studiomdl
    print "------------------------------------------------------------------------"
    print "COMPILING"
    print "------------------------------------------------------------------------"

    qcPath = cmds.textField("qcFilePath", query=True, text=True)

    if qcPath == "":
            cmds.error("Set a QC path")

    process = subprocess.Popen([studiomdl,
                    '-nop4',
                    '-game',
                    gameinfo,
                    '-file', qcPath],
                    stdout=subprocess.PIPE, shell=True)
    #Print output to console
    while True:
        output = process.stdout.readline()
        if process.poll() is not None and output == '':
            break
        if output:
            print (output.strip())
    retval = process.poll()
    return qcPath

#HLMV
def hlmvFunc(self):
    a = paths()
    binPath = a[0]
    gameinfo = a[1]
    studiomdl = a[2]
    hlmv = a[3]
    mdlDir = a[4]
    qcPath = compileFunc(self)

    #Get mdl path from qc
    f = open(qcPath,'r')
    qcMdl = "$modelname"
    for line in f.readlines():
        if line.find("$modelname") >= 0:
            mdlName=re.findall(r'"([^"]*)"', line)
    mdlNameStr = "".join(mdlName)
    mdlPath = mdlDir+mdlNameStr
    mdlPathFix = os.path.normcase(mdlPath)

    #Open HLMV
    subprocess.Popen([hlmv,
        mdlPathFix],
        shell=True)
    print "------------------------------------------------------------------------"
    print "HLMV OPENED"
    print "------------------------------------------------------------------------"

def dmxExportButton(self):
    currentShelf = cmds.tabLayout("ShelfLayout", selectTab=True, query=True)
    cmds.shelfButton(annotation='DMX Export',
                     image1='DMXExport.png',
                     imageOverlayLabel='DMX',
                     command='import DMXExport; reload(DMXExport); DMXExport.createUI()',
                     parent=currentShelf,
                     label='DMX')
