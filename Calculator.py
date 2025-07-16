#GUI Reqs
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox, QMessageBox
#Sekiro Data and functions
from Sekiro import Reference
from Sekiro import Enemy
from Sekiro import Utils
#Other
from os import path
from functools import partial
import pyperclip

class ExtrasWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Extra Options")
        layout = QVBoxLayout()

        self.wealthballoon = QCheckBox("Wealth Balloon", self)
        self.possesstionballoon = QCheckBox("Possession Balloon", self)
        self.spiritballoon = QCheckBox("Spirit Balloon", self)
        self.soulballoon = QCheckBox("Soul Balloon", self)
        self.pilgrimageballoon = QCheckBox("Pilgrimage Balloon", self)
        self.virtuousdeed = QCheckBox("Virtuous Deed", self)
        self.mostvirtuousdeed = QCheckBox("Most Virtuous Deed", self)

        layout.addWidget(self.wealthballoon)
        layout.addWidget(self.possesstionballoon)
        layout.addWidget(self.spiritballoon)
        layout.addWidget(self.soulballoon)
        layout.addWidget(self.pilgrimageballoon)
        layout.addWidget(self.virtuousdeed)
        layout.addWidget(self.mostvirtuousdeed)

        self.wealthballoon.setChecked(ui.wealthBalloon)
        self.possesstionballoon.setChecked(ui.possessionBalloon)
        self.spiritballoon.setChecked(ui.spiritBalloon)
        self.soulballoon.setChecked(ui.soulBalloon)
        self.pilgrimageballoon.setChecked(ui.pilgrimageBalloon)
        self.virtuousdeed.setChecked(ui.virtuousDeed)
        self.mostvirtuousdeed.setChecked(ui.mostVirtuousDeed)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def getData(self):
        return {
            "Wealth": self.wealthballoon.isChecked(),
            "Possession": self.possesstionballoon.isChecked(),
            "Spirit": self.spiritballoon.isChecked(),
            "Soul": self.soulballoon.isChecked(),
            "Pilgrimage": self.pilgrimageballoon.isChecked(),
            "VirtuousDeed": self.virtuousdeed.isChecked(),
            "MostVirtuousDeed": self.mostvirtuousdeed.isChecked(),
        }
    
