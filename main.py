from json import load
import tkinter as tk
import ttkbootstrap as tb
import ttkbootstrap.constants as tb_const
from ttkbootstrap.scrolled import ScrolledFrame
from tkinter import ttk


from instruments import Guitar, Piano
from settings import Settings

with open('config/constants.json') as f:
    constants = load(f)

class App:
    def __init__(self):
        row = 0
        self.font = ('Constantia', 14)
        self.root = tb.Window(themename="cosmo")
        self.root.title("See MIDI")
        self.root.geometry('{}x{}'.format(*self.root.maxsize()))
        self.root.state('zoomed')
        self.settings_client = Settings(self.root)
        menubar = tk.Menu(self.root)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label=self.settings_client.strings['settings'], command=self.settings_client.open)
        menubar.add_cascade(label=self.settings_client.strings['settings'], menu=settings_menu)

        self.root.config(menu=menubar)
        self.root_frame = ScrolledFrame(self.root, autohide=True)
        self.root_frame.pack(fill=tb_const.BOTH, expand=tb_const.YES, padx=10, pady=10)        

        #region guitar
        self.guitar_frame = tb.Frame(self.root_frame, bootstyle="default")
        self.guitar = Guitar(self.guitar_frame, self.root.maxsize()[0])
        self.guitar_frame_grid_params = {
            "row": row,
            "padx": 20,
            "pady": 30,
            "sticky": "se"
        }
        self.guitar.canvas.grid()        
        separator = tb.Separator(self.guitar_frame, bootstyle="default", orient='horizontal')
        separator.grid(pady=30, sticky='we')        
        self.guitar_frame.grid(**self.guitar_frame_grid_params)
        row += 1
        #endregion

        #region piano
        self.piano_frame = tb.Frame(self.root_frame, bootstyle="default")
        self.piano = Piano(self.piano_frame, self.root.maxsize()[0])
        self.piano_frame_grid_params = {
            "row": row,
            "padx": 20,
            "pady": 30,
            "sticky": "se"
        }
        row += 1
        self.piano.canvas.grid(sticky='nesw')        
        separator = tb.Separator(self.piano_frame, bootstyle="default", orient='horizontal')
        separator.grid(pady=30, sticky='we')
        if self.settings_client.settings['show_piano_on_start']:       
            self.piano_frame.grid(**self.piano_frame_grid_params)        
        
        #endregion

        #region settings
        self.settings_frame = tb.Labelframe(self.root_frame, bootstyle="primary", text=self.settings_client.strings['settings'])
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
        self.fret_range_frame = tb.Labelframe(self.settings_frame, bootstyle="secondary", text=self.settings_client.strings['fret_range'])
        label_from = tb.Label(self.fret_range_frame, text=self.settings_client.strings['from'])
        self.input_fret_from = tb.Combobox(self.fret_range_frame, width=5, state='readonly',
                                                values=list(range(1,constants['frets_number']+1)))
        self.input_fret_from.current(0)
        label_to = tb.Label(self.fret_range_frame, text=self.settings_client.strings['to'])
        self.input_fret_to = tb.Combobox(self.fret_range_frame, width=5, state='readonly',
                                                values=list(range(1,constants['frets_number']+1)))
        self.input_fret_to.current(constants['frets_number']-1)
        label_from.grid(column=0, row=0, padx=10)
        self.input_fret_from.grid(column=1, row=0, pady= 10, padx=5)
        label_to.grid(column=2, row=0, padx=5)
        self.input_fret_to.grid(column=3, row=0, padx=5)
        self.fret_range_frame.grid(row=2, padx=30, pady=10)
        #endregion

        #region root scale
        self.scale_root_frame = tb.Labelframe(self.settings_frame, text=self.settings_client.strings['scale_root'], bootstyle="secondary")
        self.input_scale_root = tb.Combobox(self.scale_root_frame, width=7, state='readonly',
                                             values=constants['all_notes'])
        self.input_scale_root.current(0)
        self.input_scale_root.grid(pady=10, padx=20)
        self.scale_root_frame.grid(row=2, column=2, padx=10, pady=20)
        #endregion 

        #region scale type
        self.scale_type_frame = tb.Labelframe(self.settings_frame, text=self.settings_client.strings['type'], bootstyle="secondary")
        self.input_scale_type = tb.Combobox(self.scale_type_frame, width=15, state='readonly',
                                             values=[self.settings_client.strings[s] for s in constants['scale_types']])
        self.input_scale_type.current(0)
        self.input_scale_type.grid(pady=10, padx=30)
        self.scale_type_frame.grid(row=2, column=3, padx=20, pady=20)
        #endregion

        # ok button
        self.btn_update = tb.Button(self.settings_frame, text=self.settings_client.strings['update'], command=self.show_guitar_fretboard,
                                    bootstyle="primary, outline", takefocus=False)
        self.btn_update.grid(row=2, column=4, padx=10, ipady=10)


        self.settings_frame.grid(row=row, sticky='news', padx=20, pady=10)
        row += 1

        self.show_guitar_fretboard()        
        self.root.mainloop()

    def show_guitar_fretboard(self):
        self.guitar.show_fretboard(self.input_scale_root.get(), self.input_scale_type.get(),
                            self.input_fret_from.get(), self.input_fret_to.get())
        
    def set_guitar_visibility(self):
        if self.check_state_show_guitar.get():
            self.guitar_frame.grid(**self.guitar_frame_grid_params)  
        else:
            self.guitar_frame.grid_forget()  


    def set_piano_visibility(self):
        if self.check_state_show_piano.get():
            self.piano_frame.grid(**self.piano_frame_grid_params)  
        else:
            self.piano_frame.grid_forget()  

app = App()
