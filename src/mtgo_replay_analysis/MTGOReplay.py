import io
import re

class MTGOReplay:
    log_splitter = re.compile(r'[^A-Za-z0-9 @:,\-_\+\/\[\]\'\(\)\{\}].*?(?:@P)+')

    def __init__(self, replay_path):
        self.replay_path = replay_path
        self.replay_text = ""
        with io.open(self.replay_path, "r", encoding="latin1") as f:
            self.replay_text = f.read()
        self.parse_replay()

    def parse_replay(self):
        self.action_list = re.split(self.log_splitter, self.replay_text)