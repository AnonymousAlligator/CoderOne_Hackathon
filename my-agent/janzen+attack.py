import random

BOMB_TIME = 35
RAMPAGE_GRACE_PERIOD = 10

"""
 A class for the agent
  found. /lib/x86_64-linux-gnu/libm.so.6: version `GLIBC_2.29' not found (required by /home/kevin/coderOne/CoderOne_Hackathon/venv/lib/python3.8/site-packages/arcade/soloud/libsoloud.so)
Warning, can't initialize soloud name 'soloud_dll' is not defined. Sound support will be limited.
"""
class Agent:

    # Initialise at start time
    def __init__(self):
        self.all_bombs = []
        self.all_ores = []
        self.occupied = []
        self.items = []
        self.bombables = []
        self.grace_period = BOMB_TIME+1 
        self.last_bomb = -self.grace_period
        self.id = -1
        

    # Chooses the next action
    def next_move(self, game_state, player_state):
        # Updates the game
        self.update(game_state, player_state)
        if game_state.tick_number == 0:
            self.initialise_all_ores(game_state)
            self.id = player_state.id
        
        # If have bombs, tries to bomb damaged ores, wood, then undamaged ores
        action = self.next_move_bomb(game_state, player_state)
        # If no bombs, get ammo / treasures
        if action == '':
            action = self.next_move_BFS(game_state, player_state, self.items)
        # Otherwise, move randomly while avoiding danger
        if action == '':
            action = self.next_move_random(player_state)
        
        return action
    
    
    # Initialise the ore list
    def initialise_all_ores(self, game_state):
        for pos in game_state.ore_blocks:
            ore = Ore(pos)
            self.all_ores.append(ore)
        
    
    # Tries to bomb stuff
    def next_move_bomb(self, game_state, player_state):
        if player_state.ammo != 0 and game_state.tick_number - self.last_bomb > self.grace_period:
            if player_state.location in self.bombables:
                self.last_bomb = game_state.tick_number
                return 'p'
            else:
                return self.next_move_BFS(game_state, player_state, self.bombables)
        return ''
    
    
    # Chooses a random position but tries to avoid blocks/danger
    def next_move_random(self, player_state):
        # Chooses the action, randomly
        actions = ['u','d','l','r', '']
        action = random.choice(actions)
        
        # Choose best option
        for k in range(0,len(actions)):
            if self.get_next_position(action, player_state.location) in self.occupied:
                index = actions.index(action)
                action = actions[(index+1)%len(actions)]
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
    def update(self, game_state, player_state):
        # Updates the location of all the blocks
        self.occupied = game_state.all_blocks + game_state.bombs + game_state.opponents(self.id)
        self.items = game_state.ammo + game_state.treasure
        self.update_ore_blocks(game_state)
        
        if game_state.soft_blocks == [] and game_state.ore_blocks == []:
            self.grace_period = RAMPAGE_GRACE_PERIOD # throws a bomb every second
        
        # Updates the target blocks with a certain priority
        bombables = []
        # 1) Search for damaged ore blocks (about to break)
        targets = self.get_damaged_ores()
        bombables = self.get_bombables(targets, game_state)
        # 2) Search for wooden blocks
        if bombables == []:
            targets = game_state.soft_blocks
            bombables = self.get_bombables(targets, game_state)
        # 3) Search for ore blocks
        if bombables == []:
            targets = game_state.ore_blocks
            bombables = self.get_bombables(targets, game_state)
        # 4) Once all blocks are gone/unreachable, attack the player
        if bombables == []:
            targets = game_state.opponents(self.id)
            bombables = self.get_all_neighbours(targets, game_state)
            
        # Gets the neighbours of the target blocks
        self.bombables = bombables
        
        # Removes old bombs and adds new ones
        self.occupied += self.check_bombs(game_state)
        self.add_new_bombs(game_state)

        
    # Gets the targetted blocks
    def get_bombables(self, targets, game_state):
        neighbours = self.get_all_neighbours(targets, game_state)
        bombables = self.check_accessible(game_state, neighbours)
        return bombables
    
        
    # Checks that a block is accessible
    def check_accessible(self, game_state, neighbours):
        bomb_spot = []
        for neighbour in neighbours:
            if neighbour not in game_state.all_blocks:
                bomb_spot.append(neighbour)
        return bomb_spot


    # Checks whether any bombs are exploding and updates accordingly
    def check_bombs(self, game_state):
        new_bombs = []
        explosions = []
        for bomb in self.all_bombs:
            if bomb.is_exploding(game_state.tick_number+1):
                explosion = bomb.get_explosion(game_state)
                explosions += explosion
                self.check_ore_blocks(explosion, game_state)
                self.check_other_bombs(bomb.pos, explosion, game_state)
            else:
                new_bombs.append(bomb) # effectively remove exploding bomb
        self.all_bombs = new_bombs # all bombs is now the bombs that did not explode
        return explosions # returns a list of dangerous squares

    
    # Checks the states of ore blocks
    def check_ore_blocks(self, explosion, game_state):
        for e in explosion:
            if e in game_state.ore_blocks:
                self.damage_ore_block(e)
    
    
    # Checks the state of other bombs
    def check_other_bombs(self, bomb_pos, explosion, game_state):
        explosion.remove(bomb_pos)
        for e in explosion: 
            if e in game_state.ore_blocks:
                self.detonate_bomb(e, game_state)
    
    
    # Updates the ore blocks in the game
    def update_ore_blocks(self, game_state):
        new_ore_blocks = []
        for pos in game_state.ore_blocks:
            for ore in self.all_ores:
                if ore.pos == pos:
                    new_ore_blocks.append(ore)
                    break
        self.all_ores = new_ore_blocks
    
                
    # Damages an ore block at a certain position
    def damage_ore_block(self, position):
        for ore in self.all_ores:
            if ore.pos == position:
                ore.damage()
                if ore.state == 0:
                    self.all_ores.remove(ore)
                return
    
    
    # Shortens the fuse of a bomb at a certain position
    def detonate_bomb(self, position, game_state):
        for bomb in self.all_bombs:
            if bomb.pos == position:
                bomb.detonate(game_state)
                return
    
    
    # Returns a list of the positions of ore blocks that are about to break
    def get_damaged_ores(self):
        damaged_ores = []
        for ore in self.all_ores:
            if ore.state == 1:
                damaged_ores.append(ore.pos)
        return damaged_ores
    
    
    # Adds new bombs
    def add_new_bombs(self, game_state):
        # Gets a list of all the bomb positions
        bomb_pos = [bomb.pos for bomb in self.all_bombs]
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
    def get_neighbours(self, pos, game_state): 
        max_col, max_row = game_state.size
        x, y = pos
        neighbours = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
        neighbours = [n for n in neighbours if (n[0]<max_col and n[0]>=0
                                            and n[1]<max_row and n[1]>=0)]
        return neighbours


