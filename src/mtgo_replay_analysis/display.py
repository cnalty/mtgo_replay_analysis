import typing
from PySide6.QtWidgets import (QWidget, QMainWindow, QVBoxLayout, QLabel, QTableView,
                               QHeaderView, QHBoxLayout, QSizePolicy, QGridLayout, QComboBox)
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel
from PySide6.QtGui import QIcon, QKeySequence
from mtgo_replay_analysis.ReplayDB import ReplayDB
import sys

'''

'''
class DisplayDriver(QMainWindow):
    def __init__(self, db: ReplayDB) -> None:
        super().__init__()
        self.setWindowTitle("MTGO Replay Analysis")
        #self.app = QApplication()
        self.db = db
        layout = QGridLayout()
        # Menu
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu("File")

        # Exit QAction
        file_menu.addAction(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit),
                            "Exit", QKeySequence.StandardKey.Quit, self.close)

        # Match Info Widget
        self.table = MTGODataWidget(db)

        # Win Rate Info
        win_rate = sum(int(self.table.model.data(self.table.model.createIndex(i, 2))) for i in range(self.table.model.rowCount())) / self.table.model.rowCount() * 100
        self.win_rate_widget = QLabel(f"Win Rate: {win_rate:.2f}%")

        # Filter Boxes
        self.format_drop_down = QComboBox()
        self.format_drop_down.addItems(['',
                       'standard',
                       'pioneer',
                       'modern',
                       'legacy',
                       'vintage',
                       'pauper',
                       'premodern',
                       'missing'])
        self.format_drop_down.currentTextChanged.connect(self.table.proxy_model.setFilterbyFormat)
        self.format_drop_down.currentTextChanged.connect(self.update_win_rate)



        # Place Widgets
        layout.addWidget(self.table, 0, 0, 0, 1)
        layout.addWidget(self.win_rate_widget, 0, 1)
        layout.addWidget(self.format_drop_down, 1, 1)

        # Make the widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        #sys.exit(self.app.exec())

    def update_win_rate(self):
        num_rows = self.table.proxy_model.rowCount()
        '''win_rate = 0
        for i in range(num_rows):
            idx = self.table.proxy_model.index(i, 2)
            print(idx)
            w_l = self.table.proxy_model.data(idx)
            print(w_l)
            win_rate += int(w_l)
        win_rate /= num_rows
        win_rate *= 100'''
        if num_rows == 0:
            win_rate = 0
        else:
            win_rate =  sum(int(self.table.proxy_model.data(self.table.proxy_model.index(i, 2))) for i in
                       range(num_rows)) / num_rows * 100

        self.win_rate_widget.setText(f"Win Rate: {win_rate:.2f}%")


'''

'''
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

'''

'''
class MTGOSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        QSortFilterProxyModel.__init__(self, *args, **kwargs)
        self.filters = {}


    def setFilterbyDate(self, start_date, end_date):
        self.beginFilterChange()
        self.filters[0] = (start_date, end_date)
        self.endFilterChange()

    def setFilterbyFormat(self, format):
        self.beginFilterChange()
        self.filters[3] = format.lower()
        self.endFilterChange()

    def filterAcceptsColumn(self, source_column, source_parent):
        return True

    def filterAcceptsRow(self, source_row, source_parent):
        for key, value in self.filters.items():
            idx = self.sourceModel().index(source_row, key, source_parent)
            if idx.isValid():
                # Date Filter
                if key == 0:
                    curr_date = self.sourceModel().data(idx)
                    if curr_date < value[0] or curr_date > value[1]:
                        return False
                # Format Filter
                elif key == 3:
                    curr_format = self.sourceModel().data(idx).lower()
                    if value == '':
                        return True
                    elif curr_format != value:
                        if value != 'missing':
                            return False
                        elif curr_format != '':
                            return False
        return True

'''

'''
class MTGODataWidget(QWidget):
    def __init__(self, db: ReplayDB) -> None:
        super().__init__()
        self.model = MatchTableModel(db)

        # Setup Proxy
        self.proxy_model = MTGOSortFilterProxyModel()
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


