'''
TEMPLATE for creating your own Agent to compete in
'Dungeons and Data Structures' at the Coder One AI Sports Challenge 2020.
For more info and resources, check out: https://bit.ly/aisportschallenge
BIO:
<Tell us about your Agent here>
'''

# import any external packages by un-commenting them
# if you'd like to test / request any additional packages - please check with the Coder One team
import random
# import time
# import numpy as np
# import pandas as pd
# import sklearn

"""
 A class for the agent
 
"""
class Agent:

    # Initialise at start time
    def __init__(self):
        self.all_bombs = []
        self.occupied = []

    # Chooses the next action
    def next_move(self, game_state, player_state):
        # Updates the game
        self.update(game_state)
        
        # Chooses the action, randomly
        actions = ['','u','d','l','r','p']
        action = random.choice(actions)
        
        # Keep randoming until an action is maid (or until k=6)
        for k in range(0,6):
            if self.get_next_position(action, player_state) in self.occupied:
                action = random.choice(actions)
        return action
    
    # Gets the position of the agent given an action
    def get_next_position(self, action, player_state):
        pos = player_state.location
        if action == 'u':
            return (pos[0], pos[1]+1)
        elif action == 'd':
            return (pos[0], pos[1]-1)
        elif action == 'l':
            return (pos[0]-1, pos[1])
        elif action == 'r':
            return (pos[0]+1, pos[1])
        return pos # if not moving or placing bomb
    
    # Updates the parameters of the agent class
    def update(self, game_state):
        # Updates the location of all the blocks
        self.occupied = game_state.soft_blocks + game_state.ore_blocks + game_state.indestructible_blocks
        # Removes old bombs and adds new ones
        self.check_bombs(game_state)
        self.add_new_bombs(game_state)
        
    # Checks whether any bombs are exploding and updates accordingly
    def check_bombs(self, game_state):
        new_bombs = []
        for bomb in self.all_bombs:
            if bomb.is_exploding(game_state.tick_number+1):
                self.occupied += bomb.get_explosion(game_state) # agent does not go into explosion
            else:
                new_bombs.append(bomb) # effectively remove exploding bomb
        self.all_bombs = new_bombs # all bombs is now the bombs that did not explode
    
    # Adds new bombs
    def add_new_bombs(self, game_state):
        # Gets a list of all the bomb positions
        bomb_pos = [bomb.get_pos() for bomb in self.all_bombs]
        new_bomb_pos = [pos for pos in game_state.bombs if pos not in bomb_pos]
        
        # Adds new bombs to the list
        for pos in new_bomb_pos:
            bomb = Bomb(game_state.tick_number, pos)
            self.all_bombs.append(bomb)
    

"""
 A class for a bomb
 
"""
class Bomb:

    # Initialises the bomb with its placement tick and position
    def __init__(self, starttick, position):
        self.starttick = starttick
        self.x, self.y = position
    
    # Returns the position of the bomb
    def get_pos(self):
        return (self.x, self.y)
    
    # Returns a boolean depending on whether the bomb is about to explode
    def is_exploding(self, tick):
        if tick - self.starttick >= 35: # Explodes after 3.5 seconds
            return True
        return False
        
    # Returns a list of tuples of the bomb's explosion radius
    def get_explosion(self, game_state):
        max_col, max_row = game_state.size
        explosion = [(self.x, self.y), (self.x+1, self.y), (self.x-1, self.y)]
        explosion += [(self.x+2, self.y), (self.x-2, self.y), (self.x, self.y+1)] 
        explosion += [(self.x, self.y-1), (self.x, self.y+2), (self.x, self.y-2)]
        explosion = [e for e in explosion if (e[0]<max_col and e[0]>=0 
                                          and e[1]<max_row and e[1]>=0)]
        return explosion