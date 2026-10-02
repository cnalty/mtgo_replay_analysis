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
    #unittest.main()