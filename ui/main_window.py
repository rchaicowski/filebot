from __future__ import annotations

from pathlib import Path
import threading

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QBrush
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QStatusBar, QFrame,
    QCheckBox, QComboBox, QLineEdit, QSplitter,
    QTextEdit, QProgressBar, QSizePolicy, QAbstractItemView,
)

from core.file_scanner import FileScanner, FileEntry
from ai.providers import AIProvider, NoAIProvider


# ── colours (single source of truth) ──────────────────────────────────────────
BG       = "#0f0f10"
SURFACE  = "#1a1a1e"
SURFACE2 = "#222228"
BORDER   = "#2e2e38"
ACCENT   = "#6c63ff"
ACCENT2  = "#a78bfa"
TEXT     = "#e8e6f0"
MUTED    = "#6e6c82"
SUCCESS  = "#4ade80"
WARNING  = "#fb923c"
DANGER   = "#f87171"


def _stylesheet() -> str:
    return f"""
    * {{
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        color: {TEXT};
    }}
    QMainWindow, QWidget {{
        background-color: {BG};
    }}
    QFrame#sidebar {{
        background-color: {SURFACE};
        border-right: 1px solid {BORDER};
    }}
    QFrame#topbar {{
        background-color: {SURFACE};
        border-bottom: 1px solid {BORDER};
    }}
    QPushButton {{
        background-color: {SURFACE2};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 7px 16px;
        font-size: 12px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {BORDER};
        border-color: {ACCENT};
    }}
    QPushButton:pressed {{
        background-color: {ACCENT};
        border-color: {ACCENT};
    }}
    QPushButton#btn_primary {{
        background-color: {ACCENT};
        border-color: {ACCENT};
        color: white;
    }}
    QPushButton#btn_primary:hover {{
        background-color: {ACCENT2};
        border-color: {ACCENT2};
    }}
    QPushButton#btn_danger {{
        background-color: transparent;
        border-color: {DANGER};
        color: {DANGER};
    }}
    QPushButton#btn_danger:hover {{
        background-color: {DANGER};
        color: white;
    }}
    QTableWidget {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 8px;
        gridline-color: {BORDER};
        selection-background-color: {ACCENT};
        font-size: 12px;
    }}
    QTableWidget::item {{
        padding: 6px 10px;
        border: none;
    }}
    QTableWidget::item:selected {{
        background-color: {ACCENT};
        color: white;
    }}
    QHeaderView::section {{
        background-color: {SURFACE2};
        border: none;
        border-bottom: 1px solid {BORDER};
        padding: 8px 10px;
        font-size: 11px;
        font-weight: 600;
        color: {MUTED};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    QComboBox {{
        background-color: {SURFACE2};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
        min-width: 140px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox:hover {{
        border-color: {ACCENT};
    }}
    QLineEdit {{
        background-color: {SURFACE2};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 7px 12px;
        font-size: 12px;
    }}
    QLineEdit:focus {{
        border-color: {ACCENT};
    }}
    QTextEdit {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 8px;
        font-size: 11px;
        color: {MUTED};
    }}
    QProgressBar {{
        background-color: {SURFACE2};
        border: 1px solid {BORDER};
        border-radius: 4px;
        height: 6px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background-color: {ACCENT};
        border-radius: 4px;
    }}
    QStatusBar {{
        background-color: {SURFACE};
        border-top: 1px solid {BORDER};
        font-size: 11px;
        color: {MUTED};
        padding: 0 12px;
    }}
    QScrollBar:vertical {{
        background: {SURFACE};
        width: 8px;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 4px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {MUTED};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QCheckBox {{
        spacing: 8px;
        font-size: 12px;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {BORDER};
        border-radius: 4px;
        background: {SURFACE2};
    }}
    QCheckBox::indicator:checked {{
        background-color: {ACCENT};
        border-color: {ACCENT};
    }}
    QSplitter::handle {{
        background-color: {BORDER};
        width: 1px;
    }}
    QLabel#logo {{
        font-size: 20px;
        font-weight: 800;
        letter-spacing: 2px;
        color: {TEXT};
    }}
    QLabel#logo span {{
        color: {ACCENT};
    }}
    QLabel#section_title {{
        font-size: 10px;
        font-weight: 700;
        color: {MUTED};
        letter-spacing: 2px;
        text-transform: uppercase;
    }}
    QLabel#stat_value {{
        font-size: 22px;
        font-weight: 700;
        color: {TEXT};
    }}
    QLabel#stat_label {{
        font-size: 10px;
        color: {MUTED};
        letter-spacing: 1px;
    }}
    QLabel#ai_badge {{
        font-size: 10px;
        font-weight: 700;
        background-color: {SURFACE2};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 2px 10px;
        color: {MUTED};
    }}
    QFrame#stat_card {{
        background-color: {SURFACE2};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 4px;
    }}
    """


