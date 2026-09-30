import io
import re
import warnings

class MTGOReplay:
    log_splitter = re.compile(r'[^A-Za-z0-9 @:,\-_\+\/\[\]\'\(\)\{\}\.{1,3}].*?(?:@P)+')
    parse_player = re.compile(r'\w+')
    card_played_match = re.compile(r'(\w+)\s(?:plays|casts)\s@\[([\w\s,\']+)@')
    game_end = re.compile(r'(\w+)\swins\sthe\sgame')

    def __init__(self, replay_path):
        self.replay_path = replay_path
        self.replay_text = ""
        with io.open(self.replay_path, "r", encoding="latin1") as f:
            self.replay_text = f.read()
        self.parse_replay()

    def parse_replay(self):
        # Get basic game info
        self.action_list = re.split(self.log_splitter, self.replay_text)
        self.players = [re.match(self.parse_player, self.action_list[1])[0], re.match(self.parse_player, self.action_list[2])[0]]
        self.winner = re.match(self.parse_player, self.action_list[-1][0])
        self.game_score = (int(self.action_list[-1][-3]), int(self.action_list[-1][-1]))
        if self.winner != self.players[0]:
            self.game_score = (self.game_score[1], self.game_score[0])

        # Split games and parse cards
        self.game_ends = []
        self.game_winners = []
        self.otp = []
        self.mull = []
        self.p1_cards = [set()]
        self.p2_cards = [set()]
        for i in range(len(self.action_list)):
            check_game_end = re.match(self.game_end, self.action_list[i])
            if check_game_end is not None:
                self.game_ends.append(i)
                self.game_winners.append(check_game_end.group(1))
                if len(self.game_ends) < sum(self.game_score):
                    self.p1_cards.append(set())
                    self.p2_cards.append(set())
            card = re.match(self.card_played_match, self.action_list[i])
            if card is not None:
                if card.group(1) == self.players[0]:
                    self.p1_cards[-1].add(card.group(2))
                elif card.group(1) == self.players[1]:
                    self.p2_cards[-1].add(card.group(2))
                else:
                    warnings.warn(f"Detected played card, but could not match player for: {self.action_list[i]}")






