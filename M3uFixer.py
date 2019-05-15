import re


class M3uFixer:

    def __init__(self, channelDictionary):
        self.all_lines = []
        self.vod_lines = []
        self.channelDictionary = channelDictionary

    def readAllLines(self):
        self.lines = [line.rstrip('\n') for line in open("test.m3u", encoding='utf8')]
        return len(self.lines)

    def fixLines(self):
        self.readAllLines()
        numLine = len(self.lines)
        for n in range(numLine):
            line = self.lines[n]
            if line[0] == "#":
                self.manageLine(n)
        playlist = open("playlist.m3u", "w", encoding='utf8')
        playlist.write("#EXTM3U\n")
        playlist.writelines(self.all_lines)
        playlist.close()

        vod = open("playlist_vod.m3u", 'w', encoding='utf8')
        vod.write("#EXTM3U\n")
        vod.writelines(self.vod_lines)
        vod.close()

    def getPossibleKeyMatches(self, key, matcher):
        testkey = key[0:3].casefold()
        # print(testkey)
        if testkey in matcher.replace(' ', '').casefold():
            return True
        else:
            return False

    def manageLine(self, n):
        keys = self.channelDictionary.keys()
        lineInfo = self.lines[n]
        lineLink = self.lines[n+1]
        if lineInfo != "#EXTM3U":
            m = re.search("group-title=\"(.*?)\"", lineInfo)
            group = m.group(1)
            if not(group.startswith("Canais:")):
                self.vod_lines.append(lineInfo + '\n')
                self.vod_lines.append(lineLink + '\n')
            else:
                m = re.search("tvg-name=\"(.*?)\"", lineInfo)
                name = m.group(1)
                possibleKeyMatches = filter(lambda k: self.getPossibleKeyMatches(k, name), keys)
                for key in possibleKeyMatches:
                    if name in self.channelDictionary.get(key):
                        newline = re.sub("tvg-id=\"(.*?)\"", 'tvg-id="' + key + '"', lineInfo)
                        self.all_lines.append(newline + '\n')
                        self.all_lines.append(lineLink + '\n')
