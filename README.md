# A simple GUI application for getting basic statistics on Sekiro enemies.

## Supports:
 - NG+ Scaling
 - Area/Time Scaling
 - Charmless and Demon Bell Scalings
 - Attack Power Multipliers

## Stats:
 - HP - The enemy's health pool. For multiple phases with different values, they are separated by a comma.
 - Posture - The enemy's starting posture
 - Damage Multiplier - The value used to multiply each attack's damage
 - Posture Regen - Not quite sure how this works but I included it anyway
 - A very loose estimate of how many attacks it would take to kill the enemy, just to help you get an idea of their HP

## Drops:
 - Sen - How much sen would this enemy drop
 - EXP - How much EXP would this enemy drop
 - Resource items are listed below, if the enemy has them. This includes quantity and drop chance of items such as emblems and resurrective power

### Every main boss and miniboss is listed in the dropdown menu, but it also supports all other enemies in the game via an override for you to input NpcParamIds
### The attack override can be used to change which attack is used when calculating how many average hits a kill may take. There are currently no plans to add all attack names. For example, a jump kick would be 901. This feature is kinda useless but it's there I guess

# Credits:
 - Holm - Helped a LOT with testing and comparing data, thanks!
 - Savio - For the original idea, inspiration, and moral support :)
 - Maid - Explained some intricacies with the scaling
