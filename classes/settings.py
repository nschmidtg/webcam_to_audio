def init(max_channels):
    global keep_playing
    keep_playing = True
    global coords
    coords = []
    for i in range(int(max_channels)):
        coords.append([1280, 720])
    global people_counter
    people_counter = 0
