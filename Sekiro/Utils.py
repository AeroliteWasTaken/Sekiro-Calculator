try:
    from Sekiro import Player, Multipliers, Enemy, Lots, Reference
except ModuleNotFoundError:
    import Player, Multipliers, Enemy, Lots, Reference
import copy
from math import floor, ceil

class CalcFunctions():
    @staticmethod
    def mult(multiplier, val):
        return [[x * multiplier for x in item] if isinstance(item, list) else item * multiplier for item in val]

    @staticmethod
    def div(val, multiplier):
        return [[ceil(x / multiplier) for x in item] if isinstance(item, list) else ceil(item / multiplier) for item in val]

    @staticmethod
    def multiplyRecursive(data, multiplier):
        if isinstance(data, list):  # If it's a list, apply the function to each element
            return [CalcFunctions.multiplyRecursive(item, multiplier) for item in data]
        else:  # If it's not a list, just multiply the value
            return data * multiplier

    @staticmethod
    def floatConv(nested_list):
        result = []
        for item in nested_list:
            if isinstance(item, list):
                result.append(CalcFunctions.floatConv(item))
            elif isinstance(item, float):
                result.append(int(item))
            else:
                result.append(item)
        return result
        
    @staticmethod
    def resolveInnerEnemy(enemy):
        if enemy in [1, 2, 3]:
            return Reference.InnerEnemyRef[enemy], enemy  # mapped enemy, original inner id
        return enemy, None
    
