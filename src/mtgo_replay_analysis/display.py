import typing
from PySide6.QtWidgets import (QWidget, QMainWindow, QVBoxLayout, QLabel, QTableView,
                               QHeaderView, QHBoxLayout, QSizePolicy, QGridLayout, QComboBox,
                               QHBoxLayout, QDateTimeEdit, QLineEdit, QDialog, QDialogButtonBox)
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel, QDate
from PySide6.QtGui import QIcon, QKeySequence
from mtgo_replay_analysis.ReplayDB import ReplayDB
import os
from .deck_tools.goldfish_scraper import scrape_goldfish
from tqdm import tqdm
import sys

class PopOutMatchInfoWindow(QWidget):
    def __init__(self, match_info):
        super().__init__()
        print(match_info)
        self.match_info = match_info

        self.match_id = match_info[0]
        self.date = match_info[1]
        self.player = match_info[2]
        self.opponent = match_info[3]
        self.game_wins = match_info[4:7]
        self.otps = match_info[7:10]
        self.mulls = match_info[10:13]
        self.p_cards = list(match_info[13:16])
        self.op_cards = list(match_info[16:19])
        self.match_win = match_info[19]
        self.match_format = match_info[20]
        self.p_deck = match_info[21]
        self.op_deck = match_info[22]

        for i in range(len(self.p_cards)):
            self.p_cards[i] = self.p_cards[i].replace('\", \"', '\n')
            self.p_cards[i] = self.p_cards[i].replace('\"', '')
            self.p_cards[i] = self.p_cards[i].replace('[', '')
            self.p_cards[i] = self.p_cards[i].replace(']', '')


            self.op_cards[i] = self.op_cards[i].replace('\", \"', '\n')
            self.op_cards[i] = self.op_cards[i].replace('\"', '')
            self.op_cards[i] = self.op_cards[i].replace('[', '')
            self.op_cards[i] = self.op_cards[i].replace(']', '')



        self.setWindowTitle(f"Match Info - {match_info[0]}")
        layout = QGridLayout()


        # Labels
        #self.op_label = QLabel(f"Opponent: ")
        game_winners = []
        for i in range(3):
            if self.game_wins[i] == 1:
                game_winners.append(self.player)
            elif self.game_wins[i] == 0:
                game_winners.append(self.opponent)
            else:
                game_winners.append("N/A")

        self.p_deck_label = QLabel(f"{self.p_deck}")
        self.op_deck_label = QLabel(f"{self.opponent} on {self.op_deck}")
        self.vs_label = QLabel("vs.")
        self.g1_label = QLabel(f"Game 1: Won by {game_winners[0]}")
        self.g2_label = QLabel(f"Game 2: Won by {game_winners[1]}")
        self.g3_label = QLabel(f"Game 3: Won by {game_winners[2]}")
        self.style_sheet_info = ("""QLabel {
                                        border: 2px solid white;
                                    }""")

        self.p_g1_cards = QLabel(f"{self.p_cards[0]}")
        self.p_g1_cards.setStyleSheet(self.style_sheet_info)
        self.p_g2_cards = QLabel(f"{self.p_cards[1]}")
        self.p_g2_cards.setStyleSheet(self.style_sheet_info)
        self.p_g3_cards = QLabel(f"{self.p_cards[2]}")
        self.p_g3_cards.setStyleSheet(self.style_sheet_info)

        self.op_g1_cards = QLabel(f"{self.op_cards[0]}")
        self.op_g1_cards.setStyleSheet(self.style_sheet_info)
        self.op_g2_cards = QLabel(f"{self.op_cards[1]}")
        self.op_g2_cards.setStyleSheet(self.style_sheet_info)
        self.op_g3_cards = QLabel(f"{self.op_cards[2]}")
        self.op_g3_cards.setStyleSheet(self.style_sheet_info)


        # Add things to window
        # Basic Game Info
        layout.addWidget(self.p_deck_label, 0, 0)
        layout.addWidget(self.vs_label, 0, 1)
        layout.addWidget(self.op_deck_label, 0, 2)

        # Game Labels
        layout.addWidget(self.g1_label, 1, 0)
        layout.addWidget(self.g2_label, 1, 2)
        layout.addWidget(self.g3_label, 1, 4)

        # Game Info
        g1_otp = "Play" if self.otps[0] == 1 else "Draw"
        g2_otp = "Play" if self.otps[1] == 1 else "Draw"
        g3_otp = "Play" if self.otps[2] == 1 else "Draw"
        self.g1_info_w = QLabel(f"On the {g1_otp}. Opened with {self.mulls[0]} Cards")
        self.g2_info_w = QLabel(f"On the {g2_otp}. Opened with {self.mulls[1]} Cards")
        self.g3_info_w = QLabel(f"On the {g3_otp}. Opened with {self.mulls[2]} Cards")

        layout.addWidget(self.g1_info_w, 2, 0)
        layout.addWidget(self.g2_info_w, 2, 2)
        layout.addWidget(self.g3_info_w, 2, 4)

        # Cards
        layout.addWidget(self.p_g1_cards, 3, 0)
        layout.addWidget(self.op_g1_cards, 3, 1)
        layout.addWidget(self.p_g2_cards, 3, 2)
        layout.addWidget(self.op_g2_cards, 3, 3)
        layout.addWidget(self.p_g3_cards, 3, 4)
        layout.addWidget(self.op_g3_cards, 3, 5)

        # Setup Window
        self.setLayout(layout)




