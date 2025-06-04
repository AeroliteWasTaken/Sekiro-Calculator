from Sekiro import Utils, Reference

"""Player Damage Check"""
damage = Utils.SekiroFunctions.parseDamage(5000152, AP=14) # umbrella projected force in reflection
for key, val in damage.items():
    print(f"{key} - {val}")
"""Outputs:
    Attack Type - Slash
    Effect Type - None
    Physical - 0
    Posture - 255
    Magic - 0
    Fire - 0
    Lightning - 0
    Piercing (Dark) - 536
"""
print("\n")

"""Stats Check"""
enemy = Reference.EnemyName["Chained Ogre"]
stats = Utils.SekiroFunctions.getStats(enemy, NG=7, CL=True) # charmless NG+7 ogre
for key, val in stats.items():
    print(f"{key} - {val}")
"""Outputs:
    HP - 23803
    Posture - 6973
    Posture Regen - 278
    Damage Multiplier - 5.36
    Max hits to kill at AP1 - 298
"""
print("\n")

"""Resource Check"""
enemy = Reference.EnemyName["Tokujiro"]
resources = Utils.SekiroFunctions.getExpSen(enemy) # tokujiro base drops
for key, val in resources.items():
    print(f"{key} - {val}")
"""Outputs:
    Sen - 135
    EXP - 1285
"""
print("\n")

"""Drop Check"""
enemy = 15500210 # basic hirata enemy
drops = Utils.SekiroFunctions.getDrops(enemy, DB=True, Time=2, virtuousDeed=True) # noon with demon bell and virtuous deed unlocked
for item in drops:
    print(item["count"], item["name"], item["chance"])
"""Outputs:
    1 Spirit Emblem(s) - 50% chance
    5 Resurrection Fragment(s) - 30% chance
    1 Oil - 27% chance
    1 Dousing Powder - 12% chance
    1 Scrap Iron - 25% chance
"""
print("\n")