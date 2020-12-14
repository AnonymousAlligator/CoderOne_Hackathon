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

        ammo = player_state.ammo

        bombs = game_state.bombs

        ########################
        ###      AGENT       ###
        ########################

        treasure_locations = game_state.treasure
        ammo_locations = game_state.ammo
        item_locations = treasure_locations + ammo_locations
        # Handle no items on the map
        # Handle blocks being where we want to go

        return find_items(item_locations, self.location)

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
    distances = []
    for item_location in item_locations:
        distances.append(manhattan_distance(location, item_location))
    return min(distances)[1]