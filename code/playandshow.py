import mido
import pygame
from commons import exception_catcher

MARGIN_X = 40
MARGIN_Y = 80

class NoInputException(Exception):
    """Raise when cannot open MIDO input"""

class Visualizer():

    @exception_catcher    
    def __init__(self, settings_client, size: tuple, show_guitar: bool, show_piano: bool,
                 guitar, piano, first_fret: int, last_fret: int, scale_type: str, max_bend: float,
                 reduce_bends: bool):
        self.settings_client = settings_client
        self.size = size
        self.guitar = guitar
        self.piano = piano
        self.first_fret = first_fret
        self.last_fret = last_fret
        self.scale_type = scale_type
        self.show_guitar = show_guitar
        self.show_piano = show_piano
        self.MAX_BEND = max_bend
        self.MAX_PITCH_SHIFT = 6000 # 2730
        self.ONE_STEP_PITCH = [-4095, 4096]
        self.BEND_PER_1_PITCH = self.MAX_BEND / self.MAX_PITCH_SHIFT
        self.intervals = self.settings_client.constants['scale_types'][scale_type]['intervals']
        self.guitar_notes_to_show = {}
        self.recude_bends = reduce_bends
        '''
        {(string number) 1:{
            "fret": 5,
            "interval": "p4",
            "bend": 2730
            }
        }
        '''
        self.piano_keys_to_show = set()
        # self.guitar_intervals_to_cover_up = []
        self.LABELED_FRET_TEXT_Y = float(self.guitar.FRETBOARD_WIDTH + self.guitar.TEXT_MARGIN/2)
        self.MIDDLE_FRET_Y = self.guitar.FRETBOARD_WIDTH / 2
        self.START_STRING_X = self.guitar.STRING_DICT[1]['coords']['x0'] + MARGIN_X
        self.END_STRING_X = self.guitar.STRING_DICT[1]['coords']['x1'] + MARGIN_X
        self.GUITAR_STRING_DICT = {
            string: {
                'x0': self.guitar.STRING_DICT[string]['coords']['x0'] + MARGIN_X,
                'x1': self.guitar.STRING_DICT[string]['coords']['x1'] + MARGIN_X,
                'y0': self.guitar.STRING_DICT[string]['coords']['y0'] + MARGIN_Y,
                'y1': self.guitar.STRING_DICT[string]['coords']['y1'] + MARGIN_Y
                }
            for string in self.guitar.STRING_DICT
            }
        self.GUITAR_FRET_DICT = {
            fret: {
                'x0': self.guitar.FRET_DICT[fret]['coords']['x0'] + MARGIN_X,
                'y0': self.guitar.FRET_DICT[fret]['coords']['y0'] + MARGIN_Y,
                'x1': self.guitar.FRET_DICT[fret]['coords']['x1'] + MARGIN_X,
                'y1': self.guitar.FRET_DICT[fret]['coords']['y1'] + MARGIN_Y,
                'middle_x': self.guitar.FRET_DICT[fret]['middle_x'] + MARGIN_X,
            }
            for fret in self.guitar.FRET_DICT
        }

        self.GUITAR_STRING_WIDTH_DICT = {string: int(0.5 + 0.5*string) for string in range(1,7)}        
        self.INTERVALS_TO_SHOW = []
        for string in self.settings_client.constants['guitar_strings']:
            string_number = self.settings_client.constants['guitar_strings'][string]['number']
            for fret in range(int(first_fret), int(last_fret)+1):
                note = self.settings_client.constants['guitar_strings'][string]['frets'][fret]
                interval = self.guitar.assigned_intervals[str(note)]
                if interval in self.intervals:
                    self.INTERVALS_TO_SHOW.append((fret, interval, string_number))
        
        pygame.font.init()
        self.fret_font = pygame.font.Font(pygame.font.get_default_font(), 16)
        self.interval_font = pygame.font.Font(pygame.font.get_default_font(), 
                self.settings_client.settings['interval_font_size'] + 5) #pygame is smaller than tkinter.....
        self.fret_range = range(self.first_fret, self.last_fret+1)
        self.run()

    @exception_catcher
    def no_midi_input(self, screen, fill_color):
        font_color = 'black' if not self.settings_client.settings['dark_theme'] else 'white'
        font = pygame.font.Font(pygame.font.get_default_font(), 30)
        screen.fill(fill_color)
        surface = font.render(
            self.settings_client.strings['no_midi_input'],
            False, font_color)
        screen.blit(surface, (screen.get_size()[0] / 4, screen.get_size()[1] //2 ))
        pygame.display.flip()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()      

    @exception_catcher
    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.size[0], self.size[1]))
        pygame.display.set_caption('Visualizing')
        icon = pygame.image.load('data/seeMidi.ico')
        pygame.display.set_icon(icon)        
        fill_color = 'black' if self.settings_client.settings['dark_theme'] else 'white'
        self.piano_margin_y = 0
        self.run_instruments(screen, fill_color)

    @exception_catcher
    def draw_guitar_base(self, screen: pygame.surface):
        pygame.draw.rect(screen, self.settings_client.settings['guitar_neck_color'], 
                         pygame.Rect(MARGIN_X, MARGIN_Y, self.guitar.FRETBOARD_LENGTH, self.guitar.FRETBOARD_WIDTH))
        fret = 0
        pygame.draw.line(screen, self.settings_client.settings['fret_zero_color'], 
                            (self.GUITAR_FRET_DICT[fret]['x0'], self.GUITAR_FRET_DICT[fret]['y0']),
                            (self.GUITAR_FRET_DICT[fret]['x1'], self.GUITAR_FRET_DICT[fret]['y1']),
                            width=10)    
        for fret in range(1, self.guitar.FRETS_NUMBER + 1):
            pygame.draw.line(screen, self.settings_client.settings['guitar_frets_color'], 
                             (self.GUITAR_FRET_DICT[fret]['x0'], self.GUITAR_FRET_DICT[fret]['y0']),
                             (self.GUITAR_FRET_DICT[fret]['x1'], self.GUITAR_FRET_DICT[fret]['y1']),
                             width=3)
            
        for fret in self.settings_client.constants['frets_labeled']:
            surface = self.fret_font.render(str(fret), False, (144, 144, 144))
            screen.blit(surface, (
                    self.GUITAR_FRET_DICT[fret]['middle_x'],
                    MARGIN_Y + self.LABELED_FRET_TEXT_Y
            ))
        
        for fret in self.guitar.ONE_DOT_FRETS:
            pygame.draw.circle(screen, self.settings_client.settings['guitar_dots_color'],
                (self.GUITAR_FRET_DICT[fret]['middle_x'], MARGIN_Y + self.MIDDLE_FRET_Y), 
                self.guitar.DOT_SIZE)

        for fret in self.guitar.TWO_DOT_FRETS:
            middle_point = (self.GUITAR_FRET_DICT[fret]['middle_x'], MARGIN_Y + self.MIDDLE_FRET_Y)
            pygame.draw.circle(screen, self.settings_client.settings['guitar_dots_color'],
                (middle_point[0], middle_point[1] - self.guitar.DOT_SIZE*5), self.guitar.DOT_SIZE)

            pygame.draw.circle(screen, self.settings_client.settings['guitar_dots_color'],
                (middle_point[0], middle_point[1] + self.guitar.DOT_SIZE*5), self.guitar.DOT_SIZE)     

    @exception_catcher
    def draw_guitar_strings(self, screen):
        for string in range(1, self.guitar.STRING_NUMBER+1):
            # string_y = self.guitar.STRING_DICT[string]['coords']['y0'] + MARGIN_Y
            string_y = self.GUITAR_STRING_DICT[string]['y0']
            if bend_val := self.guitar_notes_to_show.get(string,{}).get('bend'):
                # last string bends in other direction
                bend_y = (1 if string==1 else -1) * self.BEND_PER_1_PITCH * bend_val + string_y 
                bend_x = self.GUITAR_FRET_DICT[self.guitar_notes_to_show.get(string,{}).get('fret')]['middle_x']
                pygame.draw.line(screen, self.settings_client.settings['guitar_strings_color'], 
                                (self.START_STRING_X, string_y),
                                (bend_x, bend_y),
                                width=self.GUITAR_STRING_WIDTH_DICT[string])
                pygame.draw.line(screen, self.settings_client.settings['guitar_strings_color'], 
                                (bend_x, bend_y),
                                (self.END_STRING_X, string_y),
                                width=self.GUITAR_STRING_WIDTH_DICT[string])              
            else:
                pygame.draw.line(screen, self.settings_client.settings['guitar_strings_color'], 
                                (self.START_STRING_X, string_y),
                                (self.END_STRING_X, string_y),
                                width=self.GUITAR_STRING_WIDTH_DICT[string])

    @exception_catcher
    def show_fretboard(self, screen):
        for fret, interval, string in self.INTERVALS_TO_SHOW:
            self.draw_interval(screen, fret, interval, string)

    @exception_catcher
    def draw_interval(self, screen, fret: int, interval: str, 
                      string_number:int|None=None, is_played: bool=False):
        color = self.settings_client.settings['interval_color'][interval]['bg'] if not is_played else 'red'
        middle_x = self.GUITAR_FRET_DICT[fret]['middle_x']
        interval_y = self.GUITAR_STRING_DICT[string_number]['y0']        
        if self.guitar_notes_to_show.get(string_number,{}).get('bend') and \
            self.guitar_notes_to_show.get(string_number,{}).get('fret') == fret:
            interval_y += self.BEND_PER_1_PITCH * self.guitar_notes_to_show.get(string_number,{}).get('bend') * (1 if string_number == 1 else -1)
            
        pygame.draw.circle(screen, color,
                           (middle_x, interval_y),
                           radius=self.settings_client.settings['interval_label_radius'])
        
        if fret in self.fret_range and interval in self.intervals:
            surface = self.interval_font.render(
                self.settings_client.constants['all_intervals'][interval].encode('cp1252').decode(),
                    False, self.settings_client.settings['interval_color'][interval]['font'])
            surface_rect = surface.get_rect()
            surface_rect.center = (middle_x, interval_y)
            screen.blit(surface, surface_rect)        

    @exception_catcher
    def update_guitar(self, screen):
        self.draw_guitar_base(screen)
        self.draw_guitar_strings(screen)
        self.show_fretboard(screen)        
        for string_num, note in self.guitar_notes_to_show.items():
            self.draw_interval(screen, fret=note['fret'],
                                interval=note['interval'], string_number=string_num, is_played=True)                             

    @exception_catcher
    def update_piano(self, screen):
        self.draw_piano_base(screen)
        drawn = 0
        for white_key in filter(lambda x: x in self.piano.WHITE_KEYS_NBRS, self.piano_keys_to_show):
            self.draw_piano_key(screen, self.piano.keys[white_key]['type'],
                                            self.piano.keys[white_key]['x_pos'],
                                            pressed=True)
            self.draw_overlapping_piano_keys(screen, white_key)
            drawn +=1
        for black_key in filter(lambda x: x in self.piano.BLACK_KEYS_NBRS, self.piano_keys_to_show):
            self.draw_piano_key(screen, self.piano.keys[black_key]['type'],
                                            self.piano.keys[black_key]['x_pos'],
                                            pressed=True)
            drawn +=1

    @exception_catcher
    def draw_piano_base(self, screen):
        for key, values in self.piano.sorted_keys.items():
            self.draw_piano_key(screen, values['type'], values['x_pos'])

    @exception_catcher
    def draw_piano_key(self, screen, key_type: str, x_pos: float|int, pressed: bool = False):        
        if key_type == self.piano.w:
            rect = pygame.draw.rect(screen, color='white' if not pressed else 'red',
                             rect=pygame.Rect(MARGIN_X+x_pos, self.piano_margin_y, 
                            self.piano.white_key_width, self.piano.white_key_length),
                            border_radius=1)
            outline = rect.inflate(2, 2)
            pygame.draw.rect(screen, 'black', outline, 2)
        else:
            pygame.draw.rect(screen, color='black' if not pressed else 'red',
                             rect=pygame.Rect(MARGIN_X+x_pos, self.piano_margin_y, 
                            self.piano.black_key_width, self.piano.black_key_length),
                            border_radius=1)            
    
    @exception_catcher
    def draw_overlapping_piano_keys(self, screen, key_number):
        if self.piano.keys[key_number-1]['type'] == self.piano.b:                            
            self.draw_piano_key(screen, self.piano.b,
                                self.piano.keys[key_number-1]['x_pos'],
                                pressed=key_number-1 in self.piano_keys_to_show)
        if self.piano.keys[key_number+1]['type'] == self.piano.b:                            
            self.draw_piano_key(screen, self.piano.b,
                                self.piano.keys[key_number+1]['x_pos'],
                                pressed=key_number+1 in self.piano_keys_to_show)

    @exception_catcher
    def show_bored_screen(self, screen, fill_color):
        font_color = 'black' if not self.settings_client.settings['dark_theme'] else 'white'
        font = pygame.font.Font(pygame.font.get_default_font(), 40)
        screen.fill(fill_color)
        surface = font.render(
            "Please, choose anything. I'm bored. :( ",
              False, font_color)
        screen.blit(surface, (screen.get_size()[0] // 2, screen.get_size()[1] //2 ))
        pygame.display.flip()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()      

    @exception_catcher
    def run_instruments(self, screen, fill_color):
        #region prepare 
        running = True
        if self.show_guitar and self.show_piano:
            self.piano_margin_y = MARGIN_Y*2 + self.guitar.FRETBOARD_WIDTH            
            def x():
                self.update_guitar(screen)
                self.update_piano(screen)
            update_what_needs_to_be = x
        elif self.show_guitar:
            def x():
                self.update_guitar(screen)
            update_what_needs_to_be = x
        elif self.show_piano:
            self.piano_margin_y = MARGIN_Y
            def x():
                self.update_piano(screen)
            update_what_needs_to_be = x
        else:
            running = False
            self.show_bored_screen(screen, fill_color)            
        if running:
            try:
                inport = mido.open_input()
            except OSError:
                self.no_midi_input(screen, fill_color)
                return        
            screen.fill(fill_color)
            update_what_needs_to_be()
            pygame.display.flip()
            prev_signal = mido.Message(type='note_on')
        #endregion            

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    inport.close()
                    break
            for signal in inport.iter_pending():
                print(signal)
                if signal.channel < 0 or signal.channel > 5:
                    continue
                string_number = signal.channel + 1
                if signal.type == 'note_on': 
                    if signal.note not in self.piano.MIDI_INFO_DICT:
                        continue                   
                    piano_key_number = self.piano.MIDI_INFO_DICT[signal.note]
                    in_guitar_range = signal.note in self.guitar.MIDI_INFO_DICT[string_number]
                    if in_guitar_range:       
                        fret_number = self.guitar.MIDI_INFO_DICT[string_number][signal.note]['fret_number']
                        interval = self.guitar.MIDI_INFO_DICT[string_number][signal.note]['interval']
                    if signal.velocity > 0:
                        if note := self.guitar_notes_to_show.get(string_number):
                            try: self.piano_keys_to_show.remove(self.piano.MIDI_INFO_DICT[note.get('note')])
                            except: pass
                        if in_guitar_range:
                            self.guitar_notes_to_show[string_number] = {'fret': fret_number, 'interval': interval, 'note': signal.note}
                        self.piano_keys_to_show.add(piano_key_number)
                    else:
                        try:
                            if self.guitar_notes_to_show.get(string_number,{}).get('note') == signal.note:
                                del self.guitar_notes_to_show[string_number]
                        except:
                            pass
                        try: self.piano_keys_to_show.remove(piano_key_number)
                        except: pass
                elif signal.type == 'note_off':
                    print(f'[NOTE OFF]: {signal}\t\tcurrent:{self.guitar_notes_to_show.get(string_number)}')
                    piano_key_number = self.piano.MIDI_INFO_DICT.get(signal.note)
                    note = self.guitar_notes_to_show.get(string_number,{}).get('note')
                    if note == signal.note or \
                        note in range(signal.note-1, signal.note+2):
                            # prev_signal.type == 'pitchwheel' and \
                        try: del self.guitar_notes_to_show[string_number] 
                        except: pass
                        try: self.piano_keys_to_show.remove(self.piano.MIDI_INFO_DICT.get(note))
                        except: pass
                    else:
                        print(f'[NOTE OFF WTF] {signal}\t\t{note}')

                    try: self.piano_keys_to_show.remove(piano_key_number)
                    except: pass
                elif signal.type == 'pitchwheel':                    
                    if note := self.guitar_notes_to_show.get(string_number):
                        fret_number = note['fret']
                        interval = note['interval']
                        d = self.guitar_notes_to_show[string_number]   
                        hammer_on = False           
                        if signal.pitch == 0 and prev_signal.type == 'pitchwheel' and prev_signal.pitch in self.ONE_STEP_PITCH:
                            hammer_on = True
                            if prev_signal.pitch == self.ONE_STEP_PITCH[0]:                            
                                side = 1 # up
                            elif prev_signal.pitch == self.ONE_STEP_PITCH[1]:
                                side = -1 # down                            

                        if fret_number > 0 and signal.pitch in self.ONE_STEP_PITCH and \
                            (prev_signal.type != 'pitchwheel' or prev_signal.type == 'pitchwheel' and prev_signal.pitch == 0):
                            hammer_on = True
                            if signal.pitch == self.ONE_STEP_PITCH[0]:                            
                                side = -1 # down
                            elif signal.pitch == self.ONE_STEP_PITCH[1]:
                                side = 1 # up
                        if hammer_on:
                            try:
                                self.guitar_notes_to_show[string_number] = {'fret': d['fret']+1*side, 
                                                                    'interval': self.guitar.MIDI_INFO_DICT[string_number][d['note']+1*side]['interval'], 
                                                                    'note': d['note']+1*side}
                                piano_key_number = self.piano.MIDI_INFO_DICT[d['note']]
                                self.piano_keys_to_show.add(piano_key_number + 1*side)
                                self.piano_keys_to_show.remove(piano_key_number) if piano_key_number in self.piano_keys_to_show else None
                                update_what_needs_to_be()
                                pygame.display.flip()
                                prev_signal = signal
                                continue
                            except:
                                pass    
                        if signal.pitch < 0:
                            pitch = 0
                        elif signal.pitch > self.MAX_PITCH_SHIFT:
                            pitch = self.MAX_PITCH_SHIFT
                        else:
                            pitch = signal.pitch
                        self.guitar_notes_to_show[string_number] = {'fret': fret_number, 'interval': interval, 
                                                            'bend': pitch, 'note': self.guitar_notes_to_show[string_number].get('note')}
                if not self.guitar_notes_to_show and self.piano_keys_to_show:                    
                    self.piano_keys_to_show.clear()
                update_what_needs_to_be()
                pygame.display.flip()
                prev_signal = signal
        pygame.quit()