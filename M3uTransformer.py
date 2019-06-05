from typing import List

from m3uCollectors import *


class M3uTransformer:
    def __init__(self, iptv_filename):
        self.m3u_list = []
        self.iptv_filename = iptv_filename

    def readAllLines(self):
        self.lines = [line.rstrip('\n') for line in open(self.iptv_filename, encoding='utf8')]
        return len(self.lines)

    def transform(self) -> List[M3uEntity]:
        for n in range(self.readAllLines()):
            line = self.lines[n]
            if line[0] == "#":
                entity = self.map_to_m3u(n)
                if entity:
                    self.m3u_list.append(entity)
        return self.m3u_list

    def map_to_m3u(self, n):
        if self.lines[n] != "#EXTM3U":
            return M3uEntity(self.lines[n], self.lines[n + 1])
