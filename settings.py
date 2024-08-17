from json import load, dump
import tkinter as tk
import ttkbootstrap as tb
import ttkbootstrap.constants as tb_const
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog

with open('config/constants.json') as f:
    constants = load(f)

class Settings:
    def __init__(self, root):
        self.root = root
        self.font = ('Constantia', 14)
        self.SETTINGS_PATH = 'config/settings.json'
        with open(self.SETTINGS_PATH) as f:
            self.settings = load(f)        
        with open('config/strings.json') as f:
            self.all_strings = load(f)
        self.strings = self.all_strings[self.settings['language']]

    def set_color(self, parameter: str):
        interval, what = parameter.split('//')
        dialog = ColorChooserDialog(parent=self.window)
        dialog.show()
        chosen_color = dialog.result
        if not chosen_color:
            return
        self.interval_widgets_dict[interval][what]['btn'].configure(bg=chosen_color.hex)        
        self.interval_widgets_dict[interval][what]['new_color'] = chosen_color.hex

    def save_settings(self):
        lang_code = next(filter(lambda x: self.strings[x] == self.lang_combobox.get(), self.strings))
        self.settings['language'] = lang_code
        self.strings = self.all_strings[lang_code]
        self.settings['interval_label_radius'] = self.radius_size.get()
        self.settings['show_piano_on_start'] = self.check_state_show_piano.get()

        for interval in self.settings['interval_color']:
            if new_color := self.interval_widgets_dict[interval]['bg'].get('new_color'):
                self.settings['interval_color'][interval]['bg'] = new_color
            if new_color := self.interval_widgets_dict[interval]['font'].get('new_color'):
                self.settings['interval_color'][interval]['font'] = new_color

        with open(self.SETTINGS_PATH, 'w') as f:
            dump(self.settings, f)
        self.close_window()
        
    def close_window(self):
        self.window.destroy()

    def open(self):
        padx = 10
        pady= 5
        self.window = tk.Toplevel()
        self.window.title(self.strings['settings'])
        self.window.geometry('400x800')

        scroll_frame = ScrolledFrame(self.window, autohide=True)
        scroll_frame.pack(fill=tb_const.BOTH, expand=tb_const.YES, padx=10, pady=10)

        lang_frame = tb.Labelframe(scroll_frame, text=self.strings["choose_language"])
        self.lang_combobox = tb.Combobox(lang_frame, width=20, state='readonly',
                        values=[self.strings[lang] for lang in constants['available_languages']])
        self.lang_combobox.set(self.strings[self.settings['language']])
        self.lang_combobox.grid(padx=padx, pady=pady)
        lang_frame.grid(padx=padx, pady=pady)

        self.radius_size = tk.IntVar(value=self.settings['interval_label_radius'])
        radius_frame = tb.Labelframe(scroll_frame, text=self.strings['interval_label_radius'])
        radius_input = tb.Spinbox(radius_frame, from_=3, to=25, textvariable=self.radius_size, state='readonly')
        radius_input.grid(padx=padx, pady=pady)
        radius_frame.grid(padx=padx, pady=pady)

        show_on_start_frame = tb.Labelframe(scroll_frame, text=self.strings['on_start'])
        self.check_state_show_piano = tk.IntVar(value=self.settings['show_piano_on_start'])
        show_piano_checkbtn = tb.Checkbutton(show_on_start_frame, bootstyle="round-toggle", 
                                variable=self.check_state_show_piano, text=self.strings['show_piano_on_start'])
        show_piano_checkbtn.grid(padx=padx*2, pady=pady*2)
        show_on_start_frame.grid(padx=padx, pady=pady)

        intervals_frame = tb.Labelframe(scroll_frame, text=self.strings['interval_color'])
        tb.Label(intervals_frame, text=self.strings['interval']).grid(row=0, column=0, padx=padx, pady=pady)
        tb.Label(intervals_frame, text=self.strings['interval_bg_color']).grid(row=0, column=1, padx=padx, pady=pady)
        tb.Label(intervals_frame, text=self.strings['interval_font_color']).grid(row=0, column=2, padx=padx, pady=pady)
        row = 1
        self.interval_widgets_dict = {}
        for interval, colors in self.settings['interval_color'].items():
            tb.Label(intervals_frame, 
                     text=constants['all_intervals'][interval].encode('cp1252').decode()
                     ).grid(row=row, column=0, padx=padx, pady=pady)
            self.interval_widgets_dict[interval] = {'bg': {}, 'font':{}}
            self.interval_widgets_dict[interval]['frame1'] = tb.Frame(intervals_frame, bootstyle='dark')
            self.interval_widgets_dict[interval]['frame2'] = tb.Frame(intervals_frame, bootstyle='dark')

            self.interval_widgets_dict[interval]['bg']['btn'] = tk.Button(
                    self.interval_widgets_dict[interval]['frame1'],
                    command=lambda x=f'{interval}//bg': self.set_color(x), width=4)
            self.interval_widgets_dict[interval]['bg']['btn'].configure(bg=colors['bg'])

            self.interval_widgets_dict[interval]['font']['btn'] = tk.Button(
                    self.interval_widgets_dict[interval]['frame2'],
                    command=lambda x=f'{interval}//font': self.set_color(x), width=4)
            self.interval_widgets_dict[interval]['font']['btn'].configure(bg=colors['font'])

            self.interval_widgets_dict[interval]['bg']['btn'].grid(padx=2, pady=2)
            self.interval_widgets_dict[interval]['font']['btn'].grid(padx=2, pady=2)
            self.interval_widgets_dict[interval]['frame1'].grid(row=row, column=1)
            self.interval_widgets_dict[interval]['frame2'].grid(row=row, column=2)
            row += 1
        intervals_frame.grid(padx=padx, pady=pady)

        close_btns_frame = tb.Labelframe(scroll_frame)
        save_btn = tb.Button(close_btns_frame, text=self.strings['save'], 
                             bootstyle='primary', takefocus=False, command=self.save_settings)
        cancel_btn = tb.Button(close_btns_frame, text=self.strings['cancel'], 
                               bootstyle='secondary', takefocus=False, command=self.close_window)
        save_btn.grid(column=0, row=0, padx=padx, pady=pady)
        cancel_btn.grid(column=1, row=0, padx=padx, pady=pady)
        close_btns_frame.grid(sticky='e', padx=padx, pady=pady)

        self.window.mainloop()


        