"""
 A class for a bomb
 
"""
class Bomb:

    # Initialises the bomb with its placement tick and position
    def __init__(self, starttick, pos):
        self.starttick = starttick
        self.pos = pos
    
    # Tells the bomb to detonate in two ticks
    def detonate(self, tick):
        self.starttick = tick - BOMB_TIME + 2
    
    
    # Returns a boolean depending on whether the bomb is about to explode
    def is_exploding(self, tick):
        if tick - self.starttick == BOMB_TIME: # Explodes after 3.5 seconds
            return True
        return False
        
        
    # Returns a list of tuples of the bomb's explosion radius
    def get_explosion(self, game_state):
        max_col, max_row = game_state.size
        x, y = self.pos
        explosion = [(x,y), (x+1,y), (x-1,y), (x+2,y), (x-2,y),
                     (x,y+1), (x,y-1), (x,y+2), (x,y-2)]
        temp_explosion = [e for e in explosion if (e[0]<max_col and e[0]>=0 
                                          and e[1]<max_row and e[1]>=0)]
        explosion = temp_explosion
        for e in temp_explosion:
            if e in [(x+1,y), (x-1,y),(x,y+1), (x,y-1)]:
                if e in game_state.all_blocks:
                    diff = (e[0]-x, e[1]-y)
                    if diff == (1,0):
                        try:
                            explosion.remove((x+2,y))
                        except ValueError:
                            continue
                    elif diff == (-1,0):
                        try:
                            explosion.remove((x-2,y))
                        except ValueError:
                            continue
                    elif diff == (0,1):
                        try:
                            explosion.remove((x,y+2))
                        except ValueError:
                            continue
                    else:
                        try:
                            explosion.remove((x,y-2))
                        except ValueError:
                            continue
        return explosion


"""
 A class for ore blocks
 
"""
class Ore:

    # Initialises an ore block with its position
    def __init__(self, pos):
        self.state = 3 # takes 3 hits to be destroyed
        self.pos = pos
    
    
    # Damages the ore block once
    def damage(self):
        self.state -= 1