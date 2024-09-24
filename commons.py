from traceback import format_exc
from ttkbootstrap.dialogs import Messagebox

def exception_catcher(f):
    def decorator(*args, **kwargs):
        try:
            val = f(*args, **kwargs)
            return val
        except Exception as ex:
            Messagebox.show_error(f'Error in function {f.__qualname__}.\n\nException: {ex}\n\n{format_exc()}', 'Error')
    return decorator