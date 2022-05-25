import sys

from plubot.core import main



def run():
    # TODO cli
    cmd, *args = sys.argv[1:]
    if cmd == 'run':
        print(args)
        main(*args)
