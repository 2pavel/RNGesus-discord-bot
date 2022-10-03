# RNGesus-discord-bot
My first python project - discord bot used to play Neuroshima pen and paper RPG

Most essential files:
- rngesus.py - main module
- react.py - reaction module

Stats, abilities and general rules are based on the official book - Neuroshima 1.5

The bot is mostly used when a Player's ability is tested in the game. RNGesus rolls the dice and determines test result based on the roll and:
- Player's stats
- Ability level
- Difficulty level
- Critical modifiers (1 or 20 on any dice) where applicable
- Ability slider (Multiples of 4 represent a level of mastery and lower the difficulty of the test)

React module sends reaction gifs for the rolls that are most likely to cause Players to react as well.
For example, if a Player passes a very hard test because of a lucky roll, the bot will send a gif with positive reaction.
