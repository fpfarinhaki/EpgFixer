"""Database updater CLI

Usage:
    DbUpdater [options] --db-script script

Options:
-h --help               show this
--db-script <script>    run script

"""
import runpy

from docopt import docopt


def update(filename):
    runpy.run_path(filename)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='M3U List Manager 1.0')
    update(arguments['--db-script'])
