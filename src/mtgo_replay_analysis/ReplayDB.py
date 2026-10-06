import sqlite3
import warnings
import json
import os
from typing import List, Tuple

from mtgo_replay_analysis.MTGOReplay import MTGOReplay
from tqdm import tqdm
from operator import and_

class ReplayDB:
    formats = ('standard',
               'pioneer',
               'modern',
               'legacy',
               'vintage',
               'pauper',
               'premodern')

    def __init__(self, db_path: str, replay_folder: str | None, username: str | None, update_cards: bool = False):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE if not exists match_data
                            (match_id TEXT PRIMARY KEY,
                            match_date DATE,
                            player TEXT, /* players name (mostly for verification purposes) */
                            opponent TEXT, /* opponents name */
                            g1_win BOOL, /* true if player won */
                            g2_win BOOL,
                            g3_win BOOL,
                            g1_otp BOOL, /* true is player otp */
                            g2_otp BOOL,
                            g3_otp BOOL,
                            g1_mull BIT, /* starting hand size */
                            g2_mull BIT,
                            g3_mull BIT,
                            g1_p_cards TEXT, /* set of cards played each game by each player stored as string */
                            g2_p_cards TEXT,
                            g3_p_cards TEXT,
                            g1_op_cards TEXT,
                            g2_op_cards TEXT,
                            g3_op_cards TEXT,
                            match_win BOOL,
                            format TEXT,
                            player_deck TEXT,
                            opponent_deck TEXT
                            )
                            """)
        self.cur.execute("""CREATE TABLE if not exists card_data
                                    (card_name TEXT PRIMARY KEY,
                                    standard_legal BOOL,
                                    pioneer_legal BOOL,
                                    modern_legal BOOL,
                                    legacy_legal BOOL,
                                    vintage_legal BOOL,
                                    pauper_legal BOOL,
                                    premodern_legal BOOL
                                    )
                                    """)

        if update_cards:
            self.update_cards()

        self.replay_folder = self.get_replay_folder(replay_folder)
        self.username = self.get_username(username)

    def update_cards(self):
        with open("oracle-cards-20261002090157.jsonl", 'r') as f:
            num_lines = sum(1 for line in f)
        with open("oracle-cards-20261002090157.jsonl", 'r') as f:
            for line in tqdm(f, desc="Updating card legality", total=num_lines):
                curr_card = json.loads(line)

                # Check for not real cards
                if "Token" in curr_card['type_line']:
                    continue
                if "Emblem" == curr_card['type_line']:
                    continue
                if curr_card['set_type'] == 'memorabilia':
                    continue
                #if len(curr_card['games']) == 1 and curr_card['games'][0] == 'arena':
                #    continue

                # Check if card is split card, split up names for processing purposes
                if r"//" in curr_card['name']:
                    card_names = curr_card['name'].split(r"//")
                    card_names = [x.strip() for x in card_names]
                else:
                    card_names = [curr_card['name']]

                # Process Card
                legals = []
                for cformat in self.formats:
                    legals.append(curr_card['legalities'][cformat] == 'legal' or curr_card['legalities'][cformat] == 'restricted')
                for card_name in card_names:
                    self.cur.execute("""
                            INSERT INTO card_data VALUES
                                (?, ?, ?, ?, ?, ?, ?, ?)
                                ON CONFLICT (card_name) DO UPDATE SET
                                    standard_legal = excluded.standard_legal,
                                    pioneer_legal = excluded.pioneer_legal,
                                    modern_legal = excluded.modern_legal,
                                    legacy_legal = excluded.legacy_legal,
                                    vintage_legal = excluded.vintage_legal,
                                    pauper_legal = excluded.pauper_legal,
                                    premodern_legal = excluded.premodern_legal
                            """, (card_name, *legals))

        self.conn.commit()

    def get_legal(self, card_name: str) -> list:
        self.cur.execute("""
                            SELECT * from card_data where card_name = ?
                            """, (card_name,))
        row = self.cur.fetchone()
        if row is None:
            warnings.warn("Card ({}) not found, returning illegal in all formats")
            return [False] * len(self.formats)
        return row[1:]


    def get_legal_format(self, card_name: str, format: str) -> bool:
        pass


    # Initialize replay folder
    def get_replay_folder(self, replay_folder: str | None) -> str:
        # Replay folder wasn't specified, verify it is in db and return result
        if replay_folder is None:
            res = self.cur.execute("SELECT info FROM metadata WHERE name = replay_folder")
            if res.fetchone() is None:
                raise LookupError("Replay folder not specified and not saved in DB, rerun with the --replay-folder argument")
            else:
                return res.fetchone()[0]
        # New replay folder, add/update db return specified folder
        else:
            self.cur.execute("""CREATE table if not exists metadata(name text PRIMARY KEY, 
                                                                    info text)""")
            self.cur.execute("""
                                INSERT or REPLACE into metadata (name, info) VALUES (
                                 'replay_folder', ?)
                                """, (replay_folder,))
            self.conn.commit()
            return replay_folder

    # Initialize username
    def get_username(self, username: str | None) -> str:
        # Username wasn't specified, verify it is in db and return result
        if username is None:
            res = self.cur.execute("""SELECT info FROM metadata
                                        WHERE name = username""")
            if res.fetchone() is None:
                raise LookupError(
                    "Username not specified and not saved in DB, rerun with the --username argument")
            else:
                return res.fetchone()[0]
        # Insert username into db and return username
        else:
            self.cur.execute("""INSERT or REPLACE INTO metadata (name, info) VALUES
                                ('username', ?)""", (username,))
            self.conn.commit()
            return username

    # Add a match to the database
    # returns true if succesful, false otherwise
    def add(self, match: MTGOReplay) -> bool:
        p1 = match.players[0]
        p2 = match.players[1]
        player_idx, op_idx = None, None
        # Verify user was in replay, exit if not
        if p1 == self.username:
            player_idx, op_idx = 0, 1
        elif p2 == self.username:
            player_idx, op_idx = 1, 0
        else:
            warnings.warn(f"No player in replay {match.match_id} matches username, not added to DB")
            return False

        # parse info using username
        game_winners = [''] * 3
        for i in range(len(match.game_winners)):
            game_winners[i] = match.game_winners[i] == self.username

        game_otps = [''] * 3
        for i in range(len(match.otp)):
            game_otps[i] = match.otp[i] == self.username

        game_mull = [''] * 3
        for i in range(min(len(match.mull[0]), len(match.mull[1]))):
            game_mull[i] = match.mull[player_idx][i]

        player_cards = [''] * 3
        for i in range(len(match.cards[player_idx])):
            player_cards[i] = json.dumps(list(match.cards[player_idx][i]))

        op_cards = [''] * 3
        for i in range(len(match.cards[op_idx])):
            op_cards[i] = json.dumps(list(match.cards[op_idx][i]))

        decks = self.detect_decks(match)
        match_vals = (
            match.match_id,
            match.match_date,
            match.players[player_idx],
            match.players[op_idx],
            game_winners[0],
            game_winners[1],
            game_winners[2],
            game_otps[0],
            game_otps[1],
            game_otps[2],
            game_mull[0],
            game_mull[1],
            game_mull[2],
            player_cards[0],
            player_cards[1],
            player_cards[2],
            op_cards[0],
            op_cards[1],
            op_cards[2],
            match.winner == self.username,
            self.detect_format(match),
            decks[0],
            decks[1],
        )
        self.cur.execute("""INSERT INTO match_data VALUES 
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            on CONFLICT do NOTHING """, match_vals)
        self.conn.commit()
        return True

    def add_all(self) -> None:
        for entry in os.scandir(self.replay_folder):
            if entry.name.startswith("Match_GameLog"):
                curr_match = MTGOReplay(entry.path)
                self.add(curr_match)

    def detect_format(self, match: MTGOReplay) -> str:
        all_cards = set()
        for games in match.cards[0]:
            all_cards.update(games)
        for games in match.cards[1]:
            all_cards.update(games)
        possible_formats = [True] * len(self.formats)
        for card in all_cards:
            curr_formats = self.get_legal(card)
            possible_formats = list(map(and_, curr_formats, possible_formats))
            if sum(possible_formats) == 0:
                warnings.warn(f"Warning could not detect format for match id: {match.match_id}, ({card})")
                return ""
        for i in range(len(possible_formats)):
            if possible_formats[i]:
                return self.formats[i]


    def detect_decks(self, match: MTGOReplay) -> Tuple[str]:
        return ("foo", "bar")