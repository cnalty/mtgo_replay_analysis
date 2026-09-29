import io

class MTGOReplay:
    def __init__(self, replay_path):
        self.replay_path = replay_path
        self.replay_text = ""
        with io.open(self.replay_path, "r", encoding="latin1") as f:
            self.replay_text = f.read()
        print(self.replay_text)

