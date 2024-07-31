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
        TEXT_MARGIN = FRETBOARD_WIDTH / 10  # how much place under the fretboard for fret labels (numbers)
        # how long the guitar string would be - only for calculating fret distance
        POTENTIAL_STRING_LENGTH = FRETBOARD_LENGTH * 1.3
        FRET_DICT = {}
        STRING_DICT = {} # High E is first string, low E is 6th string


        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=FRETBOARD_WIDTH+TEXT_MARGIN)
        self.canvas.create_rectangle(0, 0, FRETBOARD_LENGTH, FRETBOARD_WIDTH,  outline=constants['guitar_neck_color'], fill=constants['guitar_neck_color'])
        distance = 0
        for fret in range(0, FRETS_NUMBER + 1):
            location = POTENTIAL_STRING_LENGTH - distance
            FRET_DICT[fret] = {}
            FRET_DICT[fret]['coords'] = {
                'x0': distance,
                'y0': 0,
                'x1': distance,
                'y1': FRETBOARD_WIDTH
            }            
            scaling_factor = location / 17.817    # http://www.buildyourguitar.com/resources/tips/fretdist.htm
            distance = distance + scaling_factor            
            self.canvas.create_line(*FRET_DICT[fret]['coords'].values(), fill=constants['guitar_frets_color'], width=2)
            if fret in constants['frets_labeled']:
                self.canvas.create_text(
                    FRET_DICT[fret-1]['coords']['x0'] + (FRET_DICT[fret]['coords']['x0'] - FRET_DICT[fret-1]['coords']['x0'])/2,
                    float(FRETBOARD_WIDTH + TEXT_MARGIN/2),
                    text = str(fret)
                )

        for fret in range(1, FRETS_NUMBER+1):
            FRET_DICT[fret] = constants['all_notes_grouped']
            middle_point = (
                (FRET_DICT[fret]['coords']['x0'] + FRET_DICT[fret-1]['coords']['x0']) / 2,
                (FRET_DICT[fret]['coords']['y0'] + FRET_DICT[fret]['coords']['y1']) /2
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
                        FRET_DICT[fret]['coords']['y0'] + DOT_SIZE*3,
                        middle_point[0] + DOT_SIZE,
                        FRET_DICT[fret]['coords']['y0'] + DOT_SIZE*5,
                        outline=constants['guitar_dots_color'], fill=constants['guitar_dots_color']
                )           
                self.canvas.create_oval(
                        middle_point[0] - DOT_SIZE,
                        FRET_DICT[fret]['coords']['y1'] - DOT_SIZE*5,
                        middle_point[0] + DOT_SIZE,
                        FRET_DICT[fret]['coords']['y1'] - DOT_SIZE*3,
                        outline=constants['guitar_dots_color'], fill=constants['guitar_dots_color']
                )   

        for string in range(1, STRING_NUMBER+1):
            STRING_DICT[string] = {}
            STRING_DICT[string]['coords'] = {
                'x0': 0,
                'y0': STRING_DISTANCE*string,
                'x1': FRETBOARD_LENGTH,
                'y1': STRING_DISTANCE*string
            }
            self.canvas.create_line(*STRING_DICT[string]['coords'].values(),
                                    fill=constants['guitar_strings_color'], width=0.5 + 0.5*string)

    def show_frets(self, root_note, scale_type, first_fret, last_fret):
        pass

class Piano():
    def __init__(self, root, max_width):
        self.canvas = tk.Canvas(root)