class SekiroFunctions():
    @staticmethod
    def getStats(enemy, NG=0, CL=False, DB=False, Time=1, Mode=0, AP=1, attack=5000010):
        if Mode == 0 and enemy in [1, 2, 3]:
            Mode = 1 # inner fights cant have a "Normal" mode, so default to Reflection

        enemy, changeEnemyForInner = CalcFunctions.resolveInnerEnemy(enemy)

        try:
            enemyRef = Enemy.EnemyScaling[enemy]  # Get multipliers
            enemyAttackRate = 1 # start with a damage multiplier of 1

        except:
            return 'EnemyNotFound'
        
        enemyStat = copy.deepcopy(Enemy.EnemyStats[enemy]) # get all stats

        if enemy == 71001000: # if enemy is genichiro, add his other phases (separate by default)
            enemyStat[0] = [enemyStat[0], enemyStat[0], copy.deepcopy(Enemy.EnemyStats[71100000])[0]]
            enemyStat[1] = [enemyStat[1], enemyStat[1], copy.deepcopy(Enemy.EnemyStats[71100000])[1]]

        else:
            if enemy in Multipliers.Phase_HP_Multipliers.keys(): # if enemy is among named and listed minibosses/bosses
                enemyStat[0] = CalcFunctions.mult(enemyStat[0], Multipliers.Phase_HP_Multipliers[enemy]) # multiply different phases hp

            if enemy in Multipliers.Phase_Posture_Multipliers.keys(): # if enemy is among named and listed minibosses/bosses
                enemyStat[1] = CalcFunctions.mult(enemyStat[1], Multipliers.Phase_Posture_Multipliers[enemy]) # multiply different phases posture

        if Mode == 0: # normal
            try:
                timeOffset = Multipliers.Time_Offset[DB][Time]  # find offset for time + demon bell 
                enemyStat = CalcFunctions.multiplyRecursive(enemyStat, Multipliers.Clearcount_HP[CL][NG])  # scale ng
                enemyAttackRate *= Multipliers.Clearcount_Dmg[CL][NG]  # scale ng for attack

                if CL and NG == 0:
                    timeOffset += 700  # account for new game CL scaling
                if NG > 0:
                    enemyStat = CalcFunctions.multiplyRecursive(enemyStat, Multipliers.NGCycle_HP[enemyRef[0] + timeOffset])  # correct for ng+ scaling
                    enemyAttackRate *= Multipliers.NGCycle_Attack[enemyRef[0] + timeOffset]  # correct for ng+ scaling (attack multiplier)
                if CL and enemyRef[2]: # if enemy has charmless type scaling
                    enemyStat = CalcFunctions.multiplyRecursive(enemyStat, Multipliers.Charmless_Muliplier_By_Type[enemyRef[2]])  # increase stats based off of enemy type
                    
                enemyStat = CalcFunctions.multiplyRecursive(enemyStat, Multipliers.AreaScale_HP[enemyRef[1] + timeOffset])  # multiply area scaling
                enemyAttackRate *= Multipliers.AreaScale_Attack[enemyRef[1] + timeOffset]  # multiply area scaling (attack multiplier)

            except:
                # Selected Game Time is invalid for this enemy
                return

        else:
            AP = 14 # set ap to 14 since it's fixed in reflections and gauntlets
            if changeEnemyForInner: 
                enemy = changeEnemyForInner # change override reference for inner fights after calculating with base enemy

            if Mode == 1:  # reflection
                if enemy in Reference.ReflectionOverride.keys(): # if enemy is listed as an exception or if it is an inner fight
                    override = Reference.ReflectionOverride[enemy][(CL, DB)] # get scaling IDs from said exceptions
                else:
                    override = Reference.ReflectionOverride[0][(CL, DB)] # use default

            elif Mode == 2:  # mortal journey
                if enemy in Reference.MortalJourneyOverride.keys(): # if enemy is listed as an exception or if it is an inner fight
                    override = Reference.MortalJourneyOverride[enemy][(CL, DB)] # get scaling IDs from said exceptions
                else:
                    override = Reference.MortalJourneyOverride[0][(CL, DB)] # use default
            #Multiplying Scaling
            enemyStat = CalcFunctions.mult(Multipliers.AreaScale_HP[override[0]], enemyStat) 
            enemyStat = CalcFunctions.mult(Multipliers.NGCycle_HP[override[1]], enemyStat) 
            enemyStat = CalcFunctions.mult(Multipliers.Charmless_Muliplier_By_Type[enemyRef[2]], enemyStat) 

        enemyStat = CalcFunctions.floatConv(enemyStat)
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
        attacksNeeded = SekiroFunctions.findAttacksNeeded(enemyStat[0], SekiroFunctions.getPlayerDmg(AP=AP, attack=attack))

        return output, AP, round(enemyAttackRate, 2), attacksNeeded

    @staticmethod
    def getDropLists(enemy, DB=False, Time=1, soulBalloon=False, pilgrimageBalloon=False):
        RdropList = []
        NdropList = []
        IdropList = []

        ninsatuDrops = Enemy.Enemy_NinsatuLot_Drops[enemy]
        if ninsatuDrops[0] is not None:
            NdropList = [Lots.Resource_Item_Lots[i] for i in ninsatuDrops if i]

        resourceDrops = list(Enemy.Enemy_ResourceLot_Drops[enemy])
        if resourceDrops[0] is not None:
            if (soulBalloon or pilgrimageBalloon) and resourceDrops[1] in Lots.Resource_Item_Lots:
                resourceDrops.append(resourceDrops[1]+1) # add the next resourceitemlot which contains drops for isAddLottery, triggered on stateinfo 345
            RdropList = [Lots.Resource_Item_Lots[i] for i in resourceDrops if i]

        itemDrops = copy.deepcopy(Enemy.Enemy_ItemLot_Drops[enemy])
        if itemDrops[0] is not None: # if non mandatory itemlot drop exists
            newLot = itemDrops[0] + Reference.ItemLot_Time_Offset[DB][Time] # add extra itemlot for time of day (separate from default, which is always on)
            if newLot in Lots.Item_Lots:
                itemDrops.append(newLot) # only add if demon bell lots exist
            else:
                return # dont add drops if time is unsupported
        IdropList = [Lots.Item_Lots[i] for i in itemDrops if i]

        return NdropList, RdropList, IdropList

    @staticmethod
    def getExpSen(enemy, NG=False, CL=False, wealthBalloon=False, pilgrimageBalloon=False, virtuousDeed=False, mostVirtuousDeed=False):
        enemyRef = Enemy.EnemyScaling[enemy] # Get multipliers

        if enemy in Enemy.Boss_Exp_Rates.keys():
            baseExp = Enemy.Boss_Exp_Rates[enemy] # fetch base drop rate for exp
        else:
            baseExp = Enemy.Enemy_Exp_Rates[enemy] # fetch base drop rate for exp
        baseExp *= Multipliers.Clearcount_SenXP_Droprate[NG][1] # scale ng+ for exp
        baseExp *= Multipliers.Charmless_SenXP_Multiplier[CL] # scale for charmless for exp

        baseSen = Enemy.Enemy_Sen_Rates[enemy] # fetch base drop rate for sen
        baseSen *= Multipliers.Clearcount_SenXP_Droprate[NG][0] # scale ng cycle for sen
        baseSen *= Multipliers.Charmless_SenXP_Multiplier[CL] # scale for charmless for sen

        if NG > 0:
            baseExp *= Multipliers.NGCycle_Exp_Droprate[enemyRef[0]] # scale ng+ for exp
            baseSen *= Multipliers.NGCycle_Sen_Droprate[enemyRef[0]] # scale ng+ for sen

        if wealthBalloon:
            baseSen *= 1.5 # account for Mibu Balloon of Wealth

        if pilgrimageBalloon:
            baseSen *= 1.5 # account for Mibu Pilgrimage Balloon

        if mostVirtuousDeed:
            baseSen *= 1.25 

        elif virtuousDeed:
            baseSen *= 1.125 # is ignored if Most Virtuous Deed is active too since it replaces the buff

        return baseSen, baseExp

    @staticmethod
    def getPlayerDmg(AP=1, attack=5000010):
        if attack in [900, 901, 903]: # jump kick
            baseDmg = 10
        elif attack == 3520: # throwing oil
            return 1
        else:
            baseDmg = 40 # base for most attacks and CAs
        baseDmg *= Player.Player_Attack_Power.get(AP, 1) # multiply by AP
        atkCorrect = Player.Player_Attacks[attack][2] # get atkPhysCorrection

        if atkCorrect > 0:
            baseDmg *= Player.Player_Attacks[attack][2]/100 # multiply if possible

        return ceil(baseDmg)

    @staticmethod
    def findAttacksNeeded(hp, dmg):
        out = []
        if isinstance(hp, list):
            for i in hp:
                out.append(str(ceil(i/dmg)))
            return ', '.join(out)
        return str(ceil(hp/dmg))

    @staticmethod
    def parseIChance(weight, **args):
        buffs = Multipliers.Item_Discovery_Buffs
        buff = 1

        for key in ['possessionBalloon', 'pilgrimageBalloon']:
            if args.get(key):
                buff += buffs[key]

        if args.get('mostVirtuousDeed'):
            buff += buffs['mostVirtuousDeed']
        elif args.get('virtuousDeed'):
            buff += buffs['virtuousDeed']

        chance = round(100 * (weight * buff) / ((weight * buff) + (1000 - weight)))
        return 100 if chance > 100 else chance

    @staticmethod
    def parseRChance(chance, resource, **args):
        buff = 1

        if resource == 1: # spirit emblems
            if args.get('spiritBalloon'):
                buff += 0.5
            if args.get('pilgrimageBalloon'):
                buff += 0.5 # both spirit emblem increasing effects are +50

        chance = round(1000 * (chance * buff) / ((chance * buff) + (1000 - chance)))
        return 100 if chance > 100 else chance

    @staticmethod
    def calculateEXP(n):
        val = 0
        for i in range(n):
            if i < 24:
                add = 0.1*(i+70)**2+10
            else:
                add = 0.1*(i+70)**2+10+0.02*(i+70)**2*(i-24)
            val += floor(add)
                
        return int(val)