class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.Functions = Utils.SekiroFunctions()
        self.setupUi(self)
        self.createMenus()
        self.updateSorting("Alphabetical (A-Z)")

        self.virtuousDeed = False
        self.mostVirtuousDeed = False
        self.wealthBalloon = False
        self.possessionBalloon = False
        self.spiritBalloon = False
        self.soulBalloon = False
        self.pilgrimageBalloon = False

    def createMenus(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        copyMenu = fileMenu.addMenu("Copy")
        exportMenu = fileMenu.addMenu("Export") 
        sortingMenu = fileMenu.addMenu("Sorting")

        infomenu = menubar.addMenu("Info")
        infomenu.addAction("Apparitions and Confetti", lambda: showMessageBox("Apparitions and Confetti",
            f"Divine Confetti works by adding 20 magic damage to your attacks. Since your base damage is 80, this usually acts as a +25% damage buff. However, it can be much more due to some enemies being weak to magic damage.<br>"
            "Magic damage also has a piercing effect and will go through blocks. This only applies to the additional 20 and not all of your damage.<br><br>"
            "Some apparition type enemies have a feature that decreases all physical damage taken unless you have the divine confetti effect. (StateInfo 64)<br>"
            "Hitting one of these enemies with a confetti buffed attack will ignore this effect.<br><br>"
            f"Headless - 90% damage reduction (doesn't apply to underwater headless)<br>"
            f"Shichimen - 67% damage reduction<br>"
            f"O'rin of the Water - 33% damage reduction<br>"))
        infomenu.addAction("Time Cycles and Demon Bell", lambda: showMessageBox("Time Cycles and Demon Bell",
            "As you advance through the game, the time cycle progresses as follows:<br><br>"
            f"Morning - After the tutorial<br>"
            f"Noon - After killing one of the \"Quest Bosses\" (Genichiro, Corrupted Monk, Guardian Ape, Folding Screen Monkeys)<br>"
            f"Evening - After killing 3 of the above bosses<br>"
            f"Night - After visiting Fountainhead Palace for the first time<br><br>"
            "Having the Demon Bell active will simulate incrementing the time cycle by one step, so if you are in morning, it will be treated as noon.<br>"
            "This is used in some calculations, since enemies are buffed as the time cycle increases and some only drop certain items at specific times.<br>"
            "Some areas only use \"Default\" and \"Kaneyoi\" (Morning and Night + Demonbell respectively). If you fight an enemy within this area at ANY time other than night with demon bell then it will use Morning.<br>"))
        infomenu.addAction("Reflections", lambda: showMessageBox("Reflections",
            "Boss stats are fixed within reflections and gauntlets. To compensate for this, the player's attack power is also locked to 14 so that you can't melt them at high AP levels.<br>"
            f"Generally, reflections will feel slightly harder than normal by comparison.<br>"
            f"Gauntlets and reflections are identical, with the exception of Mortal Journey which has slightly stronger enemies.<br>"))
        infomenu.addAction("Entity IDs", lambda: showMessageBox("Entity IDs",
            "All enemies have NpcParamIds, which dictate a whole lot of things like stats and itemlots.<br>"
            f"This application already has all bosses and minibosses mapped, which is why they appear in the dropdown.<br><br>"
            f"If you want to get data on a basic enemy that is not listed, follow these steps:<br>"
            "1. Download <a href='https://github.com/vawser/Smithbox/releases'>Smithbox</a> and <a href='https://github.com/Nordgaren/UXM-Selective-Unpack/releases'>UXM</a><br>"
            "2. Unpack the game files with UXM by inputting your game install path<br>"
            "3. Open Smithbox and create a new project<br>"
            "4. Open the Map Editor tab, load the map you want by right clicking<br>"
            "5. Locate the enemy within the map, you can move around with WASD while holding right click on the viewport<br>"
            "6. Click on the enemy, navigate to the \"Properties\" tab on the right and copy the NpcParamId<br>"
            "7. Paste the ID into the field within this application and press enter<br>"))
        infomenu.addSeparator()
        infomenu.addAction("Credits", lambda: showMessageBox("Credits",
            "<a href='https://next.nexusmods.com/profile/AeroliteWasTaken'>Aero</a> - Me! :D<br><br>"
            "<a href='https://www.youtube.com/@Victor_StudentOfFloppa'>Savio</a> - For the original idea, inspiration, and moral support. Also did the majority of the testing for the GUI :)<br><br>"
            "<a href='https://www.youtube.com/@Holm_GG'>Holm</a> - Helped a LOT with testing and comparing data, thanks!<br><br>"
            "MyMaidisKitchenAid - Explained some intricacies with params and taught me a lot about the scalings (thanks for saving me from hours of pain)<br>"))

        def createAction(name, func):
            action = QtWidgets.QAction(name, self)
            action.triggered.connect(func)
            return action
        
        def showMessageBox(title, message):
            msg = QMessageBox(self)
            msg.setWindowTitle(title)
            msg.setTextFormat(QtCore.Qt.RichText)
            msg.setText(message)
            msg.exec_()

        copyMenu.addAction(createAction("Stats", partial(self.copyTxt, "Stats")))
        copyMenu.addAction(createAction("Drops", partial(self.copyTxt, "Drops")))
        copyMenu.addAction(createAction("All", partial(self.copyTxt, "All")))  
        exportMenu.addAction(createAction("Stats", partial(self.exportTxt, "Stats", "txt")))
        exportMenu.addAction(createAction("Drops", partial(self.exportTxt, "Drops", "txt")))
        exportMenu.addAction(createAction("All", partial(self.exportTxt, "All", "txt")))  
        sortingMenu.addAction(createAction("Progression", partial(self.updateSorting, 'Progression')))
        sortingMenu.addAction(createAction("Alphabetical (A-Z)", partial(self.updateSorting, 'Alphabetical (A-Z)')))
        sortingMenu.addAction(createAction("Alphabetical (Z-A)", partial(self.updateSorting, 'Alphabetical (Z-A)')))
        sortingMenu.addAction(createAction("By ID", partial(self.updateSorting, 'ID')))

    def showError(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error") 
        msg.setText(text) 
        msg.exec_() 
   
    def initDropdown(self):
        for index, i in enumerate(self.enemiesList):
            self.EnemyComboBox.addItem("") # add enough blank entries for all enemies
            self.EnemyComboBox.setItemText(index, QtCore.QCoreApplication.translate("Form", f"{i}")) # add all enemies to the combobox
        self.EnemyComboBox.setCurrentIndex(-1)

    def updateSorting(self, mode):
        self.EnemyComboBox.clear()
        if mode == "Alphabetical (A-Z)":
            self.enemiesList = sorted(self.enemiesList)
            self.initDropdown()
        
        elif mode == "Alphabetical (Z-A)":
            self.enemiesList = sorted(self.enemiesList, reverse=True)
            self.initDropdown()

        elif mode == "Progression":
            self.enemiesList = Reference.EnemyID.keys()
            self.initDropdown()

        elif mode == "ID":
            self.enemiesList = sorted(Reference.EnemyID.keys(), key=lambda k: Reference.EnemyID[k])
            self.initDropdown()

    def getTxt(self, mode):
        stats_output = []
        drops_output = []
        if mode in ["Stats", "All"]:
            stats_output.append("[Stats]")
            for i in range(self.StatsListWidget.count()):
                stat = self.StatsListWidget.item(i).text()
                if '--' not in stat:
                    stats_output.append(stat)
            stats_output.append("\n")

        if mode in ["Drops", "All"]:
            drops_output.append("[Drops]")
            for i in range(self.DropsListWidget.count()):
                drop = self.DropsListWidget.item(i).text()
                if '--' not in drop:
                    drops_output.append(drop)
            drops_output.append("\n")

        return stats_output + drops_output

    def exportTxt(self, mode, filetype):
        all_data = self.getTxt(mode)

        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            f"Export Both as {filetype.upper()}",
            f"export.{filetype}",
            f"{filetype.upper()} Files (*.{filetype})",
            options=options)

        if filename:
            if filetype == "txt":
                with open(filename, "w") as f:
                    f.write("\n".join(all_data))

    def copyTxt(self, mode):
        all_data = self.getTxt(mode)
        pyperclip.copy('\n'.join(all_data))

    def getOpts(self):
       return {
            'possessionBalloon': self.possessionBalloon,
            'spiritBalloon': self.spiritBalloon,
            'soulBalloon': self.soulBalloon,
            'pilgrimageBalloon': self.pilgrimageBalloon,
            'virtuousDeed': self.virtuousDeed,
            'mostVirtuousDeed': self.mostVirtuousDeed}
    
    def showExtras(self):
        dialog = ExtrasWindow(self)
        if dialog.exec_():  # ok is pressed
            data = dialog.getData()
            self.wealthBalloon = data['Wealth']
            self.possessionBalloon = data['Possession']
            self.spiritBalloon = data['Spirit']
            self.soulBalloon = data['Soul']
            self.pilgrimageBalloon = data['Pilgrimage']
            self.virtuousDeed = data['VirtuousDeed']
            self.mostVirtuousDeed = data['MostVirtuousDeed']
            self.update()
        else:
            return # cancel is pressed

    def addStats(self, hp, posture, regen, ap, attackRate, attacksNeeded):
        self.StatsListWidget.addItem(f"-----------------------------------------------------------------------------")
        self.StatsListWidget.addItem(f"HP - {hp}")
        self.StatsListWidget.addItem(f"Posture - {posture}")
        self.StatsListWidget.addItem(f"Posture Regen - {regen}")
        self.StatsListWidget.addItem(f"-----------------------------------------------------------------------------")
        self.StatsListWidget.addItem(f"Damage Multiplier - x{attackRate}")
        self.StatsListWidget.addItem(f"Max hits to kill at AP{ap} - {attacksNeeded}")
        self.StatsListWidget.addItem(f"-----------------------------------------------------------------------------")

    def addRates(self, enemy, NG, CL, DB, Time, opts, Ndrops, Rdrops, Idrops):
        Sen = self.Functions.getSen(enemy=enemy, NG=NG, CL=CL, effects={
                                            "wealthBalloon": self.wealthBalloon, 
                                            "pilgrimageBalloon": self.pilgrimageBalloon, 
                                            "virtuousDeed": self.virtuousDeed, 
                                            "mostVirtuousDeed": self.mostVirtuousDeed})
        Exp = self.Functions.getExp(enemy=enemy, NG=NG, CL=CL)
                
        self.DropsListWidget.clear()
        self.DropsListWidget.addItem(f"-----------------------------------------------------------------------------")
        self.DropsListWidget.addItem(f"Sen - {Sen}")
        self.DropsListWidget.addItem(f"EXP - {Exp}")
        self.DropsListWidget.addItem(f"-----------------------------------------------------------------------------")

        drops = self.Functions.getDrops(enemy, dropLists=[Ndrops, Rdrops, Idrops], DB=DB, Time=Time, effects=opts)

        for drop in drops:
            self.DropsListWidget.addItem(f"{drop['Count']} {drop['Name']} - {drop['Chance']}")
        
        self.DropsListWidget.addItem(f"-----------------------------------------------------------------------------")

    def parseEnemy(self):
        enemy = self.enemyIdLineEdit.text()
        if not enemy: # if override field is empty
            try:
                enemy = Reference.EnemyID[self.EnemyComboBox.currentText()] # fetch from dropdown
            except:
                return False
            
        enemy = int(enemy)
        if enemy not in Enemy.Stats and enemy not in [1, 2, 3]: # if enemy doesnt exist (isnt in stats or inners)
            self.showError("Please select a valid enemy")
            self.enemyIdLineEdit.clear()
            return False
        
        return enemy

    def parseStats(self, enemy, ng, cl, db, time, mode, ap):
        result = self.Functions.getStats(enemy=enemy, NG=ng, CL=cl, DB=db, Time=time, Mode=mode, AP=ap)

        if result is None:
            self.StatsListWidget.addItem("Selected time does not update this enemy's stats.")
            self.StatsListWidget.addItem("Drops could still be affected by this time cycle.")
            self.StatsListWidget.addItem("Please try using Default, or Night if Demon Bell is active.")
            return
        
        if result == 'EnemyNotFound':
                self.showError("Please select a valid enemy")
                return
        hp, posture, regen, attackRate, attacksNeeded = result.values()
        
        self.addStats(hp, posture, regen, ap, attackRate, attacksNeeded)

    def parseDrops(self, enemy, NG, CL, DB, Time):
        result = self.Functions.getDropLists(enemy=enemy, DB=DB, Time=Time, effects={"pilgrimageBalloon": self.pilgrimageBalloon, 
                                                                                     "soulBalloon": self.soulBalloon})
        if result is None: 
            self.DropsListWidget.addItem("Selected time does not update this enemy's drops.")
            self.DropsListWidget.addItem("Stats could still be affected by this time cycle.")
            self.DropsListWidget.addItem("Please try using Default or Night instead.")
            return
        
        NdropList, RdropList, IdropList = result
        opts = self.getOpts()
        self.addRates(enemy, NG, CL, DB, Time, opts, NdropList, RdropList, IdropList)  
        
    def update(self):
        enemy = self.parseEnemy()
        if not enemy:
            return
        ng = self.ngComboBox.currentIndex()
        mode = self.GameModeComboBox.currentIndex()
        ap = self.APspinBox.value()
        cl = self.clCheckButton.isChecked()
        db = self.dbCheckButton.isChecked()
        time = self.timeComboBox.currentIndex()+1

        self.StatsListWidget.clear()
        self.DropsListWidget.clear()
        
        if mode == 0 and enemy not in [1, 2, 3]:
            self.parseDrops(enemy, ng, cl, db, time) # update rates if enemy isnt an inner fight or in a gauntlet/reflection

        self.parseStats(enemy, ng, cl, db, time, mode, ap)
    
    def setupUi(self, Form):
        self.enemiesList = Reference.EnemyID.keys() # get list of enemy names
        Form.setObjectName("Form")
        Form.setFixedSize(441, 389)
        self.timeComboBox = QtWidgets.QComboBox(Form)
        self.timeComboBox.setGeometry(QtCore.QRect(70, 120, 101, 22))
        self.timeComboBox.setObjectName("timeComboBox")
        self.timeComboBox.activated[str].connect(self.update)
        self.timeComboBox.addItem("")
        self.timeComboBox.addItem("")
        self.timeComboBox.addItem("")
        self.timeComboBox.addItem("")
        self.clCheckButton = QtWidgets.QCheckBox(Form)
        self.clCheckButton.setGeometry(QtCore.QRect(200, 90, 70, 21))
        self.clCheckButton.setObjectName("clCheckButton")
        self.clCheckButton.stateChanged.connect(self.update)
        self.dbCheckButton = QtWidgets.QCheckBox(Form)
        self.dbCheckButton.setGeometry(QtCore.QRect(200, 120, 70, 21))
        self.dbCheckButton.setObjectName("dbCheckButton")
        self.dbCheckButton.stateChanged.connect(self.update)
        self.ngComboBox = QtWidgets.QComboBox(Form)
        self.ngComboBox.setGeometry(QtCore.QRect(70, 90, 101, 22))
        self.ngComboBox.setObjectName("ngComboBox")
        self.ngComboBox.activated[str].connect(self.update)
        self.ngComboBox.addItem("")
        self.ngComboBox.addItem("")
        self.ngComboBox.addItem("")
        self.ngComboBox.addItem("")
        self.ngComboBox.addItem("")
        self.ngComboBox.addItem("")
        self.ngComboBox.addItem("")
        self.ngComboBox.addItem("")
        self.enemyIdLineEdit = QtWidgets.QLineEdit(Form)
        self.enemyIdLineEdit.setGeometry(QtCore.QRect(70, 60, 211, 20))
        self.enemyIdLineEdit.setToolTip("")
        self.enemyIdLineEdit.setObjectName("enemyIdLineEdit")
        self.enemyIdLineEdit.returnPressed.connect(self.update)
        self.EnemyComboBox = QtWidgets.QComboBox(Form)
        self.EnemyComboBox.setGeometry(QtCore.QRect(70, 30, 341, 22))
        self.EnemyComboBox.setToolTip("")
        self.EnemyComboBox.setEditable(True)
        self.EnemyComboBox.setObjectName("EnemyComboBox")
        self.EnemyComboBox.activated[str].connect(self.update)
        self.EnemyLabel = QtWidgets.QLabel(Form)
        self.EnemyLabel.setGeometry(QtCore.QRect(20, 30, 41, 21))
        self.EnemyLabel.setObjectName("EnemyLabel")
        self.EntityIDLabel = QtWidgets.QLabel(Form)
        self.EntityIDLabel.setGeometry(QtCore.QRect(20, 60, 51, 21))
        self.EntityIDLabel.setWhatsThis("")
        self.EntityIDLabel.setObjectName("EntityIDLabel")
        self.NGLabel = QtWidgets.QLabel(Form)
        self.NGLabel.setGeometry(QtCore.QRect(20, 90, 51, 21))
        self.NGLabel.setWhatsThis("")
        self.NGLabel.setObjectName("NGLabel")
        self.TimeLabel = QtWidgets.QLabel(Form)
        self.TimeLabel.setGeometry(QtCore.QRect(20, 120, 51, 21))
        self.TimeLabel.setWhatsThis("")
        self.TimeLabel.setObjectName("TimeLabel")
        self.line = QtWidgets.QFrame(Form)
        self.line.setGeometry(QtCore.QRect(176, 90, 16, 61))
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(Form)
        self.line_2.setGeometry(QtCore.QRect(20, 140, 391, 21))
        self.line_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(Form)
        self.line_3.setGeometry(QtCore.QRect(280, 60, 20, 91))
        self.line_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setObjectName("line_3")
        self.APLabel = QtWidgets.QLabel(Form)
        self.APLabel.setGeometry(QtCore.QRect(300, 90, 71, 21))
        self.APLabel.setObjectName("APLabel")
        self.APspinBox = QtWidgets.QSpinBox(Form)
        self.APspinBox.setGeometry(QtCore.QRect(370, 90, 42, 22))
        self.APspinBox.setMinimum(1)
        self.APspinBox.setObjectName("APspinBox")
        self.APspinBox.valueChanged.connect(self.update)
        self.ExtrasButton = QtWidgets.QPushButton(Form)
        self.ExtrasButton.setGeometry(QtCore.QRect(300, 120, 111, 20))
        self.ExtrasButton.setObjectName("ExtrasButton")
        self.ExtrasButton.clicked.connect(self.showExtras)
        self.GameModeComboBox = QtWidgets.QComboBox(Form)
        self.GameModeComboBox.setGeometry(QtCore.QRect(300, 60, 111, 22))
        self.GameModeComboBox.setObjectName("GameModeComboBox")
        self.GameModeComboBox.activated[str].connect(self.update)
        self.GameModeComboBox.addItem("")
        self.GameModeComboBox.addItem("")
        self.GameModeComboBox.addItem("")
        self.DataTabs = QtWidgets.QTabWidget(Form)
        self.DataTabs.setGeometry(QtCore.QRect(20, 160, 401, 211))
        self.DataTabs.setToolTipDuration(-1)
        self.DataTabs.setObjectName("DataTabs")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.StatsScrollArea = QtWidgets.QScrollArea(self.tab)
        self.StatsScrollArea.setGeometry(QtCore.QRect(0, 0, 401, 191))
        self.StatsScrollArea.setWidgetResizable(True)
        self.StatsScrollArea.setObjectName("StatsScrollArea")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 399, 189))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.StatsListWidget = QtWidgets.QListWidget(self.scrollAreaWidgetContents_2)
        self.StatsListWidget.setGeometry(QtCore.QRect(0, 0, 401, 191))
        self.StatsListWidget.setObjectName("StatsListWidget")
        self.StatsScrollArea.setWidget(self.scrollAreaWidgetContents_2)
        self.DataTabs.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.DropsScrollArea = QtWidgets.QScrollArea(self.tab_2)
        self.DropsScrollArea.setGeometry(QtCore.QRect(0, 0, 401, 191))
        self.DropsScrollArea.setWidgetResizable(True)
        self.DropsScrollArea.setObjectName("DropsScrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 399, 189))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.DropsListWidget = QtWidgets.QListWidget(self.scrollAreaWidgetContents)
        self.DropsListWidget.setGeometry(QtCore.QRect(0, 0, 401, 191))
        self.DropsListWidget.setObjectName("DropsListWidget")
        self.DropsScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.DataTabs.addTab(self.tab_2, "")

        self.retranslateUi(Form)
        self.EnemyComboBox.setCurrentIndex(-1)
        self.DataTabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Sekiro Calculator"))
        self.EnemyComboBox.setToolTip(_translate("Form", "List of common bosses and minibosses"))
        self.timeComboBox.setToolTip(_translate("Form", "Time Cycle. Refer to the info menu for more details."))
        self.timeComboBox.setItemText(0, _translate("Form", "Morning/Default"))
        self.timeComboBox.setItemText(1, _translate("Form", "Noon"))
        self.timeComboBox.setItemText(2, _translate("Form", "Evening"))
        self.timeComboBox.setItemText(3, _translate("Form", "Night"))
        self.clCheckButton.setText(_translate("Form", "Charmless"))
        self.dbCheckButton.setText(_translate("Form", "Demon Bell"))
        self.ngComboBox.setItemText(0, _translate("Form", "NG"))
        self.ngComboBox.setItemText(1, _translate("Form", "NG+"))
        self.ngComboBox.setItemText(2, _translate("Form", "NG+2"))
        self.ngComboBox.setItemText(3, _translate("Form", "NG+3"))
        self.ngComboBox.setItemText(4, _translate("Form", "NG+4"))
        self.ngComboBox.setItemText(5, _translate("Form", "NG+5"))
        self.ngComboBox.setItemText(6, _translate("Form", "NG+6"))
        self.ngComboBox.setItemText(7, _translate("Form", "NG+7"))
        self.enemyIdLineEdit.setPlaceholderText(_translate("Form", "*Optional"))
        self.enemyIdLineEdit.setToolTip(_translate("Form", "Optional override for enemies not listed above\n" \
        "Use NpcParamIDs"))
        self.EnemyLabel.setText(_translate("Form", "Enemy:"))
        self.EntityIDLabel.setText(_translate("Form", "Entity ID:"))
        self.NGLabel.setText(_translate("Form", "NG Cycle:"))
        self.TimeLabel.setText(_translate("Form", "Time:"))
        self.APLabel.setText(_translate("Form", "Attack Power:"))
        self.ExtrasButton.setToolTip(_translate("Form", "Extra options, mostly for drop calculations"))
        self.ExtrasButton.setText(_translate("Form", "Extra Options"))
        self.GameModeComboBox.setToolTip(_translate("Form", "Current Game Mode"))
        self.GameModeComboBox.setItemText(0, _translate("Form", "Normal"))
        self.GameModeComboBox.setItemText(1, _translate("Form", "Reflections"))
        self.GameModeComboBox.setItemText(2, _translate("Form", "Mortal Journey"))
        __sortingEnabled = self.StatsListWidget.isSortingEnabled()
        self.StatsListWidget.setSortingEnabled(False)
        self.StatsListWidget.setSortingEnabled(__sortingEnabled)
        self.DataTabs.setTabText(self.DataTabs.indexOf(self.tab), _translate("Form", "Stats"))
        __sortingEnabled = self.DropsListWidget.isSortingEnabled()
        self.DropsListWidget.setSortingEnabled(False)
        self.DropsListWidget.setSortingEnabled(__sortingEnabled)
        self.DataTabs.setTabText(self.DataTabs.indexOf(self.tab_2), _translate("Form", "Drops"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(path.join(path.dirname(path.abspath(__file__)), "calc.ico")))
    ui = Window()
    ui.show()
    sys.exit(app.exec_())

# pyinstaller Calculator.py --noconsole --icon=calc.ico --add-data "calc.ico;."