import sys
from celery import Celery

app = Celery('scrooge')
app.config_from_object('scrooge.celeryconfig')

if __name__ == '__main__':
    # The module must either be installed via the package or
    # the working directory for this script must be the one above this one.
    # Either way, the `scrooge` Python package must be in the $PYTHONPATH.
    # Pass the same set of argument you would do to the `celery` command.
    # For example:
    #   -A scrooge.celeryapp worker -l DEBUG -B
    app.start(sys.argv[1:])
