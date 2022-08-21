def init(init_params, graphic_off):
    global uncompressed
    uncompressed = graphic_off
    global keep_playing
    keep_playing = True
    global coords
    coords = []
    for i in range(4):
        coords.append([1280, 720])
    global people_counter
    people_counter = 0
    global params
    params = init_params
