import logging
import threading


class M3uWriter:

    def __init__(self, filename):
        self.buffer = []
        self.filename = filename

    def generate_list(self):
        logging.info("{} - Creating list {} with {} items"
                     .format(threading.current_thread().name, self.filename, len(self.buffer)))
        with open(self.filename, 'w+', encoding='utf8') as file:
            file.write("#EXTM3U\n")
            file.writelines(self.buffer)
        logging.info("{} - Finished creating list {}".format(threading.current_thread().name, self.filename))

    def generate_line(self, **kwargs):
        pass
