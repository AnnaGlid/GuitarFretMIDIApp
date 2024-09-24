from datetime import datetime
from traceback import format_exc
from ttkbootstrap.dialogs import Messagebox

def exception_catcher(fun):
    def decorator(*args, **kwargs):
        try:
            val = fun(*args, **kwargs)
            return val
        except Exception as ex:
            msg = f'Error in function {fun.__qualname__}.\n\nException: {ex}\n\n{format_exc()}'
            Messagebox.show_error(msg, 'Error')
            print(msg)
            with open('data/logs.txt','a+') as f:
                f.write(f'***********\n{datetime.now()}:\t\t{msg}')
    return decorator