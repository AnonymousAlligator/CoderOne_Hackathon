def bfs(game_state, player_state):
    queue = []
    visited = []
    previous = []
    treasure_locations = game_state.treasure
    ammo_locations = game_state.ammo
    # List of where items are
    item_locations = treasure_locations + ammo_locations
    # board_size = (x,y) = (col,row)
    board_size = game_state.size
    # Add current location to queue
    current_location = player_state.location
    queue.append(current_location)
    visited.append(current_location)
    previous.insert(current_location[1]*board_size[0]+current_location[0], None)
    while len(queue) != 0:
        curr = queue.pop(0)
        next_location = curr
        if curr in item_locations:
            while curr != current_location:
                index = curr[1]*board_size[0]+curr[0]
                curr = previous[index]
                if curr is None:
                    diff = (next_location[0]-curr[0], next_location[1]-curr[1])
                    if diff == (1,0):
                        move = 'r'
                    elif diff == (-1,0):
                        move = 'l'
                    elif diff == (0,1):
                        move = 'u'
                    else:
                        move = 'd'
                    return move
                next_location = curr
        # neighbours = [lect, right, up, down]
        neighbours = [(curr[0]-1,curr[1]), (curr[0]+1,curr[1]), 
                        (curr[0],curr[1]+1), (curr[0],curr[1]-1)]
        for neighbour in neighbours:
            if neighbour not in visited:
                visited.append(neighbour)
                queue.append(neighbour)
                previous.insert(neighbour[1]*board_size[0]+neighbour[0], curr)
