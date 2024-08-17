from json import load
import tkinter as tk
import ttkbootstrap as tb
from tkinter import ttk
from instruments import Guitar, Piano

with open('config/settings.json') as f:
    settings = load(f)
with open('config/strings.json') as f:
    strings = load(f)[settings['language']]
with open('config/constants.json') as f:
    constants = load(f)


class App:

    def __init__(self):
        #region create widgets
        self.root = tb.Window(themename="cosmo")
        self.root.title("See MIDI")
        self.root.geometry('{}x{}'.format(*self.root.maxsize()))
        self.root_frame = tk.Frame(self.root, pady=30, padx=40)
        columns_number = 4
        self.root.columnconfigure(index=0, weight=1)
        # [self.root_frame.columnconfigure(index=idx, weight=1) for idx in range(0, columns_number)]
     
        self.check_state_show_guitar = tk.IntVar(value=1)
        self.check_show_guitar = tk.Checkbutton(self.root_frame, text=strings['show_guitar'], 
                                                variable=self.check_state_show_guitar,
                                                command=self.set_guitar_visibility)
        self.check_show_guitar
        self.check_state_show_piano = tk.IntVar(value=0)
        self.check_show_piano = tk.Checkbutton(self.root_frame, text=strings['show_piano'], 
                                               variable=self.check_state_show_piano,
                                               command=self.set_piano_visibility)
        label_fret_range = tk.Label(self.root_frame, text=strings['fret_range'])
        label_from = tk.Label(self.root_frame, text=strings['from'])
        self.input_fret_from = ttk.Combobox(self.root_frame, width=5, state='readonly',
                                                values=list(range(1,constants['frets_number']+1)))
        self.input_fret_from.current(0)
        label_to = tk.Label(self.root_frame, text=strings['to'])
        self.input_fret_to = ttk.Combobox(self.root_frame, width=5, state='readonly',
                                                values=list(range(1,constants['frets_number']+1)))
        self.input_fret_to.current(constants['frets_number']-1)
        label_scale = tk.Label(self.root_frame, text=strings['scale'])
        label_scale_root = tk.Label(self.root_frame, text=strings['scale_root'])
        self.input_scale_root = ttk.Combobox(self.root_frame, width=5, state='readonly',
                                             values=constants['all_notes'])
        self.input_scale_root.current(0)
        label_scale_type = tk.Label(self.root_frame, text=strings['type'])
        self.input_scale_type = ttk.Combobox(self.root_frame, width=15, state='readonly',
                                             values=[strings[s] for s in constants['scale_types']])
        self.input_scale_type.current(0)
        self.btn_record = tk.Button(self.root_frame, text=strings['start_recording'])
        self.btn_pause = tk.Button(self.root_frame, text=strings['pause_recording'])
        self.btn_stop = tk.Button(self.root_frame, text=strings['stop_recording'])
        self.btn_update = ttk.Button(self.root_frame, text=strings['update'], command=self.show_guitar_fretboard)

        self.guitar = Guitar(self.root_frame, self.root.maxsize()[0])
        self.piano = Piano(self.root_frame, self.root.winfo_width())           
        #endregion

        #region pack widgets
        self.root_frame.grid(sticky='nsew', row=0, column=0)
        row = 0
        self.check_show_guitar.grid(row=row, column=0)
        row += 1
        self.guitar_grid_params = {
            "row":row, "columnspan":4, "sticky":'ns'
        }        
        self.guitar.canvas.grid(**self.guitar_grid_params)        
        row += 1             
        self.check_show_piano.grid(row=row, column=0)
        row += 1
        self.piano_grid_params = {
            "row": row, "column": 0, "columnspan": 4
        }
        if self.check_state_show_piano.get():
            self.piano.canvas.grid(**self.piano_grid_params)
        row += 1 
        # self.btn_record.grid(row=row, column=1, padx=5)
        # self.btn_pause.grid(row=row, column=2, padx=5)
        # self.btn_stop.grid(row=row, column=3, padx=5)
        # row += 1
        sep = tk.Label(self.root_frame, text="", pady=10)
        sep.grid(row=row, column=0)
        row += 1
        label_fret_range.grid(row=row, column=0)
        row += 1
        label_from.grid(row=row, column=0)
        self.input_fret_from.grid(row=row, column=1)
        label_to.grid(row=row, column=2)
        self.input_fret_to.grid(row=row, column=3)
        row += 1
        label_scale.grid(row=row, column=0)
        row += 1
        label_scale_root.grid(row=row, column=0)
        self.input_scale_root.grid(row=row, column=1)
        label_scale_type.grid(row=row, column=2)
        self.input_scale_type.grid(row=row, column=3)
        row += 1
        self.btn_update.grid(row=row, column=0, pady=5)
        #endregion

        self.show_guitar_fretboard()        
        self.root.mainloop()

    def show_guitar_fretboard(self):
        self.guitar.show_fretboard(self.input_scale_root.get(), self.input_scale_type.get(),
                            self.input_fret_from.get(), self.input_fret_to.get())
        
    def set_guitar_visibility(self):
        if self.check_state_show_guitar.get():
            self.guitar.canvas.grid(**self.guitar_grid_params)  
        else:
            self.guitar.canvas.grid_forget()  


    def set_piano_visibility(self):
        if self.check_state_show_piano.get():
            self.piano.canvas.grid(**self.piano_grid_params)  
        else:
            self.piano.canvas.grid_forget()  

app = App()
