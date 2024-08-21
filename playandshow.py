import pygame
import mido

MARGIN_X = 40
MARGIN_Y = 80

class Visualizer():
    def __init__(self, settings_client, size: tuple, show_guitar: bool, show_piano: bool,
                 guitar, piano, first_fret: int, last_fret: int, scale_type: str,
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
        self.intervals = self.settings_client.constants['scale_types'][scale_type]['intervals']
        pygame.font.init()
        self.fret_font = pygame.font.Font(pygame.font.get_default_font(), 16)
        self.interval_font = pygame.font.Font(pygame.font.get_default_font(), 
                self.settings_client.settings['interval_font_size'] + 5) #pygame is smaller than tkinter.....
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
            self.show_fretboard(screen, self.scale_type, self.first_fret, self.last_fret)

            self.draw_piano_base(screen)

            pygame.display.flip()
        pygame.quit()

    def run_guitar(self, screen, fill_color):
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
            self.show_fretboard(screen, self.scale_type, self.first_fret, self.last_fret)

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

        for fret in range(0, self.guitar.FRETS_NUMBER + 1):
            pygame.draw.line(screen, self.settings_client.settings['guitar_frets_color'], 
                             (self.guitar.FRET_DICT[fret]['coords']['x0'] + MARGIN_X, self.guitar.FRET_DICT[fret]['coords']['y0'] + MARGIN_Y),
                             (self.guitar.FRET_DICT[fret]['coords']['x1'] + MARGIN_X, self.guitar.FRET_DICT[fret]['coords']['y1'] + MARGIN_Y),
                             width=3)
            
            if fret in self.settings_client.constants['frets_labeled']:
                surface = self.fret_font.render(str(fret), False, (0, 0, 0))
                screen.blit(surface, (
                        MARGIN_X + self.guitar.FRET_DICT[fret-1]['coords']['x0'] + (self.guitar.FRET_DICT[fret]['coords']['x0'] - self.guitar.FRET_DICT[fret-1]['coords']['x0'])/2,
                        MARGIN_Y + float(self.guitar.FRETBOARD_WIDTH + self.guitar.TEXT_MARGIN/2)
                ))
        
        for fret in range(1, self.guitar.FRETS_NUMBER+1):
            middle_point = (
                MARGIN_X + (self.guitar.FRET_DICT[fret]['coords']['x0'] + self.guitar.FRET_DICT[fret-1]['coords']['x0']) / 2,
                MARGIN_Y + (self.guitar.FRET_DICT[fret]['coords']['y0'] + self.guitar.FRET_DICT[fret]['coords']['y1']) /2
            )    
            if fret in self.guitar.ONE_DOT_FRETS:
                pygame.draw.circle(screen, self.settings_client.settings['guitar_dots_color'],
                                   middle_point, self.guitar.DOT_SIZE)

            elif fret in self.guitar.TWO_DOT_FRETS:
                pygame.draw.circle(screen, self.settings_client.settings['guitar_dots_color'],
                    (middle_point[0], middle_point[1] - self.guitar.DOT_SIZE*5), self.guitar.DOT_SIZE)
  
                pygame.draw.circle(screen, self.settings_client.settings['guitar_dots_color'],
                    (middle_point[0], middle_point[1] + self.guitar.DOT_SIZE*5), self.guitar.DOT_SIZE)     

    def draw_guitar_strings(self, screen):
        for string in range(1, self.guitar.STRING_NUMBER+1):
            pygame.draw.line(screen, self.settings_client.settings['guitar_strings_color'], 
                             (self.guitar.STRING_DICT[string]['coords']['x0'] + MARGIN_X, self.guitar.STRING_DICT[string]['coords']['y0'] + MARGIN_Y),
                             (self.guitar.STRING_DICT[string]['coords']['x1'] + MARGIN_X, self.guitar.STRING_DICT[string]['coords']['y1'] + MARGIN_Y),
                             width=int(0.5 + 0.5*string))    

    def show_fretboard(self, screen, scale_type, first_fret, last_fret):
        for string in self.settings_client.constants['guitar_strings']:
            for fret in range(int(first_fret), int(last_fret)+1):
                note = self.settings_client.constants['guitar_strings'][string]['frets'][fret]
                interval = self.guitar.assigned_intervals[str(note)]
                if interval in self.intervals:
                    self.draw_interval(screen, fret, interval, string)

    def draw_interval(self, screen, fret: str, interval: str, string: str|None=None, 
                      string_number:int|None=None, is_played: bool=False):
        color = self.settings_client.settings['interval_color'][interval]['bg'] if not is_played else 'red'
        string_number = self.settings_client.constants['guitar_strings'][string]['number'] if not string_number else string_number
        middle_x = MARGIN_X + (self.guitar.FRET_DICT[fret-1]['coords']['x0'] + self.guitar.FRET_DICT[fret]['coords']['x0']) / 2
        pygame.draw.circle(screen, color,
                           (middle_x, MARGIN_Y + self.guitar.STRING_DICT[string_number]['coords']['y0']),
                           radius=self.settings_client.settings['interval_label_radius'])
        
        if interval in self.intervals:
            surface = self.interval_font.render(
                self.settings_client.constants['all_intervals'][interval].encode('cp1252').decode().replace('♭','b'), 
                    False, self.settings_client.settings['interval_color'][interval]['font'])
            surface_rect = surface.get_rect()
            surface_rect.center = (
                    middle_x,
                    MARGIN_Y + self.guitar.STRING_DICT[string_number]['coords']['y0']
            )
            screen.blit(surface, surface_rect)        

    def update_guitar(self):
        pass

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
            
    def update_piano(self):
        pass

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
        clock = pygame.time.Clock()        
        dt = 0
        mid = mido.MidiFile('mad.mid')
        signals = mid.play(meta_messages=True)
        screen.fill(fill_color)
        self.draw_guitar_base(screen)
        self.draw_guitar_strings(screen)
        self.show_fretboard(screen, self.scale_type, self.first_fret, self.last_fret)
        self.draw_piano_base(screen)        
        running = True
        pygame.mixer.music.load("mad.mid")
        pygame.mixer.music.play(-1, 0.0)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if signal := next(signals, None):
                if signal.type == 'note_on':
                    if signal.note not in self.guitar.MIDI_INFO_DICT[2]:
                        continue
                    fret_number = self.guitar.MIDI_INFO_DICT[2][signal.note]['fret_number']
                    interval = self.guitar.MIDI_INFO_DICT[2][signal.note]['interval']                    
                    if signal.velocity > 0:
                        if signal.note not in self.guitar.MIDI_INFO_DICT[2]:
                            continue
                        self.draw_interval(screen, fret_number, interval, 
                                           string_number=2, is_played=True)
                    else:
                        self.draw_interval(screen, fret_number, interval, 
                                           string_number=2, is_played=False)
                elif signal.type == 'note_off':
                    print("NOTE OFF SINGAL!")
                        # self.draw_interval(screen, fret_number, interval, 
                        #                    string_number=2, is_played=False)

                # screen.fill(fill_color)
                # self.draw_guitar_base(screen)
                # self.draw_guitar_strings(screen)
                # self.show_fretboard(screen, self.scale_type, self.first_fret, self.last_fret)
                # self.draw_piano_base(screen)
                pygame.display.flip()
                d=1
        pygame.quit()        