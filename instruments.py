from json import load
import tkinter as tk


class Guitar():

    def __init__(self, root, max_width, settings_client):    
        self.settings_client = settings_client
        self.font = ('Constantia', 10)
        self.CANVAS_WIDTH = max_width
        self.FRETBOARD_LENGTH = self.CANVAS_WIDTH - self.CANVAS_WIDTH // 25  # x axis
        self.FRETBOARD_WIDTH = self.FRETBOARD_LENGTH // 7
        self.STRING_NUMBER = 6
        self.FRETS_NUMBER = 24
        self.ONE_DOT_FRETS = [3, 5, 7, 9, 15, 17, 19, 21]
        self.TWO_DOT_FRETS = [12, 24]
        self.DOT_SIZE = self.FRETBOARD_LENGTH / 24 / 7
        self.STRING_DISTANCE = self.FRETBOARD_WIDTH / (self.STRING_NUMBER + 1)
        self.TEXT_MARGIN = self.FRETBOARD_WIDTH / 10  # how much place under the fretboard for fret labels (numbers)
        # how long the guitar string would be - only for calculating fret distance
        self.POTENTIAL_STRING_LENGTH = self.FRETBOARD_LENGTH * 1.3
        self.FRET_DICT = {}
        self.STRING_DICT = {} # High E is first string, low E is 6th string
        # !!! IMPORTANT !!!
        ''' 
        Updated in self.show_fretboard(). Holds information required for showing what's played through MIDI signal.
        self.MIDI_INFO_DICT = {
            (string number) 1: {
                (midi value) 64 : {
                    "fret_number": 1
                    "interval": "p4"
                } 
            }
        }
        '''
        self.MIDI_INFO_DICT = {}    

        self.canvas = tk.Canvas(root, width=int(self.CANVAS_WIDTH), height=int(self.FRETBOARD_WIDTH+self.TEXT_MARGIN))
        distance = 0
        for fret in range(0, self.FRETS_NUMBER + 1):
            location = self.POTENTIAL_STRING_LENGTH - distance
            self.FRET_DICT[fret] = {}
            self.FRET_DICT[fret]['coords'] = {
                'x0': distance,
                'y0': 0,
                'x1': distance,
                'y1': self.FRETBOARD_WIDTH
            }            
            scaling_factor = location / 17.817    # http://www.buildyourguitar.com/resources/tips/fretdist.htm
            distance = distance + scaling_factor            

        for string in range(1, self.STRING_NUMBER+1):
            # first string is high E
            self.STRING_DICT[string] = {}
            self.STRING_DICT[string]['coords'] = {
                'x0': 0,
                'y0': self.STRING_DISTANCE*string,
                'x1': self.FRETBOARD_LENGTH,
                'y1': self.STRING_DISTANCE*string
            }
        
        for string in self.settings_client.constants['guitar_strings']:
            # determine notes on the fretboard
            open_note = 'E' if string == "EE" else string
            note_idx = self.settings_client.constants['all_notes_grouped'].index(
                next(filter(lambda x: open_note in x, self.settings_client.constants['all_notes_grouped']))
            )
            for fret in range(self.FRETS_NUMBER+1):
                self.settings_client.constants['guitar_strings'][string]['frets'].append(self.settings_client.constants['all_notes_grouped'][note_idx])
                note_idx = note_idx + 1 if  note_idx + 1 < len(self.settings_client.constants['all_notes_grouped']) else 0        
        self.draw_guitar()        
    
    def draw_guitar(self):
        self.canvas.create_rectangle(0, 0, self.FRETBOARD_LENGTH, self.FRETBOARD_WIDTH,  
                outline=self.settings_client.settings['guitar_neck_color'], fill=self.settings_client.settings['guitar_neck_color'])
        for fret in range(0, self.FRETS_NUMBER + 1):  
            self.canvas.create_line(*self.FRET_DICT[fret]['coords'].values(), 
                                    fill=self.settings_client.settings['guitar_frets_color'], width=2)
            if fret in self.settings_client.constants['frets_labeled']:
                self.canvas.create_text(
                    self.FRET_DICT[fret-1]['coords']['x0'] + (self.FRET_DICT[fret]['coords']['x0'] - self.FRET_DICT[fret-1]['coords']['x0'])/2,
                    float(self.FRETBOARD_WIDTH + self.TEXT_MARGIN/2),
                    text = str(fret)
                )

        for fret in range(1, self.FRETS_NUMBER+1):
            middle_point = (
                (self.FRET_DICT[fret]['coords']['x0'] + self.FRET_DICT[fret-1]['coords']['x0']) / 2,
                (self.FRET_DICT[fret]['coords']['y0'] + self.FRET_DICT[fret]['coords']['y1']) /2
            )    
            if fret in self.ONE_DOT_FRETS:
                self.canvas.create_oval(
                        middle_point[0] - self.DOT_SIZE,
                        middle_point[1] + self.DOT_SIZE,
                        middle_point[0] + self.DOT_SIZE,
                        middle_point[1] - self.DOT_SIZE,
                        outline=self.settings_client.settings['guitar_dots_color'], 
                        fill=self.settings_client.settings['guitar_dots_color']
                )
            elif fret in self.TWO_DOT_FRETS:
                self.canvas.create_oval(
                        middle_point[0] - self.DOT_SIZE,
                        self.FRET_DICT[fret]['coords']['y0'] + self.DOT_SIZE*3,
                        middle_point[0] + self.DOT_SIZE,
                        self.FRET_DICT[fret]['coords']['y0'] + self.DOT_SIZE*5,
                        outline=self.settings_client.settings['guitar_dots_color'], 
                        fill=self.settings_client.settings['guitar_dots_color']
                )           
                self.canvas.create_oval(
                        middle_point[0] - self.DOT_SIZE,
                        self.FRET_DICT[fret]['coords']['y1'] - self.DOT_SIZE*5,
                        middle_point[0] + self.DOT_SIZE,
                        self.FRET_DICT[fret]['coords']['y1'] - self.DOT_SIZE*3,
                        outline=self.settings_client.settings['guitar_dots_color'], 
                        fill=self.settings_client.settings['guitar_dots_color']
                )   

        for string in range(1, self.STRING_NUMBER+1):
            self.canvas.create_line(*self.STRING_DICT[string]['coords'].values(),
                                    fill=self.settings_client.settings['guitar_strings_color'], 
                                    width=int(0.5 + 0.5*string))
        
    def get_midi_value_open_string(self, string_name: str):
        match string_name:
            case "E":
                midi_val = 40
            case "A":
                midi_val = 45
            case "D":
                midi_val = 50
            case "G":
                midi_val = 55
            case "B": 
                midi_val = 59
            case "EE":
                midi_val = 64
        return midi_val

    def show_fretboard(self, root_note, scale_type_name, first_fret, last_fret):
        self.canvas.delete('all')
        self.draw_guitar()
        root_note_idx = self.settings_client.constants['all_notes_grouped'].index(
            next(filter(lambda x: root_note in x, self.settings_client.constants['all_notes_grouped']))
        )
        scale_type = next(filter(lambda x: self.settings_client.strings[x]==scale_type_name, self.settings_client.strings))
        sorted_notes = self.settings_client.constants['all_notes_grouped'][root_note_idx:] + self.settings_client.constants['all_notes_grouped'][: root_note_idx]
        self.assigned_intervals = {}
        for note, interval in zip(sorted_notes, self.settings_client.constants['all_intervals']):
            self.assigned_intervals[str(note)] = interval
        for string in self.settings_client.constants['guitar_strings']:
            string_num = self.settings_client.constants['guitar_strings'][string]['number']
            self.MIDI_INFO_DICT[string_num] = {}
            midi_val = self.get_midi_value_open_string(string)
            for fret in range(1, self.settings_client.constants['frets_number']+1):
                midi_val += 1
                note = self.settings_client.constants['guitar_strings'][string]['frets'][fret]
                interval = self.assigned_intervals[str(note)]
                self.MIDI_INFO_DICT[string_num][midi_val] = {
                    "fret_number": fret,
                    "interval": interval
                }
                if fret in range(int(first_fret), int(last_fret)+1) and \
                        interval in self.settings_client.constants['scale_types'][scale_type]['intervals']:
                    self.draw_interval(string, fret, interval)

    def draw_interval(self, string: str, fret: str, interval: str):
        r = self.settings_client.settings['interval_label_radius']
        string_number = self.settings_client.constants['guitar_strings'][string]['number']
        middle_x = (self.FRET_DICT[fret-1]['coords']['x0'] + self.FRET_DICT[fret]['coords']['x0']) / 2
        self.canvas.create_oval(
            middle_x - r,
            self.STRING_DICT[string_number]['coords']['y0'] - r,
            middle_x + r,
            self.STRING_DICT[string_number]['coords']['y0'] + r,
            outline=self.settings_client.settings['interval_color'][interval]['bg'], 
            fill=self.settings_client.settings['interval_color'][interval]['bg']
        )
        self.canvas.create_text(
            middle_x,
            self.STRING_DICT[string_number]['coords']['y0'],
            font=('Aria', self.settings_client.settings['interval_font_size']),
            text = str(self.settings_client.constants['all_intervals'][interval].encode('cp1252').decode()),
            fill=self.settings_client.settings['interval_color'][interval]['font'],            
        )


