import pygame
import mido
import time # debug

MARGIN_X = 40
MARGIN_Y = 80

class Visualizer():
    def __init__(self, settings_client, size: tuple, show_guitar: bool, show_piano: bool,
                 guitar, piano, first_fret: int, last_fret: int, scale_type: str, max_bend: float,
                 play_demo: bool=False):
        self.settings_client = settings_client
        self.size = size
        self.guitar = guitar
        self.piano = piano
        self.first_fret = first_fret
        self.last_fret = last_fret
        self.scale_type = scale_type
        self.show_guitar = show_guitar
        self.show_piano = show_piano
        self.play_demo = play_demo
        self.MAX_BEND = max_bend
        self.MAX_PITCH_SHIFT = 2730
        self.BEND_PER_1_PITCH = self.MAX_BEND / self.MAX_PITCH_SHIFT
        self.intervals = self.settings_client.constants['scale_types'][scale_type]['intervals']
        self.guitar_notes_to_show = {}
        '''
        {(string number) 1:{
            "fret": 5,
            "interval": "p4",
            "bend": 2730
            }
        }
        '''
        self.piano_keys_to_show = set()
        self.guitar_intervals_to_cover_up = []
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

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.size[0], self.size[1]))
        pygame.display.set_caption('Visualizing')
        icon = pygame.image.load('data/seeMidi.ico')
        pygame.display.set_icon(icon)        
        fill_color = 'black' if self.settings_client.settings['dark_theme'] else 'white'
        self.piano_margin_y = 0
        if self.show_guitar:
            if self.show_piano:
                self.piano_margin_y = MARGIN_Y*2 + self.guitar.FRETBOARD_WIDTH
                if self.play_demo:
                    self.run_demo(screen, fill_color)
                else:
                    self.run_both(screen, fill_color)                
            else:
                self.run_guitar(screen, fill_color)
        elif self.show_piano:
            self.piano_margin_y = MARGIN_Y
            self.run_piano(screen, fill_color)            
        else:
            self.show_bored_screen(screen, fill_color)


    def run_both(self, screen, fill_color):
        clock = pygame.time.Clock()        
        dt = 0
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill(fill_color)
            self.draw_guitar_base(screen)
            self.draw_guitar_strings(screen)
            self.show_fretboard(screen)

            self.draw_piano_base(screen)

            pygame.display.flip()
        pygame.quit()

    def run_guitar(self, screen, fill_color):
        clock = pygame.time.Clock()        
        dt = 0
        running = True
        inport = mido.open_input()
        screen.fill(fill_color)
        self.draw_guitar_base(screen)
        self.draw_guitar_strings(screen)
        self.show_fretboard(screen)      
        print(f'[START] {mido.get_input_names()}')  
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            msg = inport.receive()
            print(msg)

            # screen.fill(fill_color)
            # self.draw_guitar_base(screen)
            # self.draw_guitar_strings(screen)
            # self.show_fretboard(screen)

            pygame.display.flip()
        pygame.quit()        

    def run_piano(self, screen, fill_color):
        clock = pygame.time.Clock()        
        dt = 0
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill(fill_color)
            self.draw_piano_base(screen)

            pygame.display.flip()
        pygame.quit()        
 
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
            surface = self.fret_font.render(str(fret), False, (0, 0, 0))
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

    def draw_guitar_strings(self, screen):
        for string in range(1, self.guitar.STRING_NUMBER+1):
            # string_y = self.guitar.STRING_DICT[string]['coords']['y0'] + MARGIN_Y
            string_y = self.GUITAR_STRING_DICT[string]['y0']
            if bend_val := self.guitar_notes_to_show.get(string,{}).get('bend'):
                # last string bends in other direction
                bend_y = (-1 if string==6 else 1) * self.BEND_PER_1_PITCH * bend_val + string_y 
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

    def show_fretboard(self, screen):
        for fret, interval, string in self.INTERVALS_TO_SHOW:
            self.draw_interval(screen, fret, interval, string)

    def draw_interval(self, screen, fret: int, interval: str, 
                      string_number:int|None=None, is_played: bool=False):
        color = self.settings_client.settings['interval_color'][interval]['bg'] if not is_played else 'red'
        middle_x = self.GUITAR_FRET_DICT[fret]['middle_x']
        interval_y = self.GUITAR_STRING_DICT[string_number]['y0']        
        if self.guitar_notes_to_show.get(string_number,{}).get('bend') and \
            self.guitar_notes_to_show.get(string_number,{}).get('fret') == fret:
            interval_y += self.BEND_PER_1_PITCH * self.guitar_notes_to_show.get(string_number,{}).get('bend') * (-1 if string_number == 6 else 1)
            
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

    def update_info_on_guitar(self, erase_note: tuple) -> bool:
        ''' Returns info if whole guitar should be re-drawn'''
        # note info: (fret_number, interval, string_number)
        try:
            del self.guitar_notes_to_show[erase_note[2]]     
        except:
            pass # well, it happend, just let it go. It was never that serious. - time optimalization
        if erase_note[1] in self.intervals and erase_note[0] in self.fret_range:
            # you can just draw default circle on it
            self.guitar_intervals_to_cover_up.append(erase_note)
        else:
            return True
        return False

    def update_guitar(self, screen, redraw: bool=True):
        if redraw:
            self.draw_guitar_base(screen)
            self.draw_guitar_strings(screen)
            self.show_fretboard(screen)        
        else:
            for note in self.guitar_intervals_to_cover_up:
                self.draw_interval(screen, fret=note[0],
                                    interval=note[1], string_number=note[2], is_played=False)   
        for string_num, note in self.guitar_notes_to_show.items():
            self.draw_interval(screen, fret=note['fret'],
                                interval=note['interval'], string_number=string_num, is_played=True)                             

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
        print(f'drawn: {drawn}: {self.piano_keys_to_show}')

    def draw_piano_base(self, screen):
        for key, values in self.piano.sorted_keys.items():
            self.draw_piano_key(screen, values['type'], values['x_pos'])

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
    
    def draw_overlapping_piano_keys(self, screen, key_number):
        if self.piano.keys[key_number-1]['type'] == self.piano.b:                            
            self.draw_piano_key(screen, self.piano.b,
                                self.piano.keys[key_number-1]['x_pos'],
                                pressed=key_number-1 in self.piano_keys_to_show)
        if self.piano.keys[key_number+1]['type'] == self.piano.b:                            
            self.draw_piano_key(screen, self.piano.b,
                                self.piano.keys[key_number+1]['x_pos'],
                                pressed=key_number+1 in self.piano_keys_to_show)

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

    def run_demo(self, screen, fill_color):
        # midi_filename = 'midis/bbcc.mid'
        # chosen_string_num = 3

        # midi_filename = 'midis/Bends.mid'
        chosen_string_num = 1

        # mid = mido.MidiFile(midi_filename).play()
        # signals = mid.play(meta_messages=False)
        # signals_list = [
        #     None,
        #     mido.MidiFile(midi_filename).play(),
        #     mido.MidiFile(midi_filename).play(),
        #     mido.MidiFile('midis/string3.mid').play(),
        #     mido.MidiFile('midis/string4.mid').play(),
        #     mido.MidiFile('midis/string5.mid').play(),
        #     # mido.MidiFile('midis/string6.mid').play()
        # ]
        inport = mido.open_input()
        screen.fill(fill_color)
        self.draw_guitar_base(screen)
        self.draw_guitar_strings(screen)
        self.show_fretboard(screen)
        self.draw_piano_base(screen)       
        pygame.display.flip()        
        running = True
        # pygame.mixer.music.load(midi_filename)
        # pygame.mixer.music.play()
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
                    key_number = self.piano.MIDI_INFO_DICT[signal.note]
                    in_guitar_range = signal.note in self.guitar.MIDI_INFO_DICT[string_number]
                    if in_guitar_range:       
                        fret_number = self.guitar.MIDI_INFO_DICT[string_number][signal.note]['fret_number']
                        interval = self.guitar.MIDI_INFO_DICT[string_number][signal.note]['interval']
                    if signal.velocity > 0:
                        if in_guitar_range:
                            self.guitar_notes_to_show[string_number] = {'fret': fret_number, 'interval': interval}
                        self.piano_keys_to_show.add(key_number)
                        # self.draw_piano_key(screen, self.piano.keys[key_number]['type'],
                        #                     self.piano.keys[key_number]['x_pos'],
                        #                     pressed=True)
                        # self.draw_overlapping_piano_keys(screen, key_number)                            
                    else:
                        # if in_guitar_range:
                            # erase_note = (fret_number, interval, string_number)
                            # to_redraw = self.update_info_on_guitar(erase_note)
                        # self.draw_piano_key(screen, self.piano.keys[key_number]['type'],
                        #                     self.piano.keys[key_number]['x_pos'],
                        #                     pressed=False)
                        # try-except for time optimization
                        try:
                            del self.guitar_notes_to_show[string_number]
                        except:
                            pass
                        try:
                            self.piano_keys_to_show.remove(key_number)
                            print(f'Deleting key: {key_number}. Keys: {self.piano_keys_to_show}')
                        except:
                            pass
                        # self.draw_overlapping_piano_keys(screen, key_number)
                    # update_screen = True         
                elif signal.type == 'note_off':
                    # in_guitar_range = signal.note in self.guitar.MIDI_INFO_DICT[string_number]
                    # if in_guitar_range:
                    #     fret_number = self.guitar.MIDI_INFO_DICT[string_number][signal.note]['fret_number']
                    #     interval = self.guitar.MIDI_INFO_DICT[string_number][signal.note]['interval']                        
                    #     erase_note = (fret_number, interval, string_number)
                    #     to_redraw = self.update_info_on_guitar(erase_note)
                    # self.draw_piano_key(screen, self.piano.keys[key_number]['type'],
                    #                     self.piano.keys[key_number]['x_pos'],
                    #                     pressed=False)
                    # try:
                    #     self.piano_keys_to_show.remove(key_number)
                    # except:
                    #     pass
                    # self.draw_overlapping_piano_keys(screen, key_number)                        
                    # update_screen = True
                    try:
                        del self.guitar_notes_to_show[string_number]
                    except:
                        pass
                    try:
                        self.piano_keys_to_show.remove(key_number)
                        print(f'Deleting key: {key_number}. Keys: {self.piano_keys_to_show}')
                    except:
                        pass                    
                elif signal.type == 'pitchwheel':
                    if note := self.guitar_notes_to_show.get(string_number):
                        fret_number = note['fret']
                        interval = note['interval']
                        # if signal.pitch == 0:
                        #     self.guitar_notes_to_show[string_number] = {'fret': fret_number, 'interval': interval}
                        # else:
                        self.guitar_notes_to_show[string_number] = {'fret': fret_number, 'interval': interval, 'bend': signal.pitch}                        
                        # update_screen = True
                        # to_redraw = True
            # if update_screen:
                self.update_guitar(screen) #, to_redraw)                
                self.update_piano(screen)
                pygame.display.flip()
        pygame.quit()        