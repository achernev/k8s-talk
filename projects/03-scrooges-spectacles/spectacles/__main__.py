from waitress import serve
from paste.translogger import TransLogger
from spectacles import create_app

if __name__ == '__main__':
    serve(TransLogger(create_app(), setup_console_handler=False))
