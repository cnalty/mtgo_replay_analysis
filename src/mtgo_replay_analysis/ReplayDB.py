import sqlite3
import warnings
import json
import os
from mtgo_replay_analysis.MTGOReplay import MTGOReplay


class ReplayDB:
    def __init__(self, db_path: str, replay_folder: str | None, username: str | None):
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
                            g3_op_cards TEXT
                            )
                            """)
        self.replay_folder = self.get_replay_folder(replay_folder)
        self.username = self.get_username(username)

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
        for i in range(len(match.mull[0])):
            game_mull[i] = match.mull[player_idx][i]

        player_cards = [''] * 3
        for i in range(len(match.cards[player_idx])):
            player_cards[i] = json.dumps(list(match.cards[player_idx][i]))

        op_cards = [''] * 3
        for i in range(len(match.cards[op_idx])):
            op_cards[i] = json.dumps(list(match.cards[op_idx][i]))


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
            op_cards[2]
        )
        self.cur.execute("""INSERT INTO match_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            on CONFLICT do NOTHING """, match_vals)
        self.conn.commit()
        return True

    def add_all(self) -> None:
        for entry in os.scandir(self.replay_folder):
            if entry.name.startswith("Match_GameLog"):
                curr_match = MTGOReplay(entry.path)
                self.add(curr_match)