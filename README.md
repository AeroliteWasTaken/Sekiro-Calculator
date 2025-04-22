# A simple GUI application for getting basic statistics on Sekiro enemies.

## Features:
 - NG+ Scaling
 - Area/Time Scaling
 - Charmless and Demon Bell Scalings
 - Attack Power Multipliers

## Key Stats:
 - HP - The enemy's health pool. For multiple phases with different values, they are separated by a comma.
 - Posture - The enemy's starting posture value.
 - Damage Multiplier - The value used to multiply each attack's damage.
 - Posture Regen - This value changes a lot depending on events and animations during fights. Dont rely on it. (Check StaminaControlParam)
 - Average hits to kill - A very loose estimate of how many attacks it would take to deplete the enemy's health, just to help you get an idea of their HP. This feature can help you get a pretty accurate ratio to compare different enemies, but shouldnt be used as an actual gauge for fight length.

## Drops:
 - Sen - Amount of Sen dropped by the enemy.
 - EXP - Experience points dropped by the enemy.
 - Resource Items - If the enemy has them, this shows quantity and drop chances of items such as emblems and resurrective power.

## Usage:
 - Enemy List - Every major boss and miniboss is listed in the dropdown menu.
 - Enemy Override - You can input NpcParamIds to view statistics for other enemies that aren't listed.
 - Attack Override - Select which attack is used for calculating the average number of hits to kill. I currently have no plans to transcribe all of the attack IDs. As such, you'll need to find the ID for each attack yourself (e.g., jump kick is 901). 

## Notes:
 - If nothing is displayed, it most likely means your time scaling is invalid. Some areas in the game only use Morning (in this case acting as "Default"), and Bell Evening (Night + Demon Bell). This usually applies to Endgame enemies.
 - Itemlot drops are not listed, this is due to a bug with smithbox that prevents us from getting accurate data. Will probably be fixed in the next update.

# Credits:
 - Holm - Helped a LOT with testing and comparing data, thanks!
 - Savio - For the original idea, inspiration, and moral support :)
 - Maid - Explained some intricacies with the scaling
