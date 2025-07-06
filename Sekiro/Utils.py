"""This module contains most of the processing and calculation functions for the calculator.
    CalcFunctions is mostly for math calculations, while SekiroFunctions is for processing data.
    The docstrings below were written with Qodo-Gen cuz I'm lazy as fuck"""

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
    """
    Calculate and return the stats for a specified enemy.

    This static method computes the health, posture, posture regeneration, and damage multiplier
    for an enemy based on various game modes and conditions such as New Game Plus (NG+), Charmless
    mode, and Demon Bell activation. It adjusts the stats using multipliers for different phases,
    areas, and enemy types. The method also calculates the maximum number of hits needed to defeat
    the enemy at a given attack power.

    Args:
        enemy (int): The ID of the enemy to calculate stats for.
        NG (int, optional): The New Game cycle number. Defaults to 0.
        CL (bool, optional): Whether Charmless mode is active. Defaults to False.
        DB (bool, optional): Whether the Demon Bell is active. Defaults to False.
        Time (int, optional): The time of day affecting scaling. Defaults to 1. (Morning)
        Mode (int, optional): The game mode, where 0 is Normal, 1 is Reflection, and 2 is Mortal Journey. Defaults to 0.
        AP (int, optional): The attack power level. Defaults to 1.
        attack (int, optional): The attack identifier. Defaults to 5000010.

    Returns:
        dict: A dictionary containing the calculated stats, including HP, Posture, Posture Regen,
              Damage Multiplier, and Max hits to kill at the specified attack power.
    """
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
                timeOffset = Reference.TimeOffset[DB][Time]  # find offset for time + demon bell 
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

    """
    Retrieve item drops for a specified enemy, considering various effects and conditions.

    This static method calculates and returns a list of item drops for an enemy,
    taking into account specific effects such as 'possessionBalloon' and 'virtuousDeed'.
    It adjusts the drop chances based on these effects and the time of day.

    Args:
        enemy: The NpcParamId for the enemy whose drops are to be retrieved.
        dropLists (list, optional): For if you have predefined drop lists for the enemy.
            Uses getDropLists() if parameter is None
        DB (bool, optional): Indicates if the demon bell is active. Defaults to False.
        Time (int, optional): The time of day affecting item drops. Defaults to 1.
        effects (dict, optional): A dictionary of effects that may influence drop rates. Defaults to None.

    Returns:
        list: A list of dictionaries, each containing the count, name, and chance of an item drop.
    """
    @staticmethod
    def getDrops(enemy, dropLists: list = None, DB=False, Time=1, effects: dict = None):
        effects = effects or {}
        possessionBalloon = effects.get('possessionBalloon', False)
        spiritBalloon = effects.get('spiritBalloon', False)
        soulBalloon = effects.get('soulBalloon', False)
        pilgrimageBalloon = effects.get('pilgrimageBalloon', False)
        virtuousDeed = effects.get('virtuousDeed', False)
        mostVirtuousDeed = effects.get('mostVirtuousDeed', False)

        if dropLists:
            Ndrops, Rdrops, Idrops = dropLists # make sure the order is correct
        else:
            Ndrops, Rdrops, Idrops = SekiroFunctions.getDropLists(enemy, DB, Time, {"soulBalloon": soulBalloon, "pilgrimageBalloon": pilgrimageBalloon})

        opts = {
            'possessionBalloon': possessionBalloon,
            'spiritBalloon': spiritBalloon,
            'soulBalloon': soulBalloon,
            'pilgrimageBalloon': pilgrimageBalloon,
            'virtuousDeed': virtuousDeed,
            'mostVirtuousDeed': mostVirtuousDeed}
        
        output = []

        for lot in Ndrops:
            if isinstance(lot, str):
                print(lot)
                continue
            for item in lot:
                if item[2] != 0:
                    output.append({"Count": item[2], "Name": Reference.ResourceName[item[0]], "Chance": f"on deathblow"})

        for lot in Rdrops:
            if isinstance(lot, str):
                print(lot)
                continue
            for item in lot:
                if item[2] != 0:
                    chance = SekiroFunctions.parseRChance(item[1], item[0], **opts)
                    output.append({"Count": item[2], "Name": Reference.ResourceName[item[0]], "Chance": f"{chance}%"})

        for lot in Idrops:
            if isinstance(lot, str):
                print(lot)
                continue
            for item in lot:
                if item[2] != 0:                  
                    chance = SekiroFunctions.parseIChance(item[1], **opts)
                    output.append({"Count": item[2], "Name": Reference.ItemName[item[0]], "Chance": f"{chance}%"})
        
        return output

    """
    Retrieve drop lists for a specified enemy, considering various effects and conditions.

    This method calculates and returns three types of drop lists: Ninsatu, Resource, and Item drops.
    It takes into account specific effects such as 'soulBalloon' and 'pilgrimageBalloon', and adjusts
    the drop lists based on the time of day and whether the demon bell is active.

    Args:
        enemy: The NpcParamId for the enemy whose drop lists are to be retrieved.
        DB (bool, optional): Indicates if the demon bell is active. Defaults to False.
        Time (int, optional): The time of day affecting item drops. Defaults to 1.
        effects (dict, optional): A dictionary of effects that may influence drop rates. Defaults to None.

    Returns:
        tuple: A tuple containing three lists - NdropList, RdropList, and IdropList, representing
                Ninsatu, Resource, and Item drops respectively.
    """
    @staticmethod
    def getDropLists(enemy, DB=False, Time=1, effects: dict = None):
        effects = effects or {}
        soulBalloon = effects.get('soulBalloon', False)
        pilgrimageBalloon = effects.get('pilgrimageBalloon', False)

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

        itemDrops = copy.deepcopy(Enemy.ItemDrops[enemy])
        if itemDrops[0] is not None: # if non mandatory itemlot drop exists
            newLot = itemDrops[0] + Reference.ItemLotTimeOffset[DB][Time] # add extra itemlot for time of day (separate from default, which is always on)
            if newLot in Lots.Items:
                itemDrops.append(newLot) # only add if time lots exist
            else:
                pass # dont add drops if time is unsupported

        NdropList: list
        RdropList: list
        IdropList: list
        if ninsatuDrops[0] is not None:
            for item in ninsatuDrops:
                if item:
                    try:
                        NdropList.append(Lots.Resources[item])
                    except KeyError:
                        NdropList.append(f"[KeyError] ResourceLot {item} does not exist")
        
        if resourceDrops[0] is not None:
            for item in resourceDrops:
                if item:
                    try:
                        RdropList.append(Lots.Resources[item])
                    except KeyError:
                        RdropList.append(f"[KeyError] ResourceLot {item} does not exist")

        for item in itemDrops:
            if item:
                try:
                    IdropList.append(Lots.Items[item])
                except KeyError:
                    IdropList.append(f"[KeyError] ItemLot {item} does not exist")

        return NdropList, RdropList, IdropList

    """
    Calculate the amount of Sen dropped by an enemy based on various factors.

    Args:
        enemy (int): The NpcParamId for the enemy.
        NG (int, optional): The New Game cycle number. Defaults to 0 aka NG.
        CL (bool, optional): Whether the Charmless mode is active. Defaults to False.
        effects (dict, optional): A dictionary of active effects that can influence Sen drop rates.
            Possible keys include 'wealthBalloon', 'pilgrimageBalloon', 'virtuousDeed', and 'mostVirtuousDeed'.

    Returns:
        int: The calculated amount of Sen dropped by the enemy.
    """
    @staticmethod
    def getSen(enemy, NG=0, CL=False, effects: dict = None):
        effects = effects or {}
        wealthBalloon = effects.get('wealthBalloon', False)
        pilgrimageBalloon = effects.get('pilgrimageBalloon', False)
        virtuousDeed = effects.get('virtuousDeed', False)
        mostVirtuousDeed = effects.get('mostVirtuousDeed', False)

        enemyRef = Enemy.Scaling[enemy] # Get multipliers

        baseSen = Enemy.SenRates[enemy] # fetch base drop rate for sen
        baseSen *= Multipliers.ClearcountDroprate[NG][0] # scale ng cycle for sen
        baseSen *= Multipliers.CharmlessSenExp[CL] # scale for charmless for sen

        if NG > 0:
            baseSen *= Multipliers.NGCycleSen[enemyRef[0]] # scale ng+ for sen

        if wealthBalloon:
            baseSen *= 1.5 # account for Mibu Balloon of Wealth

        if pilgrimageBalloon:
            baseSen *= 1.5 # account for Mibu Pilgrimage Balloon

        if mostVirtuousDeed:
            baseSen *= 1.25 

        elif virtuousDeed:
            baseSen *= 1.125 # is ignored if Most Virtuous Deed is active too since it replaces the buff

        return ceil(baseSen)
    
    """
    Calculate the experience points (EXP) gained from defeating an enemy.

    This method computes the EXP based on the enemy type, New Game Plus (NG+) cycle,
    and whether the player is in Charmless mode. It uses various multipliers from
    the Enemy and Multipliers modules to adjust the base EXP.

    Args:
        enemy (int): The NpcParamId for the enemy.
        NG (int, optional): The New Game Plus cycle number. Defaults to 0 or NG.
        CL (bool, optional): Indicates if the player is in Charmless mode. Defaults to False.

    Returns:
        int: The calculated EXP, rounded up to the nearest integer.
    """
    @staticmethod
    def getExp(enemy, NG=0, CL=False):
        enemyRef = Enemy.Scaling[enemy] # Get multipliers

        if enemy in Enemy.BossExpRates.keys():
            baseExp = Enemy.BossExpRates[enemy] # fetch base drop rate for exp
        else:
            baseExp = Enemy.ExpRates[enemy] # fetch base drop rate for exp
        baseExp *= Multipliers.ClearcountDroprate[NG][1] # scale ng+ for exp
        baseExp *= Multipliers.CharmlessSenExp[CL] # scale for charmless for exp

        if NG > 0:
            baseExp *= Multipliers.NGCycleExp[enemyRef[0]] # scale ng+ for exp

        if baseExp == int(baseExp):
            baseExp += 0.0001 # make it so ceil() can actually increase it by 1 in cases where you end up with .0

        return ceil(baseExp)

    """
    Calculate the damage based on the attack type, attack power, and mode.

    Parameters:
    attack (int): The attack identifier, default is 5000010. (Base R1)
    AP (int): The attack power level, default is 1.
    mode (str): The mode of the attack, either "Player" or "Enemy", default is "Player".
    dmgType (str): The type of damage to calculate, default is 'atkPhys'.

    Returns:
    int: The calculated damage, rounded up to the nearest integer.
    """
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
 
    """
    Parses and calculates damage details for a given attack using getDamage().

    This static method retrieves and computes the damage attributes for a specified attack
    based on the attack type and effect type. It supports both player and enemy modes.

    Args:
        attack (int): The attack ID to parse. Defaults to 5000010.
        AP (int): Attack Power used in damage calculation. Defaults to 1.
        mode (str): The mode of the attack, either "Player" or "Enemy". Defaults to "Player".

    Returns:
        dict: A dictionary containing the attack type, effect type, and damage values for
        different damage types including Physical, Posture, Magic, Fire, Lightning, and Piercing (Dark).
    """
    @staticmethod
    def parseDamage(attack=5000010, AP=1, mode="Player"):
        output = {}
        dmgTypes = {
            'Physical': 'atkPhys',
            'Posture': 'atkStam',
            'Magic': 'atkMag',
            'Fire': 'atkFire', # +50% when charmless, not included in calculation since the values multiplies how much the player receives rather than how much the enemy deals
            'Lightning': 'atkThun', # not affected by charmless
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

    """
    Calculate the number of attacks needed to deplete the given HP.

    This static method computes how many attacks are required to reduce
    the specified HP to zero, given a certain damage per attack. This is
    NOT an accurate measure of fight length/difficulty. If the HP is
    provided as a list, it returns a comma-separated string of results for each HP value.

    Parameters:
        hp (int or list of int): The health points to be depleted.
        dmg (int): The damage dealt per attack.

    Returns:
        str: The number of attacks needed as a string, or a comma-separated
        string if multiple HP values are provided.
    """
    @staticmethod
    def findAttacksNeeded(hp, dmg):
        out = []
        if isinstance(hp, list):
            for i in hp:
                out.append(str(ceil(i/dmg)))
            return ', '.join(out)
        return str(ceil(hp/dmg))

    """
    Calculate the item discovery chance based on given weight and active buffs.

    This static method computes the probability of item drops by applying
    various buffs from the ItemDiscovery multipliers. It considers specific
    buffs such as 'possessionBalloon', 'pilgrimageBalloon', 'virtuousDeed',
    and 'mostVirtuousDeed', adjusting the base weight accordingly.

    Parameters:
        weight (float): The base weight for item discovery calculation.
        **args: Arbitrary keyword arguments representing active buffs.

    Returns:
        int: The calculated item discovery chance, capped at 100.
    """
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

    """
    Calculate the adjusted chance based on resource type and additional modifiers.

    This static method adjusts a given chance value by applying specific buffs
    if certain conditions are met, particularly when the resource type is spirit emblems.
    The final chance is rounded and capped at 100.

    Args:
        chance (float): The initial chance value to be adjusted.
        resource (int): The type of resource, where 1 indicates spirit emblems.
        **args: Additional keyword arguments that may include:
            - 'spiritBalloon' (bool): If True, applies a 50% buff.
            - 'pilgrimageBalloon' (bool): If True, applies a 50% buff.

    Returns:
        int: The adjusted chance value, capped at 100.
    """
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

    """
    Calculate the experience points (EXP) required to acquire a skill point at a specified level.

    The calculation uses a quadratic formula for levels below a certain threshold and a more complex 
    formula for higher levels. The result is floored to the nearest integer.

    Args:
        lvl (int): The current level of the player.

    Returns:
        int: The required EXP to gain the next skill point at the current level.
    """
    @staticmethod
    def calculateEXP(level):
        x = level + 69

        if x < 8836: # boundary is 94^2
            val = 0.1*x**2+10
        else:
            val = 0.1*x+10*x**2+0.02*x**4
                
        return int(floor(val))
    
    """
    Calculate the total experience points (EXP) required to reach a specified level.

    This method iteratively sums the EXP required for each level up to the given level.

    Args:
        lvl (int): The target level to calculate total EXP for.

    Returns:
        int: The total EXP required to reach the specified level from level zero.
    """
    @staticmethod
    def totalEXP(lvl):
        val = 0
        for i in range(1, lvl+1):
            val += SekiroFunctions.calculateEXP(i)
        return val

