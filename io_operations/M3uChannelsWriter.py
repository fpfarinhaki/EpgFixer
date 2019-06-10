from io_operations.M3uWriter import M3uWriter


class M3uChannelsWriter(M3uWriter):
    DEFAULT_M3U_LINE = ('#EXTINF:-1 tvg-id="{tvg_id}" '
                        'tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" '
                        'group-title="{tvg_group}",{tvg_name}\n'
                        '{link}\n')

    def __init__(self, filename):
        super().__init__(filename)

    def generate_line(self, channel):
        self.buffer.append(self.DEFAULT_M3U_LINE.format(**channel, doc_id=channel.doc_id))
