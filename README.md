# Sunken
A small game where the player controls a ship. The goal is to rescue as many stranded survivors as possible, while avoiding obstacles.

Must have pygame and sqlite3 installed to run this program.

# How to play
Use the arrow keys to move the ship.

To rescue survivors, press the spacebar while near them.

To unload the passengers on board, press any of the control keys while near the dock.

# The rules:
First, choose a type of ship - Small, Medium or Large. Each ship comes with a number of differences, including different speeds, capacities and physical sizes, 
granting each it's own advantages and disadvantages.

To rescue a group of survivors, press the spacebar when nearby. When your ship's capacity hits it's maximum, you must unload the passengers on board
before continuing to rescue more survivors. Your max capacity and current capacity both can be found at the top right corner of the screen.

When you unload passengers at the dock, your score increases by the amount of passengers unloaded. Each group of survivors has a lifespan of 10 seconds. 
If not saved in time, they will drown, and your score will be decreased by the number of survivors in said group.

Be sure to avoid the sharks and the fire! When you come in contact with any of the obstacles on screen, your health will decrease by 10 points.
When your health scores hits 0, the game ends.

Your current score and health can be seen in the bottom left corner of the screen.

At the end of each game, your score, the time at which the game was played, and the class of ship will be saved in a database. Then, the scores from all games played
will be printed into 2 files - 'scores_by_date.txt', where the scores are printed ordered by the time at which the game was played, and 'high_scores.txt', where
the scores are printed ordered by the score itself.
