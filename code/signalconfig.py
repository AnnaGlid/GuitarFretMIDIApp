import mido
import tkinter as tk
import ttkbootstrap as tb
from datetime import datetime, timedelta

from commons import exception_catcher

class SignalConfig:
    LOG_NBR_LIMIT = 20
    TIMEOUT = 3

    def __init__(self, settings_client):
        self.settings_client = settings_client
        self.logs = ''
        self.log_nbr = 0
        self.running = True        
    
    @exception_catcher
    def start(self):
        padx = 25
        pady= 25
        row = 0
        self.window = tk.Toplevel()
        self.window.resizable(False,False)
        self.window.title(self.settings_client.strings['signal_config'])
        self.window.geometry('1000x600')
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)

        self.textbox = tb.Text(self.window, width=110)
        self.textbox.grid(padx=padx, pady=pady, row=row)
        self.textbox.config(state=tk.DISABLED)

        row += 1
        btn = tb.Button(self.window, command=self.check_signal, text=self.settings_client.strings['check_signal'],
                        bootstyle="default", takefocus=False)
        btn.grid(row=row)
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        self.window.mainloop()

    @exception_catcher
    def check_signal(self):
        self.running = True
        timeout = datetime.now() + timedelta(seconds=self.TIMEOUT)
        try:
            with mido.open_input() as inport:
                while self.running:
                    if timeout < datetime.now():
                        self.running = False
                        print(f'No signal in {self.TIMEOUT} seconds.')
                        self.add_log(f'No signal in {self.TIMEOUT} seconds.')
                        break
                    try:
                        for signal in inport.iter_pending():
                            self.add_log(str(signal))
                            print(signal)
                            timeout = datetime.now() + timedelta(seconds=self.TIMEOUT)
                            if not self.running:
                                break
                    except Exception as ex:
                        print(f'Exception: {ex}')
                        self.add_log(f'Exception: {ex}')
                        self.running = False
        except OSError:
            self.add_log(self.settings_client.strings['no_signal'])

    @exception_catcher
    def add_log(self, log: str):
        self.textbox.config(state=tk.NORMAL)
        if self.log_nbr >= self.LOG_NBR_LIMIT:
            self.log_nbr = 0
            self.textbox.delete("1.0", tk.END)
        self.log_nbr += 1
        self.textbox.insert(tk.END, log + '\n')
        self.textbox.config(state=tk.DISABLED)
        self.window.update()
        print(f'log added: {log}')

    def close_window(self):
        self.running = False  # turn off while loop
        self.window.destroy()
        print( "Window closed")


        