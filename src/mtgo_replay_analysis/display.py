from PySide6.QtWidgets import (QWidget, QTableWidget,
                               QTableWidgetItem, QMainWindow, QVBoxLayout, QLabel)
from mtgo_replay_analysis.ReplayDB import ReplayDB
import sys

class DisplayDriver(QMainWindow):
    def __init__(self, db: ReplayDB) -> None:
        super().__init__()
        self.setWindowTitle("MTGO Replay Analysis")
        #self.app = QApplication()
        self.db = db
        layout = QVBoxLayout()

        # Match Info Widget
        self.table = QTableWidget()
        self.columns = ["Date", "Opponent", "Win/Loss", "Format", "Player Deck", "Opponent Deck"]
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(self.columns)
        rows = self.get_all_rows()
        self.table.setRowCount(len(rows))
        self.insert_all_rows(rows)

        # Win Rate Info
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        win_rate = sum(row[2] for row in rows) / len(rows) * 100
        self.win_rate_widget = QLabel(f"Win Rate: {win_rate:.2f}%")

        layout.addWidget(self.table)
        layout.addWidget(self.win_rate_widget)
        #sys.exit(self.app.exec())

    def get_all_rows(self):
        self.db.cur.execute("SELECT * FROM match_data")
        db_rows = self.db.cur.fetchall()
        display_rows = []
        for row in db_rows:
            display_rows.append([row[1], row[3], row[-4], row[-3], row[-2], row[-1]])

        return display_rows

    def insert_row(self, row: list, row_num) -> None:
        for i in range(len(row)):
            self.table.setItem(row_num, i, QTableWidgetItem(str(row[i])))

    def insert_all_rows(self, rows) -> None:
        for i in range(len(rows)):
            self.insert_row(rows[i], i)