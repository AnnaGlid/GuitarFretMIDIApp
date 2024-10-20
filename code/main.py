import tkinter as tk
import ttkbootstrap as tb
import ttkbootstrap.constants as tb_const
from ttkbootstrap.scrolled import ScrolledFrame

from commons import exception_catcher
from settings import Settings
from playandshow import Visualizer
from instruments import Guitar, Piano
from signalconfig import SignalConfig

class App:

    @exception_catcher
    def __init__(self):
        row = 0
        self.settings_client = Settings(self)
        theme = 'darkly' if self.settings_client.settings['dark_theme'] else 'cosmo'
        self.root = tb.Window(themename=theme)

        self.root.iconbitmap('data/seeMidi.ico')
        self.root.title("See MIDI")
        self.root.geometry('{}x{}'.format(*self.root.maxsize()))
        self.root.state('zoomed')
        self.settings_client = Settings(self)
        self.menubar = tk.Menu(self.root)
        self.signal_config = SignalConfig(self.settings_client)
        # settings
        self.settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.settings_menu.add_command(label=self.settings_client.strings['settings'], command=self.settings_client.open)
        self.settings_menu.add_command(label=self.settings_client.strings['revert_to_default'], command=self.settings_client.revert_to_default)
        self.menubar.add_cascade(label=self.settings_client.strings['settings'], menu=self.settings_menu)
        # tools
        self.tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.tools_menu.add_command(label=self.settings_client.strings['signal_config'], command=self.signal_config.start)
        self.menubar.add_cascade(label=self.settings_client.strings['tools'], menu=self.tools_menu)

        self.root.config(menu=self.menubar)
        self.root_frame = ScrolledFrame(self.root, autohide=True)
        self.root_frame.pack(fill=tb_const.BOTH, expand=tb_const.YES, padx=10, pady=10)        

        #region guitar
        self.guitar_frame = tb.Frame(self.root_frame, bootstyle="default")
        self.guitar = Guitar(self.guitar_frame, self.root.maxsize()[0], self.settings_client)
        self.guitar_frame_grid_params = {
            "row": row,
            "padx": 20,
            "pady": 30,
            "sticky": "se"
        }
        self.guitar.canvas.grid()        
        separator = tb.Separator(self.guitar_frame, bootstyle="default", orient='horizontal')
        separator.grid(pady=10, sticky='we')        
        self.guitar_frame.grid(**self.guitar_frame_grid_params)
        row += 1
        #endregion

        #region piano
        self.piano_frame = tb.Frame(self.root_frame, bootstyle="default")
        self.piano = Piano(self.piano_frame, self.root.maxsize()[0], self.settings_client)
        self.piano_frame_grid_params = {
            "row": row,
            "padx": 20,
            "pady": 10,
            "sticky": "se"
        }
        row += 1
        self.piano.canvas.grid(sticky='nesw')        
        separator = tb.Separator(self.piano_frame, bootstyle="default", orient='horizontal')
        separator.grid(pady=10, sticky='we')
        if self.settings_client.settings['show_piano_on_start']:       
            self.piano_frame.grid(**self.piano_frame_grid_params)        
        
        #endregion

        #region settings
        self.settings_frame = tb.Labelframe(self.root_frame, bootstyle="info", text=self.settings_client.strings['settings'])
        self.check_state_show_guitar = tk.IntVar(value=1)
        self.check_show_guitar = tb.Checkbutton(self.settings_frame, text=self.settings_client.strings['show_guitar'],
                                                bootstyle="default-round-toggle",
                                                variable=self.check_state_show_guitar,
                                                command=self.set_guitar_visibility)        

        self.check_state_show_piano = tk.IntVar(value=self.settings_client.settings['show_piano_on_start'])
        self.check_show_piano = tb.Checkbutton(self.settings_frame, text=self.settings_client.strings['show_piano'], 
                                            bootstyle="default-round-toggle",
                                            variable=self.check_state_show_piano,
                                            command=self.set_piano_visibility)
        self.check_show_guitar.grid(padx=20, pady=10, row=0)
        self.check_show_piano.grid(padx=20, pady=10, row= 1)

        #region fret range
        self.fret_range_frame = tb.Labelframe(self.settings_frame, bootstyle="default", text=self.settings_client.strings['fret_range'])
        self.label_from = tb.Label(self.fret_range_frame, text=self.settings_client.strings['from'])
        self.input_fret_from = tb.Combobox(self.fret_range_frame, width=5, state='readonly',
                                                values=list(range(0,self.settings_client.constants['frets_number']+1)))
        self.input_fret_from.current(0)
        self.label_to = tb.Label(self.fret_range_frame, text=self.settings_client.strings['to'])
        self.input_fret_to = tb.Combobox(self.fret_range_frame, width=5, state='readonly',
                                                values=list(range(0,self.settings_client.constants['frets_number']+1)))
        self.input_fret_to.current(self.settings_client.constants['frets_number'])
        self.label_from.grid(column=0, row=0, padx=10)
        self.input_fret_from.grid(column=1, row=0, pady= 10, padx=5)
        self.label_to.grid(column=2, row=0, padx=5)
        self.input_fret_to.grid(column=3, row=0, padx=5)
        self.fret_range_frame.grid(row=2, padx=30, pady=10)
        #endregion

        #region root scale
        self.scale_root_frame = tb.Labelframe(self.settings_frame, text=self.settings_client.strings['scale_root'], bootstyle="default")
        self.input_scale_root = tb.Combobox(self.scale_root_frame, width=7, state='readonly',
                                            values=self.settings_client.constants['all_notes'])
        self.input_scale_root.current(0)
        self.input_scale_root.grid(pady=10, padx=20)
        self.scale_root_frame.grid(row=2, column=2, padx=10, pady=20)
        #endregion 

        #region scale type
        self.scale_type_frame = tb.Labelframe(self.settings_frame, text=self.settings_client.strings['type'], bootstyle="default")
        self.input_scale_type = tb.Combobox(self.scale_type_frame, width=15, state='readonly',
                                            values=[self.settings_client.strings[s] for s in self.settings_client.constants['scale_types']])
        self.input_scale_type.current(0)
        self.input_scale_type.grid(pady=10, padx=30)
        self.scale_type_frame.grid(row=2, column=3, padx=20, pady=20)
        #endregion

        # ok button
        self.btn_update = tb.Button(self.settings_frame, text=self.settings_client.strings['update'], command=self.show_guitar_fretboard,
                                    bootstyle="default", takefocus=False)
        self.btn_update.grid(row=2, column=4, padx=10, ipady=10)

        btn = tb.Button(self.settings_frame, text=self.settings_client.strings['start_visuals'], command=self.play,
                        takefocus=False)
        btn.grid(row=2, column=5, padx=10, ipady=10)

        self.settings_frame.grid(row=row, sticky='news', padx=20, pady=10)
        row += 1
        self.show_guitar_fretboard()

        self.root.mainloop()

    @exception_catcher
    def update_app(self):
        self.menubar.entryconfigure(0, label=self.settings_client.strings['settings'])
        self.menubar.entryconfigure(1, label=self.settings_client.strings['tools'])
        self.settings_menu.entryconfigure(0, label=self.settings_client.strings['settings'])
        self.settings_menu.entryconfigure(1, label=self.settings_client.strings['revert_to_default'])
        self.tools_menu.entryconfig(0, label=self.settings_client.strings['signal_config'])
        self.check_show_guitar.configure(text=self.settings_client.strings['show_guitar'])    
        self.check_show_piano.configure(text=self.settings_client.strings['show_piano'])
        self.fret_range_frame.configure(text=self.settings_client.strings['fret_range'])
        self.label_from.configure(text=self.settings_client.strings['from'])
        self.label_to.configure(text=self.settings_client.strings['to'])
        self.scale_root_frame.configure(text=self.settings_client.strings['scale_root'])
        self.scale_type_frame.configure(text=self.settings_client.strings['type'])
        if self.input_scale_type.get() not in self.settings_client.strings.values():
            # language did change
            self.input_scale_type.configure(values=[self.settings_client.strings[s] for s in self.settings_client.constants['scale_types']])
            self.input_scale_type.current(0)        
        self.btn_update.configure(text=self.settings_client.strings['update'])
        self.show_guitar_fretboard()

    @exception_catcher
    def show_guitar_fretboard(self):
        self.guitar.show_fretboard(self.input_scale_root.get(), self.input_scale_type.get(),
                            self.input_fret_from.get(), self.input_fret_to.get())

    @exception_catcher
    def set_guitar_visibility(self):
        if self.check_state_show_guitar.get():
            self.guitar_frame.grid(**self.guitar_frame_grid_params)  
        else:
            self.guitar_frame.grid_forget()  

    @exception_catcher
    def set_piano_visibility(self):
        if self.check_state_show_piano.get():
            self.piano_frame.grid(**self.piano_frame_grid_params)  
        else:
            self.piano_frame.grid_forget()
    
    @exception_catcher
    def play(self):
        vis = Visualizer(settings_client=self.settings_client,
                        size=self.root.maxsize(),
                        show_guitar=self.check_state_show_guitar.get(),
                        show_piano=self.check_state_show_piano.get(),
                        guitar = self.guitar,
                        piano = self.piano,
                        first_fret = int(self.input_fret_from.get()),
                        last_fret = int(self.input_fret_to.get()),
                        scale_type = next(filter(lambda x: self.settings_client.strings[x]==self.input_scale_type.get(), self.settings_client.strings)),
                        max_bend = self.guitar.STRING_DISTANCE,
                        reduce_bends = self.settings_client.settings['reduce_bends']
                        )

app = App()
