# A simple GUI application for getting basic statistics on Sekiro enemies.
### Requirements:
 - PyQt5
 - pyperclip

## Features:
 - NG+ Scaling
 - Area/Time Scaling
 - Charmless and Demon Bell Scalings
 - Attack Power Multipliers
 - Multiple extra options for calculations
 - Sort enemy list
 - Copy output to clipboard
 - Export output to .txt

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
 - You can input NpcParamIds to view statistics for other enemies that aren't listed using the Entity ID field.
 - Some areas in the game only use Morning (in this case acting as "Default"), and Bell Evening (Night + Demon Bell). If the enemy is fought at a different time, it will use the stats from Default. This usually applies to Endgame enemies.
 - Sen numbers might be off by a small margin due to weird behaviour with ClearCountCorrectParams
 - All of the stuff in Extra Options is pretty experimental, please DM me on discord (worstsniper11) if you find any issues.

# Credits:
 - Holm - Helped a LOT with testing and comparing data, thanks!
 - Savio - For the original idea, inspiration, and moral support. Also did the majority of the testing for the GUI :)
 - Maid - Explained some intricacies with params and taught me a lot about the scalings (thanks for saving me from hours of pain)
