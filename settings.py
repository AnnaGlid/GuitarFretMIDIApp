from json import load, dump
import tkinter as tk
import ttkbootstrap as tb
import ttkbootstrap.constants as tb_const
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog
from ttkbootstrap.dialogs import Messagebox

with open('config/constants.json') as f:
    constants = load(f)

class Settings:
    def __init__(self, app):
        self.app = app
        self.SETTINGS_PATH = 'config/settings.json'
        with open(self.SETTINGS_PATH) as f:
            self.settings = load(f)        
        with open('config/strings.json') as f:
            self.all_strings = load(f)
        self.strings = self.all_strings[self.settings['language']]

    def set_color_interval(self, parameter: str):
        interval, what = parameter.split('//')
        dialog = ColorChooserDialog(parent=self.window)
        dialog.show()
        chosen_color = dialog.result
        if not chosen_color:
            return
        self.interval_widgets_dict[interval][what]['btn'].configure(bg=chosen_color.hex)        
        self.interval_widgets_dict[interval][what]['new_color'] = chosen_color.hex

    def set_color_guitar(self, element: str):
        dialog = ColorChooserDialog(parent=self.window)
        dialog.show()
        chosen_color = dialog.result
        if not chosen_color:
            return
        self.guitar_colors[element]['btn'].configure(bg=chosen_color.hex)        
        self.guitar_colors[element]['new_color'] = chosen_color.hex        

    def save_settings(self):
        anything_changed = False
        if self.settings['interval_label_radius'] != self.radius_size.get():
            anything_changed = True
            self.settings['interval_label_radius'] = self.radius_size.get()
        if self.settings['interval_font_size'] != self.interval_font_size.get():
            anything_changed = True
            self.settings['interval_font_size'] = self.interval_font_size.get()
        if self.settings['show_piano_on_start'] != self.check_state_show_piano.get():
            anything_changed = True
            self.settings['show_piano_on_start'] = self.check_state_show_piano.get()

        for interval in self.settings['interval_color']:
            if new_color := self.interval_widgets_dict[interval]['bg'].get('new_color'):
                anything_changed = True
                self.settings['interval_color'][interval]['bg'] = new_color
            if new_color := self.interval_widgets_dict[interval]['font'].get('new_color'):
                anything_changed = True
                self.settings['interval_color'][interval]['font'] = new_color
        for element in self.guitar_colors:
            if new_color := self.guitar_colors[element].get('new_color'):
                anything_changed = True
                self.settings[element] = new_color
        if self.check_state_theme.get() != self.settings['dark_theme']:
            anything_changed = True
            self.settings['dark_theme'] = self.check_state_theme.get()
        lang_code = next(filter(lambda x: self.strings[x] == self.lang_combobox.get(), self.strings))
        if self.settings['language'] != lang_code:            
            anything_changed = True
            self.settings['language'] = lang_code
            self.strings = self.all_strings[lang_code]                            
        if anything_changed:
            with open(self.SETTINGS_PATH, 'w') as f:
                dump(self.settings, f)
            self.app.update_app()
        self.close_window()
        
    def close_window(self):
        self.window.destroy()

    def revert_to_default(self):
        mb = Messagebox.yesno(self.strings['ask_revert_to_default'], self.strings['revert_to_default'])
        if mb == 'Yes':
            with open('config/default_settings.json') as f:
                self.settings = load(f)        
            with open('config/default_strings.json') as f:
                self.all_strings = load(f)
            self.strings = self.all_strings[self.settings['language']]            
            with open(self.SETTINGS_PATH, 'w') as f:
                dump(self.settings, f)            
            self.app.update_app()

    def open(self):
        padx = 10
        pady= 5
        window_row = 0
        self.window = tk.Toplevel()
        self.window.title(self.strings['settings'])
        self.window.geometry('800x800')

        scroll_frame = ScrolledFrame(self.window, autohide=True)
        scroll_frame.pack(fill=tb_const.BOTH, expand=tb_const.YES, padx=10, pady=10)

        theme_frame = tb.LabelFrame(scroll_frame, text=self.strings['choose_theme'])
        self.check_state_theme = tk.IntVar(value=int(self.settings['dark_theme']))
        theme_checkbtn = tb.Checkbutton(theme_frame, bootstyle="round-toggle", 
                                variable=self.check_state_theme, text=self.strings['dark_theme'])
        theme_checkbtn.grid(padx=padx*2, pady=pady*2)
        theme_frame.grid(row=window_row, padx=padx,pady=pady)
        window_row +=1 

        lang_frame = tb.Labelframe(scroll_frame, text=self.strings["choose_language"])
        self.lang_combobox = tb.Combobox(lang_frame, width=20, state='readonly',
                        values=[self.strings[lang] for lang in constants['available_languages']])
        self.lang_combobox.set(self.strings[self.settings['language']])
        self.lang_combobox.grid(padx=padx, pady=pady)
        lang_frame.grid(padx=padx, pady=pady, row=window_row)
        window_row += 1

        self.radius_size = tk.IntVar(value=self.settings['interval_label_radius'])        
        radius_frame = tb.Labelframe(scroll_frame, text=self.strings['interval_label_radius'])
        radius_input = tb.Spinbox(radius_frame, from_=3, to=25, textvariable=self.radius_size, state='readonly')        
        radius_input.grid(padx=padx, pady=pady)        
        radius_frame.grid(padx=padx, pady=pady, row=window_row)        
        window_row += 1

        interval_font_size_frame = tb.Labelframe(scroll_frame, text=self.strings['interval_font_size'])
        self.interval_font_size = tk.IntVar(value=self.settings['interval_font_size'])
        interval_dont_size_input = tb.Spinbox(interval_font_size_frame, from_=1, to=30, 
                                              textvariable=self.interval_font_size, state='readonly')
        interval_dont_size_input.grid(padx=padx, pady=pady)
        interval_font_size_frame.grid(padx=padx, pady=pady, row=window_row)
        window_row += 1

        show_on_start_frame = tb.Labelframe(scroll_frame, text=self.strings['on_start'])
        self.check_state_show_piano = tk.IntVar(value=self.settings['show_piano_on_start'])
        show_piano_checkbtn = tb.Checkbutton(show_on_start_frame, bootstyle="round-toggle", 
                                variable=self.check_state_show_piano, text=self.strings['show_piano_on_start'])
        show_piano_checkbtn.grid(padx=padx*2, pady=pady*2)
        show_on_start_frame.grid(padx=padx, pady=pady, row=window_row)
        window_row += 1

        #region intervals
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
                    command=lambda x=f'{interval}//bg': self.set_color_interval(x), width=4)
            self.interval_widgets_dict[interval]['bg']['btn'].configure(bg=colors['bg'])

            self.interval_widgets_dict[interval]['font']['btn'] = tk.Button(
                    self.interval_widgets_dict[interval]['frame2'],
                    command=lambda x=f'{interval}//font': self.set_color_interval(x), width=4)
            self.interval_widgets_dict[interval]['font']['btn'].configure(bg=colors['font'])

            self.interval_widgets_dict[interval]['bg']['btn'].grid(padx=2, pady=2)
            self.interval_widgets_dict[interval]['font']['btn'].grid(padx=2, pady=2)
            self.interval_widgets_dict[interval]['frame1'].grid(row=row, column=1)
            self.interval_widgets_dict[interval]['frame2'].grid(row=row, column=2)
            row += 1
        intervals_frame.grid(padx=padx, pady=pady, row=window_row)
        #endregion
        
        guitar_color_frame = tb.Labelframe(scroll_frame, text=self.strings['guitar_colors'])
        self.guitar_colors = {}
        row = 0
        for element in ["guitar_neck_color", "guitar_dots_color", "guitar_frets_color", "guitar_strings_color"]:
            self.guitar_colors[element] = {}
            tb.Label(guitar_color_frame, text=self.strings[element]).grid(padx=padx, pady=pady, row=row, column=0)
            self.guitar_colors[element]['frame'] = tb.Frame(guitar_color_frame, bootstyle='dark')
            self.guitar_colors[element]['btn'] = tk.Button(
                    self.guitar_colors[element]['frame'],
                    command=lambda x=element: self.set_color_guitar(x), width=4)
            self.guitar_colors[element]['btn'].configure(bg=self.settings[element])

            self.guitar_colors[element]['btn'].grid(padx=2, pady=2)
            self.guitar_colors[element]['frame'].grid(row=row, column=1)
            row += 1
        guitar_color_frame.grid(row=window_row, column=1, padx=padx, pady=pady)

        window_row += 1
        close_btns_frame = tb.Labelframe(scroll_frame)
        save_btn = tb.Button(close_btns_frame, text=self.strings['save'], 
                             bootstyle='primary', takefocus=False, command=self.save_settings)
        cancel_btn = tb.Button(close_btns_frame, text=self.strings['cancel'], 
                               bootstyle='secondary', takefocus=False, command=self.close_window)
        save_btn.grid(column=0, row=0, padx=padx, pady=pady)
        cancel_btn.grid(column=1, row=0, padx=padx, pady=pady)
        close_btns_frame.grid(sticky='e', padx=padx, pady=pady, row=window_row, column=1)

        self.window.mainloop()


        
