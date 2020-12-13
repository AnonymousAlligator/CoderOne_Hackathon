def manhattan_distance(start, end):
    '''
    start == current location
    end == an item
    returns manhattan distance to the item
    '''
    x_distance = start[0] - end[0]
    y_distance = start[1] - end[1]
    if abs(x_distance) < abs(y_distance):
        if start[1] < end[1]:
            move = 'r'
        else:
            move = 'l'
    else:
        if start[0] < end[0]:
            move = 'u'
        else:
            move = 'd'
    distance = abs(start[0] - end[0]) + abs(start[1] - end[1])
    return (distance, move)

def find_items(game_state, player_state):
    # get where treasure and ammo is
    treasure_locations = game_state.treasure
    ammo_locations = game_state.ammo
    item_locations = treasure_locations + ammo_locations
    distances = []
    for item_location in item_locations:
        distances.append(manhattan_distance(player_state.location, item_location))
    return min(distances)[1]
