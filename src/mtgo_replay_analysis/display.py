import typing

from PySide6.QtWidgets import (QWidget, QMainWindow, QVBoxLayout, QLabel, QTableView,
                               QHeaderView, QHBoxLayout, QSizePolicy)
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel
from PySide6.QtGui import QIcon, QKeySequence
from mtgo_replay_analysis.ReplayDB import ReplayDB
import sys


class DisplayDriver(QMainWindow):
    def __init__(self, db: ReplayDB) -> None:
        super().__init__()
        self.setWindowTitle("MTGO Replay Analysis")
        #self.app = QApplication()
        self.db = db
        layout = QVBoxLayout()
        # Menu
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu("File")

        # Exit QAction
        file_menu.addAction(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit),
                            "Exit", QKeySequence.StandardKey.Quit, self.close)

        # Match Info Widget
        self.table = MTGODataWidget(db)

        # Win Rate Info
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        win_rate = sum(int(self.table.model.data(self.table.model.createIndex(i, 2))) for i in range(self.table.model.rowCount())) / self.table.model.rowCount() * 100
        self.win_rate_widget = QLabel(f"Win Rate: {win_rate:.2f}%")

        layout.addWidget(self.table)
        layout.addWidget(self.win_rate_widget)
        #sys.exit(self.app.exec())


class MatchTableModel(QAbstractTableModel):
    def __init__(self, db: ReplayDB) -> None:
        super().__init__()
        # Pre Load Data
        self.db = db
        self.row_data = []
        self.labels = ("Date", "Opponent", "Win/Loss", "Format", "Player Deck", "Opponent Deck")

        # Load Data
        self.load_data()

        # Post Load Data
        self.column_count = 6
        self.row_count = len(self.row_data)

    def load_data(self) -> None:
        self.db.cur.execute("SELECT * FROM match_data")
        db_rows = self.db.cur.fetchall()
        for row in db_rows:
            # "Date", "Opponent", "Win/Loss", "Format", "Player Deck", "Opponent Deck", "MatchID"
            self.row_data.append([row[1], row[3], row[-4], row[-3], row[-2], row[-1], row[0]])

    def rowCount(self, parent=QModelIndex()) -> int:
        return self.row_count

    def columnCount(self, parent=QModelIndex()) -> int:
        return self.column_count

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.labels[section]
        else:
            return f"{section}"

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        column = index.column()
        row = index.row()
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self.row_data[row][column])
        elif role == Qt.ItemDataRole.UserRole:
            # Return Match ID, used to know where to edit db
            return str(self.row_data[row][-1])
        return None


class MTGODataWidget(QWidget):
    def __init__(self, db: ReplayDB) -> None:
        super().__init__()
        self.model = MatchTableModel(db)

        # Setup Proxy
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)

        # Create View
        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)

        # Set Headers
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        #self.horizontal_header.setStretchLastSection(True)


        # QWidget Layout
        self.main_layout = QHBoxLayout()
        #size = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # Left layout
        #size.setHorizontalStretch(1)
        #self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)