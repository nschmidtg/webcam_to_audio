def init(init_params, graphic_off, x_size, y_size):
    global x_screen_size
    x_screen_size = x_size
    global y_screen_size
    y_screen_size = y_size
    global uncompressed
    uncompressed = graphic_off
    global keep_playing
    keep_playing = True
    global coords
    coords = []
    for i in range(4):
        coords.append([x_screen_size, y_screen_size])
    global people_counter
    people_counter = 0
    global params
    params = init_params
