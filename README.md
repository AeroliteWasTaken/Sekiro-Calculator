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
 - Posture Regen - Not quite sure how this works but I included it anyway.
 - Average hits to kill - A very loose estimate of how many attacks it would take to deplete the enemy's health, just to help you get an idea of their HP.

## Drops:
 - Sen - Amount of Sen dropped by the enemy.
 - EXP - Experience points dropped by the enemy.
 - Resource Items - If the enemy has them, this shows quantity and drop chances of items such as emblems and resurrective power.

## Usage:

 - Enemy List - Every major boss and miniboss is listed in the dropdown menu.

 - Enemy Override - You can input NpcParamIds to view statistics for other enemies that aren't listed.

 - Attack Override - Select which attack is used for calculating the average number of hits to kill. I currently have no plans to transcribe all of the attack IDs. As such, you'll need to find the ID for each attack yourself (e.g., jump kick is 901). This feature is only really there for fun though.

## Installation:
### Simply click the shiny green button and download the source code as a zip, then extract it wherever you want.

# Credits:
 - Holm - Helped a LOT with testing and comparing data, thanks!
 - Savio - For the original idea, inspiration, and moral support :)
 - Maid - Explained some intricacies with the scaling
