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
            return Reference.InnerEnemy[enemy], enemy  # mapped enemy, original inner id
        return enemy, None
    
class SekiroFunctions():
    @staticmethod
    def getStats(enemy, NG=0, CL=False, DB=False, Time=1, Mode=0, AP=1, attack=5000010):
        if Mode == 0 and enemy in [1, 2, 3]:
            Mode = 1 # inner fights cant have a "Normal" mode, so default to Reflection

        enemy, changeEnemyForInner = CalcFunctions.resolveInnerEnemy(enemy)

        try:
            enemyRef = Enemy.Scaling[enemy]  # Get multipliers
            enemyAttackRate = 1 # start with a damage multiplier of 1

        except:
            return 'EnemyNotFound'
        
        enemyStat = copy.deepcopy(Enemy.Stats[enemy]) # get all stats

        if enemy == 71001000: # if enemy is genichiro, add his other phases (separate by default)
            enemyStat[0] = [enemyStat[0], enemyStat[0], copy.deepcopy(Enemy.Stats[71100000])[0]]
            enemyStat[1] = [enemyStat[1], enemyStat[1], copy.deepcopy(Enemy.Stats[71100000])[1]]

        else:
            if enemy in Multipliers.PhaseChangeHP.keys(): # if enemy is among named and listed minibosses/bosses
                enemyStat[0] = CalcFunctions.mult(enemyStat[0], Multipliers.PhaseChangeHP[enemy]) # multiply different phases hp

            if enemy in Multipliers.PhaseChangePosture.keys(): # if enemy is among named and listed minibosses/bosses
                enemyStat[1] = CalcFunctions.mult(enemyStat[1], Multipliers.PhaseChangePosture[enemy]) # multiply different phases posture

        if Mode == 0: # normal
            try:
                timeOffset = Multipliers.TimeOffset[DB][Time]  # find offset for time + demon bell 
                enemyStat = CalcFunctions.multiplyRecursive(enemyStat, Multipliers.ClearcountHP[CL][NG])  # scale ng
                enemyAttackRate *= Multipliers.ClearcountDMG[CL][NG]  # scale ng for attack

                if CL and NG == 0:
                    timeOffset += 700  # account for new game CL scaling
                if NG > 0:
                    enemyStat = CalcFunctions.multiplyRecursive(enemyStat, Multipliers.NGCycleHP[enemyRef[0] + timeOffset])  # correct for ng+ scaling
                    enemyAttackRate *= Multipliers.NGCycleAttack[enemyRef[0] + timeOffset]  # correct for ng+ scaling (attack multiplier)
                if CL and enemyRef[2]: # if enemy has charmless type scaling
                    enemyStat = CalcFunctions.multiplyRecursive(enemyStat, Multipliers.CharmlessByType[enemyRef[2]])  # increase stats based off of enemy type
                    
                enemyStat = CalcFunctions.multiplyRecursive(enemyStat, Multipliers.AreaScaleHP[enemyRef[1] + timeOffset])  # multiply area scaling
                enemyAttackRate *= Multipliers.AreaScaleAttack[enemyRef[1] + timeOffset]  # multiply area scaling (attack multiplier)

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
            enemyStat = CalcFunctions.mult(Multipliers.AreaScaleHP[override[0]], enemyStat) 
            enemyStat = CalcFunctions.mult(Multipliers.NGCycleHP[override[1]], enemyStat) 
            enemyStat = CalcFunctions.mult(Multipliers.CharmlessByType[enemyRef[2]], enemyStat) 

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
        attacksNeeded = SekiroFunctions.findAttacksNeeded(enemyStat[0], SekiroFunctions.getDamage(AP=AP, attack=attack))

        return {
            "HP": output[0],
            "Posture": output[1],
            "Posture Regen": output[2],
            "Damage Multiplier": round(enemyAttackRate, 2),
            f"Max hits to kill at AP{AP}": attacksNeeded}

    @staticmethod
    def getDrops(enemy, DB=False, Time=1, soulBalloon=False, pilgrimageBalloon=False, possessionBalloon=False, spiritBalloon=False, virtuousDeed=False, mostVirtuousDeed=False):
        Ndrops, Rdrops, Idrops = SekiroFunctions.getDropLists(enemy, DB, Time, soulBalloon, pilgrimageBalloon)
        opts = {
            'possessionBalloon': possessionBalloon,
            'spiritBalloon': spiritBalloon,
            'soulBalloon': soulBalloon,
            'pilgrimageBalloon': pilgrimageBalloon,
            'virtuousDeed': virtuousDeed,
            'mostVirtuousDeed': mostVirtuousDeed}
        
        output = []

        for lot in Ndrops:
            for item in lot:
                if item[2] != 0:
                    output.append({"count": item[2], "name": Reference.ResourceName[item[0]], "chance": "on deathblow"})

        for lot in Rdrops:
            for item in lot:
                if item[2] != 0:
                    chance = SekiroFunctions.parseRChance(item[1], item[0], **opts)
                    output.append({"count": item[2], "name": Reference.ResourceName[item[0]], "chance": f"- {chance}% chance"})

        for lot in Idrops:
            for item in lot:
                if item[2] != 0:                  
                    chance = SekiroFunctions.parseIChance(item[1], **opts)
                    output.append({"count": item[2], "name": Reference.ItemName[item[0]], "chance": f"- {chance}% chance"})
        
        return output

    @staticmethod
    def getDropLists(enemy, DB=False, Time=1, soulBalloon=False, pilgrimageBalloon=False):
        RdropList = []
        NdropList = []
        IdropList = []

        ninsatuDrops = Enemy.NinsatuDrops[enemy]
        if ninsatuDrops[0] is not None:
            NdropList = [Lots.Resources[i] for i in ninsatuDrops if i]

        resourceDrops = list(Enemy.ResourceDrops[enemy])
        if resourceDrops[0] is not None:
            if (soulBalloon or pilgrimageBalloon) and resourceDrops[1] in Lots.Resources:
                resourceDrops.append(resourceDrops[1]+1) # add the next resourceitemlot which contains drops for isAddLottery, triggered on stateinfo 345
            RdropList = [Lots.Resources[i] for i in resourceDrops if i]

        itemDrops = copy.deepcopy(Enemy.ItemDrops[enemy])
        if itemDrops[0] is not None: # if non mandatory itemlot drop exists
            newLot = itemDrops[0] + Reference.ItemLotTimeOffset[DB][Time] # add extra itemlot for time of day (separate from default, which is always on)
            if newLot in Lots.Items:
                itemDrops.append(newLot) # only add if demon bell lots exist
            else:
                pass # dont add drops if time is unsupported
        IdropList = [Lots.Items[i] for i in itemDrops if i]

        return NdropList, RdropList, IdropList

    @staticmethod
    def getExpSen(enemy, NG=False, CL=False, wealthBalloon=False, pilgrimageBalloon=False, virtuousDeed=False, mostVirtuousDeed=False):
        enemyRef = Enemy.Scaling[enemy] # Get multipliers

        if enemy in Enemy.BossExpRates.keys():
            baseExp = Enemy.BossExpRates[enemy] # fetch base drop rate for exp
        else:
            baseExp = Enemy.ExpRates[enemy] # fetch base drop rate for exp
        baseExp *= Multipliers.ClearcountDroprate[NG][1] # scale ng+ for exp
        baseExp *= Multipliers.CharmlessSenExp[CL] # scale for charmless for exp

        baseSen = Enemy.SenRates[enemy] # fetch base drop rate for sen
        baseSen *= Multipliers.ClearcountDroprate[NG][0] # scale ng cycle for sen
        baseSen *= Multipliers.CharmlessSenExp[CL] # scale for charmless for sen

        if NG > 0:
            baseExp *= Multipliers.NGCycleExp[enemyRef[0]] # scale ng+ for exp
            baseSen *= Multipliers.NGCycleSen[enemyRef[0]] # scale ng+ for sen

        if wealthBalloon:
            baseSen *= 1.5 # account for Mibu Balloon of Wealth

        if pilgrimageBalloon:
            baseSen *= 1.5 # account for Mibu Pilgrimage Balloon

        if mostVirtuousDeed:
            baseSen *= 1.25 

        elif virtuousDeed:
            baseSen *= 1.125 # is ignored if Most Virtuous Deed is active too since it replaces the buff

        if baseExp == int(baseExp):
            baseExp += 0.0001 # make it so ceil() can actually increase it by 1 in cases where you end up with .0

        return {"Sen": ceil(baseSen), "EXP": ceil(baseExp)}

    @staticmethod
    def getDamage(attack=5000010, AP=1, mode="Player", dmgType='atkPhys'):
        if mode == "Player":
            baseDmg = Player.Attacks[attack][dmgType]
            atkCorrect = Player.Attacks[attack][f'{dmgType}Correction'] # get multiplier
            if baseDmg == 0 and atkCorrect > 0: 
                baseDmg = 40 # base for most player attacks and CA's

            if dmgType == 'atkStam':
                baseDmg *= 2

            baseDmg *= Player.AttackPower.get(AP, 1) # multiply by AP
            
            if atkCorrect > 0:
                baseDmg *= atkCorrect/100 # multiply if possible
        
        elif mode == "Enemy":
            baseDmg = Enemy.Attacks[attack][dmgType]
            atkCorrect = Enemy.Attacks[attack][f'{dmgType}Correction'] # get multiplier

            if atkCorrect > 0:
                baseDmg *= atkCorrect/100 # multiply if possible

        return ceil(baseDmg)
    
    @staticmethod
    def parseDamage(attack=5000010, AP=1, mode="Player"):
        output = {}
        dmgTypes = {
            'Physical': 'atkPhys',
            'Posture': 'atkStam',
            'Magic': 'atkMag',
            'Fire': 'atkFire',
            'Lightning': 'atkThun',
            'Piercing (Dark)': 'atkDark'}
        
        if mode == "Player":
            output['Attack Type'] = Reference.AttackAttribute[Player.Attacks[attack]['atkAttribute']]
            output['Effect Type'] = Reference.SpecialAttribute[Player.Attacks[attack]['spAttribute']]
        elif mode == 'Enemy':
            output['Attack Type'] = Reference.AttackAttribute[Enemy.Attacks[attack]['atkAttribute']]
            output['Effect Type'] = Reference.SpecialAttribute[Enemy.Attacks[attack]['spAttribute']]

        for key, val in dmgTypes.items():
            dmg = SekiroFunctions.getDamage(attack=attack, AP=AP, mode=mode, dmgType=val)
            output[key] = dmg

        return output

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
        buffs = Multipliers.ItemDiscovery
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

    """Calculate EXP required to get a skill point at a given level."""
    @staticmethod
    def calculateEXP(lvl):
        a = 0.1
        b = 10
        c = 0.02
        d = 94

        if lvl+69 < d**2:
            val = a*(lvl+69)**2+b
        else:
            val = a*(lvl+69)+b*(lvl+69)*2+c*(lvl+69)*2*(lvl+69)*2
                
        return int(floor(val))
    
    """Return total EXP required to get to this level."""
    @staticmethod
    def totalEXP(lvl):
        val = 0
        for i in range(1, lvl+1):
            val += SekiroFunctions.calculateEXP(i)
        return val