'''

'''
class DisplayDriver(QMainWindow):
    def __init__(self, db: ReplayDB) -> None:
        super().__init__()
        self.setWindowTitle("MTGO Replay Analysis")
        self.db = db
        layout = QGridLayout()

        self.constructed_formats = ['standard',
                       'pioneer',
                       'modern',
                       'legacy',
                       'vintage',
                       'pauper',
                       'premodern']

        # Menu
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu("File")
        options_menu = self.menu.addMenu("Options")

        # File Buttons
        file_menu.addAction(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit),
                            "Exit", QKeySequence.StandardKey.Quit, self.close)
        file_menu.addAction("Update Decks", self.db.update_decks)
        file_menu.addAction("Assign Decks", self.assign_decks)

        # Options Buttons
        date_format_menu = options_menu.addMenu("Date Format")
        date_format_menu.addAction("MM/DD/YYYY", lambda: self.update_date_format("MM/dd/yyyy"))
        date_format_menu.addAction("DD/MM/YYYY", lambda: self.update_date_format("dd/MM/yyyy"))

        options_menu.addAction("Set Replay Folder Location", self.update_replay_folder_menu)
        options_menu.addAction("Set MTGO Username", self.update_username_menu)

        self.autosave = True

        # Match Info Widget
        self.table = MTGODataWidget(db)
        self.table.vertical_header.setVisible(False)
        self.table.table_view.doubleClicked.connect(self.create_match_info_popup)

        # Text Info
        win_rate = sum(int(self.table.model.data(self.table.model.createIndex(i, 2))) for i in range(self.table.model.rowCount())) / self.table.model.rowCount() * 100
        self.win_rate_widget = QLabel(f"Win Rate: {win_rate:.2f}%")

        matches_played = self.table.model.rowCount()
        self.matches_played_widget = QLabel(f"Matches Played: {matches_played}")

        # Format Filter
        self.format_drop_down = QComboBox()
        self.format_drop_down.addItems(['',
                       'standard',
                       'pioneer',
                       'modern',
                       'legacy',
                       'vintage',
                       'pauper',
                       'premodern',
                       'cube',
                       'missing'])
        self.format_drop_down.currentTextChanged.connect(self.table.proxy_model.setFilterbyFormat)
        self.format_drop_down.currentTextChanged.connect(self.update_text_info_after_filter)

        self.format_label = QLabel("Format:")

        # Date Stuff
        self.date_format = "MM/dd/yyyy"
        self.date_begin_label = QLabel("Start Date:")
        self.date_end_label = QLabel("End Date:")

        self.default_min_date = QDate(1999, 1, 1)
        self.default_max_date = QDate(2099, 1, 1)

        self.date_begin_input = QDateTimeEdit(self.default_min_date)
        self.date_begin_input.setDisplayFormat(self.date_format)
        self.date_begin_input.dateChanged.connect(self.update_min_date)
        self.date_begin_input.setMaximumDate(self.default_max_date)

        self.date_end_input = QDateTimeEdit(self.default_max_date)
        self.date_end_input.setDisplayFormat(self.date_format)
        self.date_end_input.dateChanged.connect(self.update_max_date)
        self.date_end_input.setMinimumDate(self.default_min_date)

        # Card Win Rate
        self.card_wr_card_label = QLabel("Card: ")
        self.card_wr_input = QLineEdit()
        self.card_wr_input.setMaximumWidth(150)
        self.card_wr = QLabel("--.--% (-/-)")

        self.card_wr_input.textEdited.connect(self.get_card_winrate)

        # Place Widgets
        layout.addWidget(self.table, 0, 0, 10, 1)
        layout.addWidget(self.win_rate_widget, 0, 1, 1, 2)
        layout.addWidget(self.matches_played_widget, 1, 1, 1, 2)
        layout.addWidget(self.format_label, 2, 1)
        layout.addWidget(self.format_drop_down, 2, 2)
        layout.addWidget(self.date_begin_label, 3, 1)
        layout.addWidget(self.date_begin_input, 3, 2)
        layout.addWidget(self.date_end_label, 4, 1)
        layout.addWidget(self.date_end_input, 4, 2)

        layout.addWidget(self.card_wr_card_label, 5, 1)
        layout.addWidget(self.card_wr_input, 5, 2)
        layout.addWidget(self.card_wr, 6, 1, 1, 2)

        # Make Main Window
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Prepare for popup windows
        self.match_popouts = {}


    def update_text_info_after_filter(self):
        num_rows = self.table.proxy_model.rowCount()
        if num_rows == 0:
            win_rate = 0
        else:
            win_rate =  sum(int(self.table.proxy_model.data(self.table.proxy_model.index(i, 2))) for i in
                       range(num_rows)) / num_rows * 100

        self.win_rate_widget.setText(f"Win Rate: {win_rate:.2f}%")
        self.matches_played_widget.setText(f"Matches Played: {num_rows}")
        self.get_card_winrate()

    def update_min_date(self):
        d_min = self.date_begin_input.date()
        d_max = self.date_end_input.date().toString('yyyy/MM/dd')
        self.date_end_input.setMinimumDate(d_min)
        self.table.proxy_model.setFilterbyDate(d_min.toString('yyyy/MM/dd'), d_max)
        self.update_text_info_after_filter()

    def update_max_date(self):
        d_min = self.date_begin_input.date().toString('yyyy/MM/dd')
        d_max = self.date_end_input.date()
        self.date_begin_input.setMaximumDate(d_max)
        self.table.proxy_model.setFilterbyDate(d_min, d_max.toString('yyyy/MM/dd'))
        self.update_text_info_after_filter()


    def assign_decks(self):
        pass

    def create_match_info_popup(self):
        for idx in self.table.table_view.selectionModel().selectedIndexes():
            #row_num = idx.row()
            col_num = idx.column()
            if col_num != self.table.proxy_model.columnCount() - 1:
                continue
            match_id = self.table.proxy_model.data(idx)
            self.db.cur.execute("SELECT * FROM match_data WHERE match_id = ?", (match_id,))
            db_row = self.db.cur.fetchone()
            p = PopOutMatchInfoWindow(db_row)
            self.match_popouts[match_id] = p
            p.show()

    def closeEvent(self, event) -> None:
        for w in self.match_popouts.values():
            w.close()

    def update_date_format(self, date_format: str) -> None:
        self.date_format = date_format
        self.date_begin_input.setDisplayFormat(self.date_format)
        self.date_end_input.setDisplayFormat(self.date_format)

    def update_replay_folder_menu(self):
        w = QDialog()
        layout = QVBoxLayout()
        info_box = QLineEdit()
        self.db.cur.execute("""
                        SELECT info FROM metadata 
                        WHERE name = 'replay_folder'
                        """)
        curr_folder = self.db.cur.fetchone()
        info_box.setText(curr_folder[0])

        def update_replay_folder():
            if os.path.isdir(info_box.text()):
                self.db.cur.execute("""
                                    REPLACE into metadata VALUES
                                    ('replay_folder', ?)
                                    """, (info_box.text(),))
                if self.autosave:
                    self.db.conn.commit()
                w.close()
            else:
                print("Invalid Folder")

        btn = ( QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btn_box = QDialogButtonBox(btn)
        btn_box.accepted.connect(update_replay_folder)
        btn_box.rejected.connect(w.close)

        layout.addWidget(info_box)
        layout.addWidget(btn_box)
        w.setLayout(layout)
        w.exec()




    def update_username_menu(self):
        w = QDialog()
        layout = QVBoxLayout()
        info_box = QLineEdit()
        self.db.cur.execute("""
                                SELECT info FROM metadata 
                                WHERE name = 'username'
                                """)
        curr_folder = self.db.cur.fetchone()
        info_box.setText(curr_folder[0])

        def update_username():
            self.db.cur.execute("""
                                REPLACE into metadata VALUES
                                ('username', ?)
                                """, (info_box.text(),))
            if self.autosave:
                self.db.conn.commit()
            w.close()


        btn = (QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btn_box = QDialogButtonBox(btn)
        btn_box.accepted.connect(update_username)
        btn_box.rejected.connect(w.close)

        layout.addWidget(info_box)
        layout.addWidget(btn_box)
        w.setLayout(layout)
        w.exec()

    def get_card_winrate(self):
        card_name = self.card_wr_input.text()
        if card_name == "":
            self.card_wr.setText("--.--% (-/-)")
            return
        games_with_card = 0
        games_card_won = 0
        for row in range(self.table.proxy_model.rowCount()):
            curr_idx = self.table.proxy_model.index(row, 0)
            match_id = self.table.proxy_model.data(curr_idx, role=Qt.ItemDataRole.UserRole)
            self.db.cur.execute("""
                                SELECT g1_win, g2_win, g3_win, g1_p_cards, g2_p_cards, g3_p_cards
                                FROM match_data
                                WHERE match_id = ?
                                """, (match_id,))
            match_info = self.db.cur.fetchone()
            for i in range(3):
                if card_name in match_info[i+3]:
                    games_with_card += 1
                    if match_info[i] == 1:
                        games_card_won += 1
        if games_with_card == 0:
            self.card_wr.setText("No Games With Card")
            return
        wr = games_card_won / games_with_card * 100
        self.card_wr.setText(f"{wr:.2f}% ({games_card_won}/{games_with_card})")



'''

'''
class MatchTableModel(QAbstractTableModel):
    def __init__(self, db: ReplayDB) -> None:
        super().__init__()
        # Pre Load Data
        self.db = db
        self.row_data = []
        self.labels = ("Date", "Opponent", "Win/Loss", "Format", "Player Deck", "Opponent Deck", "ID")
        self.db_column_names = ("match_date", "opponent", "match_win", "format", "player_deck", "opponent_deck", "match_id")

        # Load Data
        self.load_data()

        # Post Load Data
        self.column_count = len(self.labels)
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

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.ItemIsEnabled

        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            column = index.column()
            row = index.row()
            self.row_data[row][column] = value
            match_id = self.row_data[row][-1]
            self.db.cur.execute(f"""
                                UPDATE match_data
                                SET {self.db_column_names[column]} = ?
                                WHERE match_id = ?
                                """, (value, match_id))
            self.db.conn.commit()
            return True
        return False

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

    def setFilterbyFormat(self, deck_format):
        self.beginFilterChange()
        self.filters[3] = deck_format.lower()
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


