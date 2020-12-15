import random

BOMB_TIME = 35

"""
 A class for the agent
 
"""
class Agent:

    # Initialise at start time
    def __init__(self):
        self.all_bombs = []
        self.occupied = []
        self.items = []
        self.bombables = []
        self.last_bomb = -BOMB_TIME-1
        

    # Chooses the next action
    def next_move(self, game_state, player_state):
        # Updates the game
        self.update(game_state)
        
        # Algorithm:
        # 1) If have bombs and crates and next to crate, place bomb and run
        # 2) If have bombs and crates and not next to crate, go towards crate
        # 3) If have bombs and no crates and next to ore, place bomb and run
        # 4) If have bombs and no crates and not next to ore, go towards ore
        # 5) If no bombs, get ammo / treasures
        # 6) Move randomly
        action = self.next_move_bomb(game_state, player_state)
        if action == '':
            action = self.next_move_BFS(game_state, player_state, self.items)
        if action == '':
            action = self.next_move_random(player_state)
        return action
    
    
    # Tries to bomb wooden crates
    def next_move_bomb(self, game_state, player_state):
        if player_state.ammo != 0 and game_state.tick_number - self.last_bomb > BOMB_TIME+1:
            if player_state.location in self.bombables:
                self.last_bomb = game_state.tick_number
                return 'p'
            else:
                return self.next_move_BFS(game_state, player_state, self.bombables)
        return ''
    
    
    # Chooses a random position but tries to avoid blocks/danger
    def next_move_random(self, player_state):
        # Chooses the action, randomly
        actions = ['u','d','l','r']
        action = random.choice(actions)
        
        # Choose best option
        for k in range(0,5):
            if self.get_next_position(action, player_state.location) in self.occupied:
                index = actions.index(action)
                action = actions[(index+1)%len(actions)]
            break
        return action

        
    # Gets the position of the agent given an action
    def get_next_position(self, action, pos):
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
        self.occupied = game_state.all_blocks + game_state.opponents(0)
        self.items = game_state.ammo + game_state.treasure
        
        # Updates the list of neighbours of bombable blocks
        bombables = game_state.soft_blocks
        if bombables == []:
            bombables = game_state.ore_blocks
        self.bombables = self.get_all_neighbours(bombables, game_state)
        
        # Removes old bombs and adds new ones
        self.occupied += self.check_bombs(game_state)
        self.add_new_bombs(game_state)

        
    # Checks whether any bombs are exploding and updates accordingly
    def check_bombs(self, game_state):
        new_bombs = []
        explosions = []
        for bomb in self.all_bombs:
            if bomb.is_exploding(game_state.tick_number+1):
                explosions += bomb.get_explosion(game_state)
            else:
                new_bombs.append(bomb) # effectively remove exploding bomb
        self.all_bombs = new_bombs # all bombs is now the bombs that did not explode
        return explosions # returns a list of dangerous squares

        
    # Adds new bombs
    def add_new_bombs(self, game_state):
        # Gets a list of all the bomb positions
        bomb_pos = [bomb.get_pos() for bomb in self.all_bombs]
        new_bomb_pos = [pos for pos in game_state.bombs if pos not in bomb_pos]
        
        # Adds new bombs to the list
        for pos in new_bomb_pos:
            bomb = Bomb(game_state.tick_number, pos)
            self.all_bombs.append(bomb)

            
    # Determines the optimal next movement using BFS
    def next_move_BFS(self, game_state, player_state, target_squares):
        visited = [] # visited squares
        previous = [] # squares previous to the visited squares
        queue = [] # queue of squares to be visited
        
        # Add current position to the queue
        player_pos = player_state.location
        queue.append(player_pos)
        visited.append(player_pos)
        previous.append((-1,-1)) # random number
    
    
        # Run until the queue is empty
        while(len(queue)!=0):
            curr = queue.pop(0)
            
            # If an items is found
            if curr in target_squares:
                next = curr
                while curr != player_pos:
                    next = curr
                    curr = previous[visited.index(curr)]
                
                return self.get_direction(player_pos, next)
            
            # Add neighbouring squares to the queue
            neighbours = self.get_neighbours(curr, game_state)
            for n in neighbours:
                if n not in visited and n not in self.occupied:
                    visited.append(n)
                    queue.append(n)
                    previous.append(curr)
        
        return ''
    
    
    # Gets the direction given a current and next positions
    def get_direction(self, curr_pos, next_pos):
        diff = (curr_pos[0]-next_pos[0], curr_pos[1]-next_pos[1])
        
        if diff == (0,1):
            return 'd'
        elif diff == (1,0):
            return 'l'
        elif diff == (0,-1):
            return 'u'
        elif diff == (-1,0):
            return 'r'
        else:
            return ''
    
    
    # Gets the neighbouring squares of a list of squares
    def get_all_neighbours(self, positions, game_state):
        neighbours = []
        for position in positions:
            neighbours += self.get_neighbours(position, game_state)
        list(dict.fromkeys(neighbours)) # remove duplicates
        return neighbours
        
        
    # Gets the neighbouring squares
    def get_neighbours(self, curr_pos, game_state): 
        max_col, max_row = game_state.size
        x, y = curr_pos
        neighbours = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
        neighbours = [n for n in neighbours if (n[0]<max_col and n[0]>=0
                                            and n[1]<max_row and n[1]>=0)]
        return neighbours
        
    
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
        if tick - self.starttick >= BOMB_TIME: # Explodes after 3.5 seconds
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