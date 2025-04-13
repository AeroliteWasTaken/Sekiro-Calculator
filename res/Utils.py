from res import PlayerStats

def mult(multiplier, val):
    return [[x * multiplier for x in item] if isinstance(item, list) else item * multiplier for item in val]

def div(val, multiplier):
    return [[ceil(x / multiplier) for x in item] if isinstance(item, list) else ceil(item / multiplier) for item in val]

def multiplyRecursive(data, multiplier):
    if isinstance(data, list):  # If it's a list, apply the function to each element
        return [multiplyRecursive(item, multiplier) for item in data]
    else:  # If it's not a list, just multiply the value
        return data * multiplier

def floatConv(nested_list):
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.append(floatConv(item))
        elif isinstance(item, float):
            result.append(int(item))
        else:
            result.append(item)
    return result

def ceil(x):
    if isinstance(x, list):
        return [ceil(item) for item in x]
    elif isinstance(x, (int, float)):
        return int(x) if x == int(x) else int(x) + 1 if x > 0 else int(x)
    
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

def findAttacksNeeded(hp, dmg):
    out = []
    if isinstance(hp, list):
        for i in hp:
            out.append(str(ceil(i/dmg)))
        return ', '.join(out)
    return str(ceil(hp/dmg))