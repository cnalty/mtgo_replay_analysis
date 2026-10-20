from argparse import ArgumentParser
from .ReplayDB import ReplayDB
from .display import DisplayDriver
from PySide6.QtWidgets import QApplication
import sys

def main(args):
    db = ReplayDB(args.db, args.replay_folder, args.username)
    db.add_all()
    app = QApplication()
    window = DisplayDriver(db)
    window.show()
    sys.exit(app.exec())


def parse_arguments():
    parser = ArgumentParser(prog='MTGO Replay Analysis')
    parser.add_argument('--db', help='Database location', default="./replay.db")
    parser.add_argument('--replay_folder', help='Absolute Path to MTGO replay folder, '
                                                'will be remembered after first run', default=None)
    parser.add_argument('--username', help='Your MTGO Username, '
                                           'will be remembered after first run', default=None)

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    print(args.db)
    main(args)