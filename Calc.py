#GUI Reqs
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
#Sekiro Data and functions
from res import Multipliers
from res import EnemyRef
from res import EnemyBaseStats
from res import Lots
from res import Utils
#Other
import copy

class Window(QtWidgets.QMainWindow):

    def showError(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error") 
        msg.setText(text) 
        msg.exec_()

    def showRates(self, enemy, ng, cl):
        exp, sen, Rdrops, Idrops = self.getRates(enemy=enemy, NG=ng, CL=cl)
        self.DropsListWidget.addItem(f"------------------------------------------------")
        self.DropsListWidget.addItem(f"Sen - {sen}")
        self.DropsListWidget.addItem(f"EXP - {exp}")
        self.DropsListWidget.addItem(f"------------------------------------------------")
        for lot in Rdrops:
            for item in lot:
                if item[2] != 0:
                    self.DropsListWidget.addItem(f"{item[2]} {Lots.ResourceRef[item[0]]} - {item[1]}% chance")
        self.DropsListWidget.addItem(f"------------------------------------------------")

    def getStat(self, enemy, AP=1, NG=0, CL=False, DB=False, Time=1, Mode=0, attack=5000010):

        innerEnemyRef = {
            1: 71001000,
            2: 50601010,
            3: 54000000}
        
        if Mode == 0 and enemy not in [1, 2, 3]:
            self.showRates(enemy, NG, CL) # update rates if enemy isnt an inner fight or in a gauntlet/reflection

        changeEnemyForInner = None

        if enemy in [1, 2, 3]: # inner fights
            Mode = 1
            changeEnemyForInner = enemy
            enemy = innerEnemyRef[enemy]

        try:
            enemyRef = EnemyRef.EnemyRef[enemy]  # Get multipliers
            enemyAttackRate = 1

        except:
            self.showError("Please select a valid enemy")
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
                if CL:
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
        
        print(output, AP, round(enemyAttackRate, 2), attacksNeeded)
        return output, AP, round(enemyAttackRate, 2), attacksNeeded
    
    def getRates(self, enemy, NG=0, CL=False):
        enemyRef = EnemyRef.EnemyRef[enemy] # Get multipliers

        baseExp = EnemyBaseStats.Enemy_Exp_Rates[enemy] # fetch base drop rate for exp
        baseExp *= Multipliers.Clearcount_SenXP_Droprate[NG][1] # scale ng+ for exp
        baseExp *= Multipliers.Charmless_SenXP_Multiplier[CL] # scale for charmless for exp

        baseSen = EnemyBaseStats.Enemy_Sen_Rates[enemy] # fetch base drop rate for sen
        baseSen *= Multipliers.Clearcount_SenXP_Droprate[NG][0] # scale ng cycle for sen
        baseSen *= Multipliers.Charmless_SenXP_Multiplier[CL] # scale for charmless for sen

        if NG > 0:
            baseExp *= Multipliers.NGCycle_Exp_Droprate[enemyRef[0]] # scale ng+ for exp
            baseSen *= Multipliers.NGCycle_Sen_Droprate[enemyRef[0]] # scale ng+ for sen
            baseSen *= 1.25 # no idea why but sen requires a permanent multiplier in ng+

        resourceDrops = EnemyBaseStats.Enemy_ResourceLot_Drops[enemy]
        RdropList = [Lots.Resource_Item_Lots[i] for i in resourceDrops if i]

        itemDrops = EnemyBaseStats.Enemy_ItemLot_Drops[enemy]
        IdropList = [Lots.TR_Item_Lots[i] for i in itemDrops if i]
        
        return round(baseExp), round(baseSen), RdropList, IdropList
        
    def update(self):
        enemy = self.enemyIdLineEdit.text()
        if not enemy:
            try:
                enemy = EnemyRef.EntityIdRef[self.EnemyComboBox.currentIndex()]
            except:
                return
        try:
            enemy = int(enemy)
        except:
            self.showError("Please select a valid enemy")
            return
        
        attack = self.AttacklineEdit.text()
        if not attack:
            attack = 5000010
        else:
            try:
                attack = int(attack)
            except:
                self.showError("Please select a valid attack")
                return

        ng = self.ngComboBox.currentIndex()
        time = self.timeComboBox.currentIndex() + 1
        mode = self.GameModeComboBox.currentIndex()
        ap = self.APspinBox.value()
        cl = self.clCheckButton.isChecked()
        db = self.dbCheckButton.isChecked()

        self.StatsListWidget.clear()
        self.DropsListWidget.clear()
        
        result = self.getStat(enemy=enemy, NG=ng, CL=cl, DB=db, Time=time, Mode=mode, AP=ap, attack=attack)

        if result is None:
            return # skip adding values if there is an error in calculation (this is usually due to an incorrect time input)
        output, attackPower, attackRate, attacksNeeded = result

        self.StatsListWidget.addItem(f"HP - {output[0]}")
        self.StatsListWidget.addItem(f"Posture - {output[1]}")
        self.StatsListWidget.addItem(f"Damage Multiplier - x{attackRate}")
        self.StatsListWidget.addItem(f"Posture Regen - {output[2]}")
        self.StatsListWidget.addItem(f"At AP{attackPower}, it would take {attacksNeeded} attacks to kill this enemy!")
    
    def setupUi(self, Form):
        self.enemiesList = ["Tutorial Genichiro",
                        "Lady Butterfly",
                        "Gyoubu",
                        "Genichiro Ashina",
                        "Guardian Ape",
                        "Headless Ape",
                        "Brown Ape",
                        "Corrupted Monk",
                        "Emma",
                        "Isshin Ashina",
                        "Great Shinobi Owl",
                        "True Monk",
                        "Divine Dragon",
                        "Owl (Father)",
                        "Demon of Hatred",
                        "Genichiro Way of Tomoe (Silvergrass Field)",
                        "Isshin the Sword Saint",
                        "Inner Genichiro",
                        "Inner Father",
                        "Inner Isshin",
                        "Shigenori Yamauchi",
                        "Naomori Kawarada",
                        "Chained Ogre",
                        "Tenzen Yamauchi",
                        "Ako Headless",
                        "Shinobi Hunter Enshin",
                        "Juzou",
                        "Blazing Bull",
                        "Armoured Warrior",
                        "Long Arm Centipede Sen-Un",
                        "Lone Shadow Longswordsman",
                        "General Kuranosuke Matsumoto",
                        "Seven Ashina Spears - Shikibu Toshikatsu Yamauchi",
                        "Ungo Headless",
                        "Lone Shadow Masanaga the Spear-bearer",
                        "Ashina Elite - Jinsuke Saze",
                        "Shichimen Warrior (Dungeon)",
                        "Gokan Headless",
                        "Snake Eyes Shirafuji",
                        "Gachiin Headless",
                        "Tokujiro ",
                        "Mist Noble",
                        "O'Rin of the Water",
                        "Snake Eyes Shirahagi",
                        "Chained Ogre (Castle)",
                        "Lone Shadow Vilehand",
                        "Long-arm Centipede Giraffe",
                        "Shichimen Warrior (Ashina Depths)",
                        "Shigekichi of the Red Guard",
                        "Chained Ogre (Outskirts)",
                        "Sakura Bull of the Palace",
                        "Lone Shadow Masanaga the Spear-bearer (Hirata 2)",
                        "Juzou (Hirata 2)",
                        "Seven Ashina Spears - Shume Masaji Oniwa",
                        "Ashina Elite - Ujinari Mizuo",
                        "Okami Leader Shizu",
                        "Shichimen Warrior (Fountainhead)",
                        "Yashariku Headless",
                        "Yashariku Headless Phantom"]

        Form.setObjectName("Form")
        Form.resize(441, 379)
        self.timeComboBox = QtWidgets.QComboBox(Form)
        self.timeComboBox.setGeometry(QtCore.QRect(70, 110, 101, 22))
        self.timeComboBox.setObjectName("timeComboBox")
        self.timeComboBox.activated[str].connect(self.update)
        self.timeComboBox.addItem("")
        self.timeComboBox.addItem("")
        self.timeComboBox.addItem("")
        self.timeComboBox.addItem("")
        self.clCheckButton = QtWidgets.QCheckBox(Form)
        self.clCheckButton.setGeometry(QtCore.QRect(200, 80, 70, 21))
        self.clCheckButton.setObjectName("clCheckButton")
        self.clCheckButton.stateChanged.connect(self.update)
        self.dbCheckButton = QtWidgets.QCheckBox(Form)
        self.dbCheckButton.setGeometry(QtCore.QRect(200, 110, 70, 21))
        self.dbCheckButton.setObjectName("dbCheckButton")
        self.dbCheckButton.stateChanged.connect(self.update)
        self.ngComboBox = QtWidgets.QComboBox(Form)
        self.ngComboBox.setGeometry(QtCore.QRect(70, 80, 101, 22))
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
        self.enemyIdLineEdit.setGeometry(QtCore.QRect(70, 50, 211, 20))
        self.enemyIdLineEdit.setToolTip("")
        self.enemyIdLineEdit.setObjectName("enemyIdLineEdit")
        self.enemyIdLineEdit.returnPressed.connect(self.update)
        self.EnemyComboBox = QtWidgets.QComboBox(Form)
        self.EnemyComboBox.setGeometry(QtCore.QRect(70, 20, 341, 22))
        self.EnemyComboBox.setToolTip("")
        self.EnemyComboBox.setEditable(True)
        self.EnemyComboBox.setObjectName("EnemyComboBox")
        self.EnemyComboBox.activated[str].connect(self.update)

        for _ in range(len(self.enemiesList)):
            self.EnemyComboBox.addItem("") # add enough blank entries for all enemies
       
        self.EnemyLabel = QtWidgets.QLabel(Form)
        self.EnemyLabel.setGeometry(QtCore.QRect(20, 20, 41, 21))
        self.EnemyLabel.setObjectName("EnemyLabel")
        self.EntityIDLabel = QtWidgets.QLabel(Form)
        self.EntityIDLabel.setGeometry(QtCore.QRect(20, 50, 51, 21))
        self.EntityIDLabel.setWhatsThis("")
        self.EntityIDLabel.setObjectName("EntityIDLabel")
        self.NGLabel = QtWidgets.QLabel(Form)
        self.NGLabel.setGeometry(QtCore.QRect(20, 80, 51, 21))
        self.NGLabel.setWhatsThis("")
        self.NGLabel.setObjectName("NGLabel")
        self.TimeLabel = QtWidgets.QLabel(Form)
        self.TimeLabel.setGeometry(QtCore.QRect(20, 110, 51, 21))
        self.TimeLabel.setWhatsThis("")
        self.TimeLabel.setObjectName("TimeLabel")
        self.line = QtWidgets.QFrame(Form)
        self.line.setGeometry(QtCore.QRect(176, 80, 16, 61))
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(Form)
        self.line_2.setGeometry(QtCore.QRect(20, 130, 391, 21))
        self.line_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(Form)
        self.line_3.setGeometry(QtCore.QRect(280, 50, 20, 91))
        self.line_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setObjectName("line_3")
        self.APLabel = QtWidgets.QLabel(Form)
        self.APLabel.setGeometry(QtCore.QRect(300, 80, 71, 21))
        self.APLabel.setObjectName("APLabel")
        self.APspinBox = QtWidgets.QSpinBox(Form)
        self.APspinBox.setGeometry(QtCore.QRect(370, 80, 42, 22))
        self.APspinBox.setMinimum(1)
        self.APspinBox.setObjectName("APspinBox")
        self.APspinBox.valueChanged.connect(self.update)
        self.AttacklineEdit = QtWidgets.QLineEdit(Form)
        self.AttacklineEdit.setGeometry(QtCore.QRect(300, 110, 111, 20))
        self.AttacklineEdit.setObjectName("AttacklineEdit")
        self.AttacklineEdit.returnPressed.connect(self.update)
        self.GameModeComboBox = QtWidgets.QComboBox(Form)
        self.GameModeComboBox.setGeometry(QtCore.QRect(300, 50, 111, 22))
        self.GameModeComboBox.setObjectName("GameModeComboBox")
        self.GameModeComboBox.activated[str].connect(self.update)
        self.GameModeComboBox.addItem("")
        self.GameModeComboBox.addItem("")
        self.GameModeComboBox.addItem("")
        self.DataTabs = QtWidgets.QTabWidget(Form)
        self.DataTabs.setGeometry(QtCore.QRect(20, 150, 401, 211))
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
        item = QtWidgets.QListWidgetItem()
        self.StatsListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.StatsListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.StatsListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.StatsListWidget.addItem(item)
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
        item = QtWidgets.QListWidgetItem()
        self.DropsListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.DropsListWidget.addItem(item)
        self.DropsScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.DataTabs.addTab(self.tab_2, "")

        self.retranslateUi(Form)
        self.EnemyComboBox.setCurrentIndex(-1)
        self.DataTabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Sekiro Stat Calculator"))
        self.timeComboBox.setToolTip(_translate("Form", "Some areas only use morning (used as default) and night + demon bell. Eg. Silvergrass Field"))
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

        for index, i in enumerate(self.enemiesList):
            self.EnemyComboBox.setItemText(index, _translate("Form", f"{i}")) # add all enemies to the combobox

        self.EnemyLabel.setToolTip(_translate("Form", "List of common bosses and minibosses"))
        self.EnemyLabel.setText(_translate("Form", "Enemy:"))
        self.EntityIDLabel.setToolTip(_translate("Form", "Optional override for enemies not listed above"))
        self.EntityIDLabel.setText(_translate("Form", "Entity ID:"))
        self.NGLabel.setToolTip(_translate("Form", "NG+ Scaling for calculations"))
        self.NGLabel.setText(_translate("Form", "NG Cycle:"))
        self.TimeLabel.setToolTip(_translate("Form", "Game Time"))
        self.TimeLabel.setText(_translate("Form", "Time:"))
        self.APLabel.setToolTip(_translate("Form", "Player Attack Power"))
        self.APLabel.setText(_translate("Form", "Attack Power:"))
        self.AttacklineEdit.setToolTip(_translate("Form", "ID of the player attack used when calculating how many attacks a kill would take"))
        self.AttacklineEdit.setPlaceholderText(_translate("Form", "Attack ID *Optional"))
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
    Form = QtWidgets.QWidget()
    ui = Window()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
