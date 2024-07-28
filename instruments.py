from json import load
import tkinter as tk

# with open('config/settings.json') as f:
#     settings = load(f)
# with open('config/strings.json') as f:
#     strings = load(f)[settings['language']]
with open('config/constants.json') as f:
    constants = load(f)

class Guitar():

    def __init__(self, root, max_width):        
        CANVAS_WIDTH = max_width
        FRETBOARD_LENGTH = CANVAS_WIDTH - CANVAS_WIDTH // 10     # x axis
        FRETBOARD_WIDTH = FRETBOARD_LENGTH // 7
        STRING_NUMBER = 6
        FRETS_NUMBER = 24
        ONE_DOT_FRETS = [3, 5, 7, 9, 15, 17, 19, 21]
        TWO_DOT_FRETS = [12, 24]
        DOT_SIZE = FRETBOARD_LENGTH / 24 / 7
        STRING_DISTANCE = FRETBOARD_WIDTH / (STRING_NUMBER + 1)
        # how long the guitar string would be - only for calculating fret distance
        POTENTIAL_STRING_LENGTH = FRETBOARD_LENGTH * 1.3
        FRETS_COORDS = {}
        STRING_COORDS = {}

        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=FRETBOARD_WIDTH)
        self.canvas.create_rectangle(0, 0, FRETBOARD_LENGTH, FRETBOARD_WIDTH,  outline=constants['guitar_neck_color'], fill=constants['guitar_neck_color'])
        distance = 0
        for i in range(0, FRETS_NUMBER + 1):
            location = POTENTIAL_STRING_LENGTH - distance
            scaling_factor = location / 17.817    # http://www.buildyourguitar.com/resources/tips/fretdist.htm
            distance = distance + scaling_factor
            FRETS_COORDS[i] = {
                'x0': distance,
                'y0': 0,
                'x1': distance,
                'y1': FRETBOARD_WIDTH
            }
            self.canvas.create_line(*FRETS_COORDS[i].values(), fill=constants['guitar_frets_color'], width=2)

        for fret in range(1, 25):
            middle_point = (
                (FRETS_COORDS[fret]['x0'] + FRETS_COORDS[fret-1]['x0']) / 2,
                (FRETS_COORDS[fret]['y0'] + FRETS_COORDS[fret]['y1']) /2
            )    
            if fret in ONE_DOT_FRETS:
                self.canvas.create_oval(
                        middle_point[0] - DOT_SIZE,
                        middle_point[1] + DOT_SIZE,
                        middle_point[0] + DOT_SIZE,
                        middle_point[1] - DOT_SIZE,
                        outline=constants['guitar_dots_color'], fill=constants['guitar_dots_color']
                )
            elif fret in TWO_DOT_FRETS:
                self.canvas.create_oval(
                        middle_point[0] - DOT_SIZE,
                        FRETS_COORDS[fret]['y0'] + DOT_SIZE*3,
                        middle_point[0] + DOT_SIZE,
                        FRETS_COORDS[fret]['y0'] + DOT_SIZE*5,
                        outline=constants['guitar_dots_color'], fill=constants['guitar_dots_color']
                )           
                self.canvas.create_oval(
                        middle_point[0] - DOT_SIZE,
                        FRETS_COORDS[fret]['y1'] - DOT_SIZE*5,
                        middle_point[0] + DOT_SIZE,
                        FRETS_COORDS[fret]['y1'] - DOT_SIZE*3,
                        outline=constants['guitar_dots_color'], fill=constants['guitar_dots_color']
                )    
        for string in range(1, STRING_NUMBER+1):
            self.canvas.create_line(0, STRING_DISTANCE*string, FRETBOARD_LENGTH, STRING_DISTANCE*string, 
                                    fill=constants['guitar_strings_color'], width=1.5)

class Piano():
    def __init__(self, root, max_width):
        self.canvas = tk.Canvas(root)