# ── worker thread for scanning ─────────────────────────────────────────────────
class ScanWorker(QThread):
    file_found   = pyqtSignal(FileEntry)
    scan_done    = pyqtSignal(list)
    progress     = pyqtSignal(int)

    def __init__(self, folder: Path, recursive: bool, extensions: list[str] | None):
        super().__init__()
        self.folder = folder
        self.recursive = recursive
        self.extensions = extensions
        self._scanner = FileScanner()

    def run(self):
        def on_progress(i: int, entry: FileEntry):
            self.file_found.emit(entry)
            self.progress.emit(i)

        entries = self._scanner.scan(
            self.folder,
            recursive=self.recursive,
            extensions=self.extensions,
            on_progress=on_progress,
        )
        self.scan_done.emit(entries)

    def stop(self):
        self._scanner.stop()


# ── main window ────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):

    def __init__(self, ai_provider: AIProvider | None = None):
        super().__init__()
        self.ai_provider = ai_provider or NoAIProvider()
        self._entries: list[FileEntry] = []
        self._worker: ScanWorker | None = None
        self._folder: Path | None = None

        self.setWindowTitle("FileBot")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)
        self.setStyleSheet(_stylesheet())

        self._build_ui()
        self._update_stats()

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        main_area = QWidget()
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self._build_topbar())
        main_layout.addWidget(self._build_content(), 1)

        root.addWidget(main_area, 1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready — open a folder to start")

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(4)

        # Logo
        logo = QLabel("FILE<span style='color:#6c63ff'>BOT</span>")
        logo.setObjectName("logo")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setContentsMargins(0, 0, 0, 16)
        layout.addWidget(logo)

        # AI badge
        ai_badge = QLabel(f"  ◉  {self.ai_provider.name}")
        ai_badge.setObjectName("ai_badge")
        ai_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ai_badge)
        layout.addSpacing(20)

        # Section: actions
        layout.addWidget(self._section_label("Actions"))

        self._nav_buttons: list[QPushButton] = []
        for label, icon_char, slot in [
            ("  Rename",   "✦", self._on_rename),
            ("  Organize", "⊞", self._on_organize),
            ("  Cleanup",  "◈", self._on_cleanup),
            ("  Summarize","⬡", self._on_summarize),
        ]:
            btn = QPushButton(f"{icon_char}{label}")
            btn.setCheckable(True)
            btn.clicked.connect(slot)
            layout.addWidget(btn)
            self._nav_buttons.append(btn)

        layout.addSpacing(20)
        layout.addWidget(self._section_label("Stats"))

        # Stat cards
        for attr in ("_stat_files", "_stat_size", "_stat_selected"):
            card = QFrame()
            card.setObjectName("stat_card")
            card.setFixedHeight(52)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(10, 6, 10, 6)
            cl.setSpacing(0)
            val = QLabel("—")
            val.setObjectName("stat_value")
            lbl = QLabel(attr.replace("_stat_", "").upper())
            lbl.setObjectName("stat_label")
            cl.addWidget(val)
            cl.addWidget(lbl)
            setattr(self, attr, val)
            layout.addWidget(card)
            layout.addSpacing(4)

        layout.addStretch()

        # Settings button at bottom
        settings_btn = QPushButton("⚙  Settings")
        settings_btn.clicked.connect(self._on_settings)
        layout.addWidget(settings_btn)

        return sidebar

    def _build_topbar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("topbar")
        bar.setFixedHeight(60)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        # Folder path display
        self.folder_label = QLineEdit()
        self.folder_label.setPlaceholderText("No folder selected — click Browse")
        self.folder_label.setReadOnly(True)
        self.folder_label.setMinimumWidth(300)
        layout.addWidget(self.folder_label, 1)

        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_folder)
        layout.addWidget(browse_btn)

        # Extension filter
        self.ext_filter = QComboBox()
        self.ext_filter.addItems(["All files", ".txt", ".csv", ".json", ".pdf", ".png", ".jpg", ".mp4"])
        self.ext_filter.currentTextChanged.connect(self._on_filter_changed)
        layout.addWidget(self.ext_filter)

        # Recursive toggle
        self.recursive_cb = QCheckBox("Recursive")
        self.recursive_cb.setChecked(False)
        layout.addWidget(self.recursive_cb)

        layout.addSpacing(10)

        # Run / Stop
        self.run_btn = QPushButton("▶  Run")
        self.run_btn.setObjectName("btn_primary")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._on_run)
        layout.addWidget(self.run_btn)

        self.stop_btn = QPushButton("■  Stop")
        self.stop_btn.setObjectName("btn_danger")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        layout.addWidget(self.stop_btn)

        return bar

    def _build_content(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(1)

        # File table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["✓", "Name", "Extension", "Size", "AI Suggestion"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 36)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 90)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        # Override alternating row color via palette
        pal = self.table.palette()
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(SURFACE2))
        self.table.setPalette(pal)

        splitter.addWidget(self.table)

        # Log panel
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(8, 6, 8, 6)
        log_layout.setSpacing(4)

        log_header = QHBoxLayout()
        log_header.addWidget(self._section_label("Log"))
        log_header.addStretch()
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedHeight(22)
        clear_btn.setFixedWidth(60)
        clear_btn.clicked.connect(lambda: self.log.clear())
        log_header.addWidget(clear_btn)
        log_layout.addLayout(log_header)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedHeight(120)
        log_layout.addWidget(self.log)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setFixedHeight(6)
        log_layout.addWidget(self.progress)

        splitter.addWidget(log_widget)
        splitter.setSizes([560, 180])

        return splitter

    # ── helpers ────────────────────────────────────────────────────────────────

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("section_title")
        lbl.setContentsMargins(0, 4, 0, 6)
        return lbl

    def _log(self, msg: str, color: str = MUTED):
        self.log.append(f'<span style="color:{color}">→ {msg}</span>')

    def _update_stats(self):
        total = len(self._entries)
        selected = sum(1 for e in self._entries if e.selected)
        total_size = sum(e.size for e in self._entries)

        self._stat_files.setText(str(total))
        self._stat_size.setText(self._human_size(total_size))
        self._stat_selected.setText(str(selected))

    def _human_size(self, size: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.0f} {unit}"
            size /= 1024
        return f"{size:.1f} GB"

    def _populate_table(self, entries: list[FileEntry]):
        self.table.setRowCount(0)
        for entry in entries:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Checkbox col
            cb = QTableWidgetItem()
            cb.setCheckState(Qt.CheckState.Checked if entry.selected else Qt.CheckState.Unchecked)
            cb.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            cb.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, cb)

            self.table.setItem(row, 1, QTableWidgetItem(entry.name))
            self.table.setItem(row, 2, QTableWidgetItem(entry.extension or "—"))

            size_item = QTableWidgetItem(entry.size_human)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 3, size_item)

            suggestion = QTableWidgetItem(entry.ai_suggestion or "—")
            suggestion.setForeground(QColor(ACCENT2) if entry.ai_suggestion else QColor(MUTED))
            self.table.setItem(row, 4, suggestion)

        self._update_stats()

    # ── slots ──────────────────────────────────────────────────────────────────

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", str(Path.home()))
        if folder:
            self._folder = Path(folder)
            self.folder_label.setText(str(self._folder))
            self.run_btn.setEnabled(True)
            self._log(f"Folder selected: {folder}", TEXT)
            self._scan_folder()

    def _scan_folder(self):
        if not self._folder:
            return

        ext_text = self.ext_filter.currentText()
        extensions = None if ext_text == "All files" else [ext_text]

        self._entries.clear()
        self.table.setRowCount(0)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # indeterminate
        self.stop_btn.setEnabled(True)

        self._worker = ScanWorker(
            self._folder,
            recursive=self.recursive_cb.isChecked(),
            extensions=extensions,
        )
        self._worker.file_found.connect(self._on_file_found)
        self._worker.scan_done.connect(self._on_scan_done)
        self._worker.start()
        self._log(f"Scanning {self._folder}…", MUTED)

    def _on_file_found(self, entry: FileEntry):
        self._entries.append(entry)
        row = self.table.rowCount()
        self.table.insertRow(row)

        cb = QTableWidgetItem()
        cb.setCheckState(Qt.CheckState.Checked)
        cb.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 0, cb)
        self.table.setItem(row, 1, QTableWidgetItem(entry.name))
        self.table.setItem(row, 2, QTableWidgetItem(entry.extension or "—"))
        size_item = QTableWidgetItem(entry.size_human)
        size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 3, size_item)
        self.table.setItem(row, 4, QTableWidgetItem("—"))

        # Scroll to last row while scanning
        self.table.scrollToBottom()

    def _on_scan_done(self, entries: list[FileEntry]):
        self.progress.setVisible(False)
        self.stop_btn.setEnabled(False)
        self._update_stats()
        count = len(entries)
        self._log(
            f"Scan complete — {count} file{'s' if count != 1 else ''} found",
            SUCCESS,
        )
        self.status_bar.showMessage(f"{count} files loaded from {self._folder}")

    def _on_filter_changed(self, _text: str):
        if self._folder:
            self._scan_folder()

    def _on_selection_changed(self):
        selected_rows = len(self.table.selectedItems()) // self.table.columnCount()
        self.status_bar.showMessage(f"{selected_rows} row(s) selected")

    def _on_run(self):
        if not self._entries:
            self._log("No files loaded. Browse a folder first.", WARNING)
            return
        self._log("Run clicked — action not yet implemented in v0.1", WARNING)

    def _on_stop(self):
        if self._worker:
            self._worker.stop()
            self._log("Scan stopped by user.", WARNING)
            self.stop_btn.setEnabled(False)
            self.progress.setVisible(False)

    def _on_rename(self):   self._log("Rename action selected.", TEXT)
    def _on_organize(self): self._log("Organize action selected.", TEXT)
    def _on_cleanup(self):  self._log("Data Cleanup action selected.", TEXT)
    def _on_summarize(self):self._log("Summarize action selected.", TEXT)
    def _on_settings(self): self._log("Settings — coming soon.", MUTED)
