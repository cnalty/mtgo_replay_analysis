import unittest
from mtgo_replay_analysis.ReplayDB import ReplayDB

'''class TestCardDB(unittest.TestCase):
    def test_get_legal(self):
        pass

    def test_get_legal_format(self):
        pass
'''
if __name__ == '__main__':
    db = ReplayDB("replay.db", "my_replays", "Rudabega", update_cards=True)
    db.add_all()
    for row in db.cur.execute("SELECT * FROM match_data"):
        print(row)
    db.cur.execute("SELECT COUNT(match_id) FROM match_data ")
                   #"WHERE format = 'legacy' AND match_date LIKE '%2026'")
    matches = db.cur.fetchone()[0]
    db.cur.execute("SELECT COUNT(match_id) FROM match_data WHERE match_win = 1")
                   #"WHERE format = 'legacy' AND match_win = 1 AND match_date LIKE '2026%'")
    wins = db.cur.fetchone()[0]
    print(wins / matches * 100)
    #unittest.main()