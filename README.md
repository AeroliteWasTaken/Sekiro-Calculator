# A simple GUI application for getting basic statistics on Sekiro enemies under a variety of conditions.
## This repository also contains all of the data that was mined and used during the creation of this project. 
### Requirements:
 - PyQt5
 - pyperclip 

## Data within \Sekiro:
 - Enemy.py - Contains info such as stats and scaling IDs
 - Lots.py - Data for resource and itemlots for handling drops
 - Multipliers.py - A bunch of different multipliers used in calculation
 - Player.py - Player stats, mostly unused currently apart from attack power values
 - Reference.py - Commonly used info and references, mostly ID to name dictionaries
 - Utils.py - All functions used in the calculation process

## Displayed Data:
 - HP - The enemy's health pool. For multiple phases with different values, they are separated by a comma.
 - Posture - The enemy's starting posture value.
 - Damage Multiplier - The value used to multiply each attack's damage.
 - Posture Regen - This value changes a lot depending on events and animations during fights. Dont rely on it. (Check StaminaControlParam)
 - Average hits to kill - A very loose estimate of how many attacks it would take to deplete the enemy's health, just to help you get an idea of their HP. This feature can help you get a pretty accurate ratio to compare different enemies, but shouldnt be used as an actual gauge for fight length.
 - Sen - Amount of Sen dropped by the enemy.
 - EXP - Experience points dropped by the enemy.
 - Drops on deathblow - Used for giving resurrection fragments after getting a deathblow on a enemy.
 - Resource Items - If the enemy has them, this shows quantity and drop chances of items such as emblems and resurrective power.
 - Item Drops - Shows possible item drops from this enemy.

## Notes:
 - You can input NpcParamIds to view statistics for basic enemies that aren't listed by using the Entity ID field.
 - Some areas in the game only use Morning (in this case acting as "Default"), and Bell Evening (Night + Demon Bell). If the enemy is fought at a different time, it will use the stats from Default. This usually applies to Endgame enemies.
 - Sen and EXP numbers may be off by 1 due to Fromsoft being REALLY FUCKING BAD AT ROUNDING. (e.g. 25.9 being rounded down to 25 and 27.1 being rounded up to 29 (????))
 - All of the stuff in Extra Options is pretty experimental, please DM me on discord (worstsniper11) if you find any issues.

## How to get NpcParamIds:
1. Download [UXM](https://www.nexusmods.com/eldenring/mods/1651?tab=files) and [Smithbox](https://github.com/vawser/Smithbox/releases)
2. Unpack the game with UXM by inputting the executable path
3. Open Smithbox and make a new project
4. Go to Map Editor, right click the map that the enemy you want is in, and click load
5. Find the enemy and click on it (you move by holding right click over the viewport)
6. On the right, click properties and scroll down to find NPC Param ID, copy this and paste it into the field within the calculator

# Credits:
 - Holm - Helped a LOT with testing and comparing data, thanks!
 - Savio - For the original idea, inspiration, and moral support. Also did the majority of the testing for the GUI :)
 - Maid - Explained some intricacies with params and taught me a lot about the scalings (thanks for saving me from hours of pain)
