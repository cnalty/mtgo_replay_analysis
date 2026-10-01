import io
import re
import warnings
import os
from pathlib import Path
import time

class MTGOReplay:
    log_splitter = re.compile(r'[^A-Za-z0-9 @:,\-_\+\/\[\]\'\(\)\{\}\.{1,3}].*?(?:@P)+')
    parse_player = re.compile(r'[A-Za-z0-9\-_]+')
    card_played_match = re.compile(r'(\w+)\s(?:plays|casts)\s@\[([\w\s,\']+)@')
    game_end = re.compile(r'(\w+)\swins\sthe\sgame')
    mull_match = re.compile(r'(\w+).*begins\sthe\sgame\swith\s([a-z]+)\scards')
    otp_match = re.compile(r'(\w+)\schooses\sto\splay\sfirst')
    end_match = re.compile(r'(\w+)\swins\sthe\smatch\s([0-9])-([0-9])')
    hand_size = {"zero" : 0,
                 "one" : 1,
                 "two" : 2,
                 "three" : 3,
                 "four" : 4,
                 "five" : 5,
                 "six" : 6,
                 "seven" : 7}


    def __init__(self, replay_path):
        self.replay_path = replay_path
        self.replay_text = ""
        with io.open(self.replay_path, "r", encoding="latin1") as f:
            self.replay_text = f.read()
        self.match_date = time.ctime(os.path.getmtime(self.replay_path))
        self.match_id = Path(self.replay_path).stem.replace("Match_GameLog_", "")
        self.parse_replay()

    def parse_replay(self):
        # Get basic game info
        self.action_list = re.split(self.log_splitter, self.replay_text)
        self.players = [re.match(self.parse_player, self.action_list[1])[0], re.match(self.parse_player, self.action_list[2])[0]]
        self.game_score = [0, 0]

        # Split games and parse cards
        self.game_ends = []
        self.game_winners = []
        self.otp = []
        self.mull = [[], []]
        self.cards = [[set()], [set()]]
        for i in range(len(self.action_list)):
            check_game_end = re.match(self.game_end, self.action_list[i])
            if check_game_end is not None:
                self.game_ends.append(i)
                self.game_winners.append(check_game_end.group(1))
                if check_game_end.group(1) == self.players[0]:
                    self.game_score[0] += 1
                else:
                    self.game_score[1] += 1

                self.cards[0].append(set())
                self.cards[1].append(set())

            card = re.match(self.card_played_match, self.action_list[i])
            if card is not None:
                if card.group(1) == self.players[0]:
                    self.cards[0][-1].add(card.group(2))
                elif card.group(1) == self.players[1]:
                    self.cards[1][-1].add(card.group(2))
                else:
                    warnings.warn(f"Detected played card, but could not match player for: {self.action_list[i]}")
            is_otp = re.match(self.otp_match, self.action_list[i])
            if is_otp is not None:
                self.otp.append(is_otp.group(1))
            mull_size = re.match(self.mull_match, self.action_list[i])
            if mull_size is not None:
                if mull_size.group(1) == self.players[0]:
                    self.mull[0].append(self.hand_size[mull_size.group(2)])
                elif mull_size.group(1) == self.players[1]:
                    self.mull[1].append(self.hand_size[mull_size.group(2)])
            is_match_win = re.match(self.end_match, self.action_list[i])
            '''if is_match_win is not None:
                self.winner = is_match_win.group(1)
                self.game_score = is_match_win.group(2), is_match_win.group(3)
                self.cards[0].pop(-1)
                self.cards[1].pop(-1)'''

        self.winner = self.players[0] if self.game_score[0] > self.game_score[1] else self.players[1]
        self.cards[0].pop(-1)
        self.cards[1].pop(-1)


