'''
This is a bot facing an existential crisis.
All it does is walk around the map.
'''

import time
import random

class agent:

    def __init__(self):
        pass

    def next_move(self, game_state, player_state):
        """ 
        This method is called each time the agent is required to choose an action
        """

        ########################
        ###    VARIABLES     ###
        ########################

        # list of all possible actions to take
        actions = ['', 'u', 'd', 'l','r','p']

        # store some information about the environment
        # game map is represented in the form (x,y)
        self.cols = game_state.size[0]
        self.rows = game_state.size[1]
        self.game_state = game_state # for us to refer to later
        self.location = player_state.location
        if game_state.tick_number == 0:
            self.id = player_state.id
            if self.id == 0:
                opponent_id = 1
            else:
                opponent_id = 0
        opponent_location = game_state.opponents(self.id)[0]
        blocks = game_state.all_blocks
        ammo = player_state.ammo

        bombs = game_state.bombs

        ########################
        ###      AGENT       ###
        ########################
        # 1) find bombs
        # 2.1) cant find bombs then find opponent and follow them 
        # 2.1.1) if opponent is trappable, attack
        # 2.2) if not 7 find treasure and collect
        # 2.2.1) no treasure then go for crates
        # 2.2.2) no crates go for ore
        # 2.2.3) no ore then run around
        treasure_locations = game_state.treasure
        ammo_locations = game_state.ammo
        # surrounding = [west, east, north, south, nw, ne, se, sw]
        my_surrounding = [(self.location[0]-1,self.location[1]), (self.location[0]+1,self.location[1]), 
                        (self.location[0],self.location[1]+1), (self.location[0],self.location[1]-1),
                        (self.location[0]-1,self.location[1]+1), (self.location[0]+1,self.location[1]+1),
                        (self.location[0]+1,self.location[1]-1), (self.location[0]-1,self.location[1]-1)]

        opponent_surrouding = [(opponent_location[0]-1,opponent_location[1]), (opponent_location[0]+1,opponent_location[1]), 
                        (opponent_location[0],opponent_location[1]+1), (opponent_location[0],opponent_location[1]-1),
                        (opponent_location[0]-1,opponent_location[1]+1), (opponent_location[0]+1,opponent_location[1]+1),
                        (opponent_location[0]+1,opponent_location[1]-1), (opponent_location[0]-1,opponent_location[1]-1)]
        # 1)
        action = find_items(ammo_locations, self.location)
        # 2.1)
        # if action == '' and opponent_location in my_surrounding:
        #     action = attack(self.location, opponent_location, bombs)
        # 2.1)
        if action == '':
            action = stalk(self.location, opponent_location)

        # Handle blocks being where we want to go

        return action

def stalk(my_location, opponent_location):
    x_distance = opponent_location[0] - my_location[0]
    y_distance = opponent_location[1] - my_location[1]
    if abs(y_distance) < abs(x_distance):
        if my_location[0] < opponent_location[0]:
            move = 'r'
        else:
            move = 'l'
    else:
        if my_location[1] < opponent_location[1]:
            move = 'u'
        else:
            move = 'd'
    return move

def attack(my_location, opponent_location, bombs):
    if my_location in bombs:
        pass

def manhattan_distance(start, end):
    '''
    start == current location
    end == an item
    returns manhattan distance to the item
    '''
    x_distance = end[0] - start[0]
    y_distance = end[1] - start[1]
    if abs(y_distance) < abs(x_distance):
        if start[0] < end[0]:
            move = 'r'
        else:
            move = 'l'
    else:
        if start[1] < end[1]:
            move = 'u'
        else:
            move = 'd'
    distance = abs(x_distance) + abs(y_distance)
    return (distance, move)

def find_items(item_locations, location):
    if item_locations == []:
        return ''
    distances = []
    for item_location in item_locations:
        distances.append(manhattan_distance(location, item_location))
    return min(distances)[1]