import mido
import tkinter as tk
import ttkbootstrap as tb

from commons import exception_catcher

class SignalConfig:
    LOG_NBR_LIMIT = 50

    def __init__(self, settings_client):
        self.settings_client = settings_client
        self.logs = ''
        self.log_nbr = 0
    
    @exception_catcher
    def start(self):
        padx = 25
        pady= 25
        row = 0
        self.window = tk.Toplevel()
        self.window.title(self.settings_client.strings['signal_config'])
        self.window.geometry('1000x600')
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)

        self.textbox = tb.Text(self.window, width=110)
        self.textbox.grid(padx=padx, pady=pady, row=row)

        row += 1
        btn = tb.Button(self.window, command=self.check_signal, text=self.settings_client.strings['check_signal'],
                        bootstyle="default", takefocus=False)
        btn.grid(row=row)

    @exception_catcher
    def check_signal(self):
        try:
            inport = mido.open_input()
            for signal in inport.iter_pending():
                self.add_log(signal)
        except OSError:
            self.add_log(self.settings_client.strings['no_signal'])

    @exception_catcher
    def add_log(self, log: str):
        if self.log_nbr >= self.LOG_NBR_LIMIT:
            self.log_nbr = 0
            self.textbox.delete("1.0", tk.END)
        self.log_nbr += 1
        self.textbox.insert(tk.END, log + '\n')

        