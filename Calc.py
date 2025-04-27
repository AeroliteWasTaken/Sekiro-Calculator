#GUI Reqs
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox
#Sekiro Data and functions
from res import Multipliers
from res import EnemyRef
from res import EnemyBaseStats
from res import Lots
from res import Utils
#Other
import copy
from os import path
from functools import partial
import pyperclip

class Functions():
    def __init__(self, uiInstance):
        super().__init__()
        self.UI = uiInstance
    
    @staticmethod
    def resolveInnerEnemy(enemy):
        if enemy in [1, 2, 3]:
            return EnemyRef.InnerEnemyRef[enemy], enemy  # mapped enemy, original inner id
        return enemy, None

    def getStats(self, enemy, NG, CL, DB, Time, Mode, AP, attack=5000010):
        if Mode == 0 and enemy in [1, 2, 3]:
            Mode = 1 # inner fights cant have a "Normal" mode, so default to Reflection

        enemy, changeEnemyForInner = Functions.resolveInnerEnemy(enemy)

        try:
            enemyRef = EnemyRef.EnemyRef[enemy]  # Get multipliers
            enemyAttackRate = 1 # start with a damage multiplier of 1

        except:
            self.UI.showError("Please select a valid enemy")
            return
        
        enemyStat = copy.deepcopy(EnemyBaseStats.EnemyStats[enemy]) # get all stats
 
        if enemy == 71001000: # if enemy is genichiro, add his other phases (separate by default)
            enemyStat[0] = [enemyStat[0], enemyStat[0], copy.deepcopy(EnemyBaseStats.EnemyStats[71100000])[0]]
            enemyStat[1] = [enemyStat[1], enemyStat[1], copy.deepcopy(EnemyBaseStats.EnemyStats[71100000])[1]]

        else:
            if enemy in Multipliers.Phase_HP_Multipliers.keys(): # if enemy is among named and listed minibosses/bosses
                enemyStat[0] = Utils.mult(enemyStat[0], Multipliers.Phase_HP_Multipliers[enemy]) # multiply different phases hp

            if enemy in Multipliers.Phase_Posture_Multipliers.keys(): # if enemy is among named and listed minibosses/bosses
                enemyStat[1] = Utils.mult(enemyStat[1], Multipliers.Phase_Posture_Multipliers[enemy]) # multiply different phases posture

        if Mode == 0: # normal
            try:
                timeOffset = Multipliers.Time_Offset[DB][Time]  # find offset for time + demon bell 
                enemyStat = Utils.multiplyRecursive(enemyStat, Multipliers.Clearcount_HP[CL][NG])  # scale ng
                enemyAttackRate *= Multipliers.Clearcount_Dmg[CL][NG]  # scale ng for attack

                if CL and NG == 0:
                    timeOffset += 700  # account for new game CL scaling
                if NG > 0:
                    enemyStat = Utils.multiplyRecursive(enemyStat, Multipliers.NGCycle_HP[enemyRef[0] + timeOffset])  # correct for ng+ scaling
                    enemyAttackRate *= Multipliers.NGCycle_Attack[enemyRef[0] + timeOffset]  # correct for ng+ scaling (attack multiplier)
                if CL and enemyRef[2]: # if enemy has charmless type scaling
                    enemyStat = Utils.multiplyRecursive(enemyStat, Multipliers.Charmless_Muliplier_By_Type[enemyRef[2]])  # increase stats based off of enemy type
                    
                enemyStat = Utils.multiplyRecursive(enemyStat, Multipliers.AreaScale_HP[enemyRef[1] + timeOffset])  # multiply area scaling
                enemyAttackRate *= Multipliers.AreaScale_Attack[enemyRef[1] + timeOffset]  # multiply area scaling (attack multiplier)

            except:
                # Selected Game Time is invalid for this enemy
                return

        else:
            AP = 14 # set ap to 14 since it's fixed in reflections and gauntlets
            if changeEnemyForInner: 
                enemy = changeEnemyForInner # change override reference for inner fights after calculating with base enemy

            if Mode == 1:  # reflection
                if enemy in EnemyRef.ReflectionOverride.keys(): # if enemy is listed as an exception or if it is an inner fight
                    override = EnemyRef.ReflectionOverride[enemy][(CL, DB)] # get scaling IDs from said exceptions
                else:
                    override = EnemyRef.ReflectionOverride[0][(CL, DB)] # use default

            elif Mode == 2:  # mortal journey
                if enemy in EnemyRef.MortalJourneyOverride.keys(): # if enemy is listed as an exception or if it is an inner fight
                    override = EnemyRef.MortalJourneyOverride[enemy][(CL, DB)] # get scaling IDs from said exceptions
                else:
                    override = EnemyRef.MortalJourneyOverride[0][(CL, DB)] # use default
            #Multiplying Scaling
            enemyStat = Utils.mult(Multipliers.AreaScale_HP[override[0]], enemyStat) 
            enemyStat = Utils.mult(Multipliers.NGCycle_HP[override[1]], enemyStat) 
            enemyStat = Utils.mult(Multipliers.Charmless_Muliplier_By_Type[enemyRef[2]], enemyStat) 

        enemyStat = Utils.floatConv(enemyStat)
        output = []
        try:
            output.append(', '.join([str(i) for i in enemyStat[0]])) # separate different phases
        except:
            output.append(enemyStat[0])

        try:
            output.append(', '.join([str(i) for i in enemyStat[1]])) # separate different phases
        except:
            output.append(enemyStat[1])

        output.append(enemyStat[2])
        attacksNeeded = Utils.findAttacksNeeded(enemyStat[0], Utils.getPlayerDmg(AP=AP, attack=attack))

        return output, AP, round(enemyAttackRate, 2), attacksNeeded

    def getDropLists(self, enemy, DB, Time):
        RdropList = []
        NdropList = []
        IdropList = []

        ninsatuDrops = EnemyBaseStats.Enemy_NinsatuLot_Drops[enemy]
        if ninsatuDrops[0] is not None:
            NdropList = [Lots.Resource_Item_Lots[i] for i in ninsatuDrops if i]

        resourceDrops = list(EnemyBaseStats.Enemy_ResourceLot_Drops[enemy])
        if resourceDrops[0] is not None:
            if (self.UI.soulBalloon or self.UI.pilgrimageBalloon) and resourceDrops[1] in Lots.Resource_Item_Lots:
                resourceDrops.append(resourceDrops[1]+1) # add the next resourceitemlot which contains drops for isAddLottery, triggered on stateinfo 345
            RdropList = [Lots.Resource_Item_Lots[i] for i in resourceDrops if i]

        itemDrops = copy.deepcopy(EnemyBaseStats.Enemy_ItemLot_Drops[enemy])
        if itemDrops[0] is not None: # if non mandatory itemlot drop exists
            newLot = itemDrops[0] + Lots.ItemLot_Time_Offset[DB][Time] # add extra itemlot for time of day (separate from default, which is always on)
            if newLot in Lots.Item_Lots:
                itemDrops.append(newLot) # only add if demon bell lots exist
            else:
                return # dont add drops if time is unsupported
        IdropList = [Lots.Item_Lots[i] for i in itemDrops if i]

        return NdropList, RdropList, IdropList

    def getExpSen(self, enemy, NG, CL):
        enemyRef = EnemyRef.EnemyRef[enemy] # Get multipliers

        if enemy in EnemyBaseStats.Boss_Exp_Rates.keys():
            baseExp = EnemyBaseStats.Boss_Exp_Rates[enemy] # fetch base drop rate for exp
        else:
            baseExp = EnemyBaseStats.Enemy_Exp_Rates[enemy] # fetch base drop rate for exp
        baseExp *= Multipliers.Clearcount_SenXP_Droprate[NG][1] # scale ng+ for exp
        baseExp *= Multipliers.Charmless_SenXP_Multiplier[CL] # scale for charmless for exp

        baseSen = EnemyBaseStats.Enemy_Sen_Rates[enemy] # fetch base drop rate for sen
        baseSen *= Multipliers.Clearcount_SenXP_Droprate[NG][0] # scale ng cycle for sen
        baseSen *= Multipliers.Charmless_SenXP_Multiplier[CL] # scale for charmless for sen

        if NG > 0:
            baseExp *= Multipliers.NGCycle_Exp_Droprate[enemyRef[0]] # scale ng+ for exp
            baseSen *= Multipliers.NGCycle_Sen_Droprate[enemyRef[0]] # scale ng+ for sen

        if self.UI.wealthBalloon:
            baseSen *= 1.5 # account for Mibu Balloon of Wealth

        if self.UI.pilgrimageBalloon:
            baseSen *= 1.5 # account for Mibu Pilgrimage Balloon

        if self.UI.mostVirtuousDeed:
            baseSen *= 1.25 

        elif self.UI.virtuousDeed:
            baseSen *= 1.125 # is ignored if Most Virtuous Deed is active too since it replaces the buff

        return baseSen, baseExp
    
    def addStats(self, output, attackPower, attackRate, attacksNeeded):
        self.UI.StatsListWidget.addItem(f"-----------------------------------------------------------------------------")
        self.UI.StatsListWidget.addItem(f"HP - {output[0]}")
        self.UI.StatsListWidget.addItem(f"Posture - {output[1]}")
        self.UI.StatsListWidget.addItem(f"Posture Regen - {output[2]}")
        self.UI.StatsListWidget.addItem(f"-----------------------------------------------------------------------------")
        self.UI.StatsListWidget.addItem(f"Damage Multiplier - x{attackRate}")
        self.UI.StatsListWidget.addItem(f"Max hits to kill at AP{attackPower} - {attacksNeeded}")
        self.UI.StatsListWidget.addItem(f"-----------------------------------------------------------------------------")

    def addRates(self, opts, sen, exp, Ndrops, Rdrops, Idrops):
        self.UI.DropsListWidget.addItem(f"-----------------------------------------------------------------------------")
        self.UI.DropsListWidget.addItem(f"Sen - {sen}")
        self.UI.DropsListWidget.addItem(f"EXP - {exp}")
        self.UI.DropsListWidget.addItem(f"-----------------------------------------------------------------------------")

        for lot in Ndrops:
            for item in lot:
                if item[2] != 0:
                    self.UI.DropsListWidget.addItem(f"{item[2]} {Lots.ResourceRef[item[0]]} on deathblow")

        for lot in Rdrops:
            for item in lot:
                if item[2] != 0:
                    chance = Utils.parseRChance(item[1], item[0], **opts)
                    self.UI.DropsListWidget.addItem(f"{item[2]} {Lots.ResourceRef[item[0]]} - {chance}% chance")  

        for lot in Idrops:
            for item in lot:
                if item[2] != 0:                  
                    chance = Utils.parseIChance(item[1], **opts)
                    self.UI.DropsListWidget.addItem(f"{item[2]} {Lots.ItemRef[item[0]]} - {chance}% chance")
        
        self.UI.DropsListWidget.addItem(f"-----------------------------------------------------------------------------")

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

    def get_data(self):
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
        self.Functions = Functions(self)
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

        def createAction(name, func):
            action = QtWidgets.QAction(name, self)
            action.triggered.connect(func)
            return action

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
            self.enemiesList = EnemyRef.EnemyNameRef.keys()
            self.initDropdown()

        elif mode == "ID":
            self.enemiesList = sorted(EnemyRef.EnemyNameRef.keys(), key=lambda k: EnemyRef.EnemyNameRef[k])
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
            data = dialog.get_data()
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
 
    def parseEnemy(self):
        enemy = self.enemyIdLineEdit.text()
        if not enemy: # if override field is empty
            try:
                enemy = EnemyRef.EnemyNameRef[self.EnemyComboBox.currentText()] # fetch from dropdown
            except:
                return False
        try:
            enemy = int(enemy)
            if enemy not in EnemyBaseStats.EnemyStats:
                raise Exception
        except:
            self.showError("Please select a valid enemy")
            return False
        return enemy

    def parseDrops(self, enemy, NG, CL, DB, Time):
        Sen, Exp = self.Functions.getExpSen(enemy=enemy, NG=NG, CL=CL)
        result = self.Functions.getDropLists(enemy=enemy, DB=DB, Time=Time)

        if result is not None:
            NdropList, RdropList, IdropList = result
        else: 
            return

        opts = self.getOpts()
        self.Functions.addRates(opts, Utils.ceil(Sen), Utils.ceil(Exp), NdropList, RdropList, IdropList)  
        
    def update(self):
        enemy = self.parseEnemy()
        if not enemy:
            return
        ng = self.ngComboBox.currentIndex()
        time = self.timeComboBox.currentIndex() + 1 # time is 1-4 and indexes are 0-3
        mode = self.GameModeComboBox.currentIndex()
        ap = self.APspinBox.value()
        cl = self.clCheckButton.isChecked()
        db = self.dbCheckButton.isChecked()

        self.StatsListWidget.clear()
        self.DropsListWidget.clear()
        
        if mode == 0 and enemy not in [1, 2, 3]:
            self.parseDrops(enemy, ng, cl, db, time) # update rates if enemy isnt an inner fight or in a gauntlet/reflection

        result = self.Functions.getStats(enemy=enemy, NG=ng, CL=cl, DB=db, Time=time, Mode=mode, AP=ap)

        if result is None:
            return # skip adding values if there is an error in calculation (this is usually due to an incorrect time input)
        output, attackPower, attackRate, attacksNeeded = result

        self.Functions.addStats(output, attackPower, attackRate, attacksNeeded)
    
    def setupUi(self, Form):
        self.enemiesList = EnemyRef.EnemyNameRef.keys() # get list of enemy names
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
        self.timeComboBox.setToolTip(_translate("Form", "Some areas only use \"default\", night and/or night + demon bell.\n" \
        "Morning - After tutorial\n" \
        "Noon - After killing one of the following: Geni, Ape, Cmonk, FSMs\n" \
        "Evening - After beating 3 of the above bosses\n" \
        "Night - After visiting Fountainhead Palace for the first time"))
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
    app.setWindowIcon(QtGui.QIcon(path.join(path.dirname(path.abspath(__file__)), "res/calc.ico"))) # remove 'res/' and move ico to root when freezing
    ui = Window()
    ui.show()
    sys.exit(app.exec_())

# pyinstaller calc.py --noconsole --icon=calc.ico --add-data "calc.ico;."