class Piano():

    def __init__(self, root, max_width, settings_client):
        self.settings_client = settings_client
        self.CANVAS_WIDTH = max_width
        self.KEYBOARD_LENGTH = self.CANVAS_WIDTH - self.CANVAS_WIDTH // 10  # x axis, horizontal
        self.KEYBOARD_WIDTH = self.KEYBOARD_LENGTH // 6 # y axis, vertical
        self.canvas = tk.Canvas(root, width=int(self.CANVAS_WIDTH), height=int(self.KEYBOARD_WIDTH))
        self.OCTAVES_NUMBER = 4
        self.KEYS_PADDING_BOTTOM = 10

        self.white_key_width = self.KEYBOARD_LENGTH / (self.OCTAVES_NUMBER*7) # x axis, horizontal
        self.white_key_length = self.KEYBOARD_WIDTH - self.KEYS_PADDING_BOTTOM # y axis, vertical
        self.black_key_width = self.white_key_width * 0.75
        self.black_key_length = self.white_key_length * 0.6
        self.b = b = 'b'    # black key signature
        self.w = w ='w'    # white key signature
        self.octave = [w,b,w,b,w, w,b,w,b,w,b,w] # c, c#, d, d#, e,   f, f#, g, g#, a, a#, b
        # 4 octaves from E to E (like in guitar)
        self.all_keys = self.octave[4:] + self.octave * 3 + self.octave[:5]
        self.keys = {}
        idx = 4 # starting from E
        x_pos_white = 0
        for key_num, key in enumerate(self.all_keys):
            self.keys[key_num] = {
                'note': self.settings_client.constants['all_notes_grouped'][idx],
                'type': key
            }
            idx = idx + 1 if idx+1 < len(self.settings_client.constants['all_notes_grouped']) else 0
            if key == self.w:
                self.keys[key_num]['x_pos'] = x_pos_white
                x_pos_white = x_pos_white + self.white_key_width 
            else:
                self.keys[key_num]['x_pos'] = x_pos_white - (self.black_key_width / 2)
                
        self.sorted_keys = dict(sorted(self.keys.items(), key=lambda item: item[1]['type'], reverse=True))
        self.draw_piano()

    def draw_key(self, key_type: str, x_pos: float|int):
        if key_type == self.w:
            self.canvas.create_rectangle(x_pos, 0, self.white_key_width + x_pos, self.white_key_length,
                                         outline='black', fill='white')
        else:
            self.canvas.create_rectangle(x_pos, 0, self.black_key_width + x_pos, self.black_key_length,
                                         outline='black', fill='black')
            

    def draw_piano(self):
        for key, values in self.sorted_keys.items():
            self.draw_key(values['type'], values['x_pos'])
