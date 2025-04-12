import Multipliers
import EnemyRef
import EnemyBaseStats
import Lots
import PlayerStats
import argparse

def ceil(x):
    if x == int(x):
        return int(x)
    else:
        return int(x) + 1 if x > 0 else int(x)

def getPlayerDmg(AP=1, attack=5000010):
    if attack in [900, 901, 903]: # jump kick
        baseDmg = 10
    elif attack == 3520: # throwing oil
        return 1
    else:
        baseDmg = 40 # base for most attacks and CAs
    baseDmg *= PlayerStats.Player_Attack_Power[AP] # multiply by AP
    atkCorrect = PlayerStats.Player_Attacks[attack][2] # get atkPhysCorrection

    if atkCorrect > 0:
        baseDmg *= PlayerStats.Player_Attacks[attack][2]/100 # multiply if possible

    return ceil(baseDmg)

def getStat(enemy, AP=1, NG=0, CL=False, DB=False, Time=1, Mode=0, attack=5000010):
    
    enemyRef = EnemyRef.EnemyRef[enemy]  # Get multipliers

    if Mode == 0:  # normal
        timeOffset = Multipliers.Time_Offset[DB][Time]  # find offset for time + demon bell
        enemyStat = [EnemyBaseStats.EnemyStats[enemy][0], EnemyBaseStats.EnemyStats[enemy][1], EnemyBaseStats.EnemyStats[enemy][2]] # get all stats
        enemyStat = [x * Multipliers.Clearcount_HP[CL][NG] for x in enemyStat]  # scale ng

        if CL and NG == 0:
            timeOffset += 700  # account for new game CL scaling
        if NG > 0:
            enemyStat = [x * Multipliers.NGCycle_HP[enemyRef[0] + timeOffset] for x in enemyStat]  # correct for ng+ scaling
        if CL:
            enemyStat = [x * Multipliers.Charmless_Muliplier_By_Type[enemyRef[2]] for x in enemyStat]  # increase stats based off of enemy type (in this case; boss)
        enemyStat = [x * Multipliers.AreaScale_HP[enemyRef[1] + timeOffset] for x in enemyStat]  # multiply area scaling

    else:
        AP = 14 # set ap to 14 since it's fixed in reflections and gauntlets
        if Mode == 1:  # reflection
            override = EnemyRef.ReflectionOverride[(CL, DB)]

        elif Mode == 2:  # mortal journey
            override = EnemyRef.MortalJourneyOverride[(CL, DB)]

        enemyStat = [EnemyBaseStats.EnemyStats[enemy][0], EnemyBaseStats.EnemyStats[enemy][1], EnemyBaseStats.EnemyStats[enemy][2]]
        enemyStat = [x * Multipliers.AreaScale_HP[override[0]] for x in enemyStat]
        enemyStat = [x * Multipliers.NGCycle_HP[override[1]] for x in enemyStat]
        enemyStat = [x * Multipliers.Charmless_Muliplier_By_Type[enemyRef[2]] for x in enemyStat]

    output = [int(x) for x in enemyStat]
    attacksNeeded = ceil(output[0] / getPlayerDmg(AP=AP, attack=attack))
    print("\n-----------------------------------------------")
    print(f"HP: {output[0]}\nPosture: {output[1]}\nPosture Regen: {output[2]}")
    print(f"\nAt AP{AP}, it would take {attacksNeeded} attacks to kill this enemy!")
    print("-----------------------------------------------")

"""Time Codes: 1 - Dawn/Default, 2 - Noon, 3 - Sunset, 4 - Night""" # note: some end game areas only use 1 and 4 (as default and demon bell respectively)
"""Modes: 0 - Default, 1 - Reflections/Gauntlets, 2 - Mortal Journey"""
"""Stats: 0 - HP, 1 - Posture, 2 - Posture Regen"""

def getRates(enemy, NG=0, CL=False):
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
    print("\n-----------------------------------------------")
    print("Guaranteed Drops:\n")
    print(f"EXP: {round(baseExp)}\nSen: {round(baseSen)}")
    print("-----------------------------------------------")

    resourceDrops = EnemyBaseStats.Enemy_ResourceLot_Drops[enemy]
    dropList = [Lots.Resource_Item_Lots[i] for i in resourceDrops if i]
    for index, i in enumerate(dropList):
        print(f'Resource Lot #{index+1}:\n')
        for j in i:
            print(f"{' -' if j[2] == 0 else f' - {j[2]}'} {Lots.ResourceRef[j[0]]} - {j[1]}% chance\n")
        print("-----------------------------------------------")

    itemDrops = EnemyBaseStats.Enemy_ItemLot_Drops[enemy]
    dropList = [Lots.TR_Item_Lots[i] for i in itemDrops if i]
    try:
        dropList += [Lots.TR_Item_Lots[enemy]]
    except:
        pass
    for index, i in enumerate(dropList):
        print(f'Item Lot #{index+1}:\n')
        print(f" - {i}\n")
        print("-----------------------------------------------")
    
def process_arguments(enemy, ng, cl, db, time, mode, ap, attack):

    if not enemy:
        print("Please input an enemy ID")
        quit()

    getStat(enemy=enemy, NG=ng, CL=cl, DB=db, Time=time, Mode=mode, AP=ap, attack=attack)
    getRates(enemy=enemy, NG=ng, CL=cl)

def main():
    parser = argparse.ArgumentParser(description="Parse command line arguments for game settings.")

    parser.add_argument('-enemy', type=int, required=True, help="Specify the enemy ID")
    parser.add_argument('-ng', type=int, default=0, help="Specify NG value (default: 0)")
    parser.add_argument('-ap', type=int, default=1, help="Specify AP value (default: 1)")
    parser.add_argument('-attack', type=int, default=5000010, help="Specify attack ID (default: 5000010)")
    parser.add_argument('--cl', action='store_true', help="Specify CL value")
    parser.add_argument('--db', action='store_true', help="Specify DB value")
    parser.add_argument('-time', type=int, choices=[1, 2, 3, 4], default=1, help="Specify Time value (1-4, default: 1)")
    parser.add_argument('-mode', type=int, choices=[0, 1, 2], default=0, help="Specify Mode value (0-2, default: 0)")

    args = parser.parse_args()

    process_arguments(args.enemy, args.ng, args.cl, args.db, args.time, args.mode, args.ap, args.attack)

if __name__ == "__main__":
    main()

