import logging
import math
import re
import sys
import threading
import traceback
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QSize, QThread, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPixmap, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout,
    QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPlainTextEdit, QPushButton, QSizePolicy, QStackedWidget, QToolButton, QVBoxLayout, QWidget,
)

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / "src"))

import settings

STYLE_SHEET = """
* { font-family: 'Inter', 'Microsoft JhengHei', sans-serif; color: #e4e1e7; }
QMainWindow, QWidget#Root { background-color: #131317; }
QWidget#TopBar {
    background-color: #131317;
    border-bottom: 0px;
}
QLabel#BrandLabel {
    color: #a3c9ff;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: -0.5px;
}
QWidget#SideNav { background-color: #1f1f23; }
QPushButton#NavBtn, QToolButton#NavBtn {
    background-color: transparent;
    color: #c1c6d4;
    border: none;
    padding: 14px 6px;
    text-align: center;
    font-size: 10px;
}
QPushButton#NavBtn:hover, QToolButton#NavBtn:hover { background-color: #353439; color: white; }
QPushButton#NavBtn:checked, QToolButton#NavBtn:checked {
    background-color: #2a2a2e;
    color: #a3c9ff;
    border-right: 2px solid #a3c9ff;
}
QLabel#PageTitle {
    font-size: 22px;
    font-weight: 600;
    color: #e4e1e7;
}
QLabel#PageSubtitle {
    font-size: 12px;
    color: #c1c6d4;
}
QFrame#Card {
    background-color: #1f1f23;
    border-radius: 8px;
}
QLabel#CardTitle {
    font-size: 13px;
    font-weight: 500;
    color: #e4e1e7;
}
QLabel#FieldLabel {
    font-size: 11px;
    color: #c1c6d4;
}
QLineEdit#PathEdit {
    background-color: #1b1b1f;
    border: none;
    border-radius: 3px;
    padding: 8px 12px;
    color: #e4e1e7;
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 12px;
}
QLineEdit#PathEdit:focus {
    background-color: #2a2a2e;
    border-bottom: 2px solid #a3c9ff;
}
QPushButton#BrowseBtn {
    background-color: #2a2a2e;
    color: #e4e1e7;
    border: none;
    border-radius: 3px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#BrowseBtn:hover { background-color: #353439; }
QPushButton#ClearBtn {
    background-color: transparent;
    color: #c1c6d4;
    border: none;
    border-radius: 3px;
    padding: 8px 12px;
    font-size: 12px;
}
QPushButton#ClearBtn:hover { color: #ffb4ab; background-color: #2a2a2e; }
QPushButton#ExecuteBtn {
    background-color: #a3c9ff;
    color: #00315c;
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#ExecuteBtn:hover { background-color: #c6dcff; }
QPushButton#ExecuteBtn:disabled { background-color: #414752; color: #8c919d; }
QPushButton#StopBtn {
    background-color: #1f1f23;
    color: #ffb4ab;
    border: 1px solid #93000a;
    border-radius: 3px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton#StopBtn:hover { background-color: #2a2a2e; }
QPushButton#StopBtn:disabled { color: #8c919d; border-color: #414752; }
QLabel#StatusChip {
    background-color: #434a4f;
    color: #b2b9bf;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 500;
}
QLabel#StatusChipRun {
    background-color: #0061ad;
    color: #c6dcff;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 500;
}
QPlainTextEdit#Terminal {
    background-color: #0e0e12;
    color: #e4e1e7;
    border: none;
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 12px;
    padding: 12px;
}
QFrame#TerminalHeader {
    background-color: #2a2a2e;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}
QFrame#TerminalBody {
    background-color: #0e0e12;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
}
QLabel#TerminalTitle {
    font-size: 10px;
    font-weight: 500;
    color: #c1c6d4;
    letter-spacing: 2px;
}
QComboBox, QDoubleSpinBox {
    background-color: #1b1b1f;
    border: none;
    border-radius: 3px;
    padding: 6px 10px;
    color: #e4e1e7;
    min-width: 140px;
    font-size: 12px;
}
QComboBox:focus, QDoubleSpinBox:focus {
    background-color: #2a2a2e;
    border-bottom: 2px solid #a3c9ff;
}
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #1f1f23;
    color: #e4e1e7;
    selection-background-color: #353439;
}
QPushButton#SaveBtn {
    background-color: #a3c9ff;
    color: #00315c;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#SaveBtn:hover { background-color: #c6dcff; }
QMessageBox { background-color: #ffffff; }
QMessageBox QLabel { color: #000000; font-size: 13px; }
QMessageBox QPushButton {
    color: #000000;
    background-color: #f0f0f0;
    border: 1px solid #c0c0c0;
    border-radius: 3px;
    padding: 6px 18px;
    min-width: 70px;
}
QMessageBox QPushButton:hover { background-color: #e0e0e0; }
QMessageBox QPushButton:default { background-color: #a3c9ff; color: #00315c; border: none; }
QScrollBar:vertical { background: #131317; width: 8px; }
QScrollBar::handle:vertical { background: #353439; border-radius: 4px; }
QScrollBar::handle:vertical:hover { background: #414752; }
"""


class QtLogHandler(logging.Handler, QObject):
    log_emitted = Signal(str, str)  # level_name, message

    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        try:
            self.log_emitted.emit(record.levelname, self.format(record))
        except Exception:
            pass


class Worker(QObject):
    finished = Signal(bool, str)  # success, message

    def __init__(self, excel_path, stop_event):
        super().__init__()
        self.excel_path = excel_path
        self.stop_event = stop_event

    def run(self):
        try:
            import importlib
            import main as main_mod
            importlib.reload(main_mod)
            main_mod.main(excel_path=self.excel_path, stop_event=self.stop_event)
            self.finished.emit(True, "執行完成")
        except Exception as e:
            tb = traceback.format_exc()
            logging.getLogger().error(tb)
            self.finished.emit(False, f"{type(e).__name__}: {e}")


class ProcessorPage(QWidget):
    def __init__(self, log_handler):
        super().__init__()
        self.selected_path = ""
        self.stop_event = None
        self.thread = None
        self.worker = None
        self._build(log_handler)

    def _build(self, log_handler):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # Page header
        title = QLabel("Data Processing Engine")
        title.setObjectName("PageTitle")
        subtitle = QLabel("選擇 Excel 檔案並執行會計傳票自動化作業。")
        subtitle.setObjectName("PageSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        # Config row
        config_row = QHBoxLayout()
        config_row.setSpacing(12)

        # File card
        file_card = QFrame()
        file_card.setObjectName("Card")
        fl = QVBoxLayout(file_card)
        fl.setContentsMargins(16, 16, 16, 16)
        fl.setSpacing(8)
        fl.addWidget(self._card_title("Input Configuration"))
        label = QLabel("Excel 檔案")
        label.setObjectName("FieldLabel")
        fl.addWidget(label)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.path_edit = QLineEdit()
        self.path_edit.setObjectName("PathEdit")
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("尚未選擇檔案...")
        browse = QPushButton("  Browse")
        browse.setObjectName("BrowseBtn")
        browse.clicked.connect(self._browse)
        clear = QPushButton("Clear")
        clear.setObjectName("ClearBtn")
        clear.clicked.connect(self._clear)
        row.addWidget(self.path_edit, 1)
        row.addWidget(browse)
        row.addWidget(clear)
        fl.addLayout(row)
        fl.addStretch()

        # Exec card
        exec_card = QFrame()
        exec_card.setObjectName("Card")
        el = QVBoxLayout(exec_card)
        el.setContentsMargins(16, 16, 16, 16)
        el.setSpacing(8)
        el.addWidget(self._card_title("Execution"))

        status_row = QHBoxLayout()
        s_label = QLabel("狀態")
        s_label.setObjectName("FieldLabel")
        self.status_chip = QLabel("IDLE")
        self.status_chip.setObjectName("StatusChip")
        status_row.addWidget(s_label)
        status_row.addStretch()
        status_row.addWidget(self.status_chip)
        el.addLayout(status_row)
        el.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.exec_btn = QPushButton("▶  Execute")
        self.exec_btn.setObjectName("ExecuteBtn")
        self.exec_btn.clicked.connect(self._execute)
        self.stop_btn = QPushButton("■  Stop")
        self.stop_btn.setObjectName("StopBtn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop)
        btn_row.addWidget(self.exec_btn)
        btn_row.addWidget(self.stop_btn)
        el.addLayout(btn_row)

        config_row.addWidget(file_card, 2)
        config_row.addWidget(exec_card, 1)
        root.addLayout(config_row)

        # Terminal
        term_wrap = QVBoxLayout()
        term_wrap.setSpacing(0)
        header = QFrame()
        header.setObjectName("TerminalHeader")
        header.setFixedHeight(36)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 0, 16, 0)
        t_title = QLabel("SYSTEM OUTPUT")
        t_title.setObjectName("TerminalTitle")
        clear_log = QPushButton("Clear")
        clear_log.setObjectName("ClearBtn")
        clear_log.clicked.connect(lambda: self.terminal.clear())
        hl.addWidget(t_title)
        hl.addStretch()
        hl.addWidget(clear_log)

        body = QFrame()
        body.setObjectName("TerminalBody")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(0, 0, 0, 0)
        self.terminal = QPlainTextEdit()
        self.terminal.setObjectName("Terminal")
        self.terminal.setReadOnly(True)
        bl.addWidget(self.terminal)

        term_wrap.addWidget(header)
        term_wrap.addWidget(body, 1)
        root.addLayout(term_wrap, 1)

        log_handler.log_emitted.connect(self._append_log)

    def _card_title(self, text):
        lab = QLabel(text)
        lab.setObjectName("CardTitle")
        return lab

    def _append_log(self, level, msg):
   
        color = {
            "DEBUG": "#8c919d",
            "INFO": "#ececec",
            "WARNING": "#ffb4ab",
            "ERROR": "#ffb4ab",
            "CRITICAL": "#ffb4ab",
        }.get(level, "#e4e1e7")
        self.terminal.appendHtml(
            f'<span style="color:{color};">{msg}</span>'
        )
        self.terminal.moveCursor(QTextCursor.End)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "選擇 Excel 檔案", str(BASE_DIR), "Excel Files (*.xlsx *.xls)"
        )
        if path:
            self.selected_path = path
            self.path_edit.setText(path)

    def _clear(self):
        self.selected_path = ""
        self.path_edit.clear()

    def _set_running(self, running):
        self.exec_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        if running:
            self.status_chip.setText("RUNNING")
            self.status_chip.setObjectName("StatusChipRun")
        else:
            self.status_chip.setText("IDLE")
            self.status_chip.setObjectName("StatusChip")
        self.status_chip.style().unpolish(self.status_chip)
        self.status_chip.style().polish(self.status_chip)

    def _execute(self):
        if not self.selected_path:
            QMessageBox.warning(self, "提示", "請先選擇 Excel 檔案")
            return
        self.stop_event = threading.Event()
        self.thread = QThread()
        self.worker = Worker(self.selected_path, self.stop_event)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self._set_running(True)
        self.thread.start()

    def _stop(self):
        if self.stop_event is not None:
            self.stop_event.set()
            logging.getLogger().warning("使用者要求中斷執行...")

    def _on_finished(self, success, message):
        self._set_running(False)
        if not success:
            QMessageBox.critical(self, "執行失敗", message)


class SettingsPage(QWidget):
    SLEEP_FIELDS = [
        ("BODY_SLEEP", "Body Sleep"),
        ("DEBIT_CREDIT_SLEEP", "Debit/Credit Sleep"),
        ("ACCOUNT_CODE_SLEEP", "Account Code Sleep"),
        ("DESCRIPTION_SLEEP", "Description Sleep"),
        ("DEPT_SLEEP", "Dept Sleep"),
        ("AMOUNT_SLEEP", "Amount Sleep"),
        ("PROJECT_CODE_SLEEP", "Project Code Sleep"),
        ("LINE_NOTE_SLEEP", "Line Note Sleep"),
    ]

    def __init__(self):
        super().__init__()
        self._build()
        self._load()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("Settings")
        title.setObjectName("PageTitle")
        subtitle = QLabel("修改 logging 等級與各欄位等待時間 (settings.py)。")
        subtitle.setObjectName("PageSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        # Logging card
        log_card = QFrame()
        log_card.setObjectName("Card")
        lc = QVBoxLayout(log_card)
        lc.setContentsMargins(20, 20, 20, 20)
        lc.setSpacing(10)
        lc.addWidget(self._card_title("Logging"))
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft)
        self.log_combo = QComboBox()
        self.log_combo.addItems(["DEBUG", "INFO"])
        form.addRow(self._field_label("Log Level"), self.log_combo)
        lc.addLayout(form)
        root.addWidget(log_card)

        # Sleep card
        sleep_card = QFrame()
        sleep_card.setObjectName("Card")
        sc = QVBoxLayout(sleep_card)
        sc.setContentsMargins(20, 20, 20, 20)
        sc.setSpacing(10)
        sc.addWidget(self._card_title("Sleep Timings (秒)"))
        s_form = QFormLayout()
        s_form.setSpacing(8)
        s_form.setLabelAlignment(Qt.AlignLeft)
        self.sleep_spins = {}
        for key, label in self.SLEEP_FIELDS:
            spin = QDoubleSpinBox()
            spin.setDecimals(2)
            spin.setRange(0.0, 60.0)
            spin.setSingleStep(0.1)
            self.sleep_spins[key] = spin
            s_form.addRow(self._field_label(label), spin)
        sc.addLayout(s_form)
        root.addWidget(sleep_card)

        # Save
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("SaveBtn")
        self.save_btn.clicked.connect(self._save)
        btn_row.addWidget(self.save_btn)
        root.addLayout(btn_row)
        root.addStretch()

    def _card_title(self, text):
        lab = QLabel(text)
        lab.setObjectName("CardTitle")
        return lab

    def _field_label(self, text):
        lab = QLabel(text)
        lab.setObjectName("FieldLabel")
        return lab

    def _load(self):
        import importlib
        importlib.reload(settings)
        level_name = logging.getLevelName(settings.LOG_LEVEL)
        idx = self.log_combo.findText(level_name)
        self.log_combo.setCurrentIndex(idx if idx >= 0 else 0)
        for key, _ in self.SLEEP_FIELDS:
            self.sleep_spins[key].setValue(float(getattr(settings, key, 0.0)))

    def _save(self):
        path = BASE_DIR / "settings.py"
        text = path.read_text(encoding="utf-8")

        level = self.log_combo.currentText()
        text = re.sub(
            r"^LOG_LEVEL\s*=.*$",
            f"LOG_LEVEL = logging.{level}",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        for key, _ in self.SLEEP_FIELDS:
            value = self.sleep_spins[key].value()
            text = re.sub(
                rf"^{key}\s*=.*$",
                f"{key} = {value}",
                text,
                count=1,
                flags=re.MULTILINE,
            )
        path.write_text(text, encoding="utf-8")

        import importlib
        importlib.reload(settings)
        logging.getLogger().setLevel(settings.LOG_LEVEL)
        QMessageBox.information(self, "儲存成功", "設定已寫入 settings.py")


def _make_processor_icon(size: int = 24) -> QIcon:
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    # Blue circle background
    p.setBrush(QColor("#a3c9ff"))
    p.drawEllipse(0, 0, size, size)
    # Dark play triangle
    p.setBrush(QColor("#131317"))
    path = QPainterPath()
    cx, cy = size / 2, size / 2
    path.moveTo(cx - 3, cy - 5)
    path.lineTo(cx - 3, cy + 5)
    path.lineTo(cx + 5, cy)
    path.closeSubpath()
    p.drawPath(path)
    p.end()
    return QIcon(px)


def _make_settings_icon(size: int = 24) -> QIcon:
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    # Blue circle background
    p.setBrush(QColor("#a3c9ff"))
    p.drawEllipse(0, 0, size, size)
    # Dark gear shape — 8 teeth, smaller and cleaner
    p.setBrush(QColor("#131317"))
    cx, cy = size / 2.0, size / 2.0
    n_teeth = 8
    outer_r = size * 0.21   # valley radius
    tooth_r = size * 0.30   # tooth tip radius
    tooth_half = math.pi / n_teeth * 0.60
    gear_path = QPainterPath()
    for i in range(n_teeth):
        base = 2 * math.pi * i / n_teeth - math.pi / 2
        p1 = (cx + outer_r * math.cos(base - tooth_half * 1.3),
              cy + outer_r * math.sin(base - tooth_half * 1.3))
        p2 = (cx + tooth_r * math.cos(base - tooth_half * 0.5),
              cy + tooth_r * math.sin(base - tooth_half * 0.5))
        p3 = (cx + tooth_r * math.cos(base + tooth_half * 0.5),
              cy + tooth_r * math.sin(base + tooth_half * 0.5))
        p4 = (cx + outer_r * math.cos(base + tooth_half * 1.3),
              cy + outer_r * math.sin(base + tooth_half * 1.3))
        if i == 0:
            gear_path.moveTo(*p1)
        else:
            gear_path.lineTo(*p1)
        gear_path.lineTo(*p2)
        gear_path.lineTo(*p3)
        gear_path.lineTo(*p4)
    gear_path.closeSubpath()
    p.drawPath(gear_path)
    # Blue center hole
    p.setBrush(QColor("#a3c9ff"))
    hole_r = size * 0.12
    p.drawEllipse(int(cx - hole_r), int(cy - hole_r), int(hole_r * 2), int(hole_r * 2))
    p.end()
    return QIcon(px)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoucherAutomate")
        self.resize(1200, 780)

        # Logging handler
        self.log_handler = QtLogHandler()
        root_logger = logging.getLogger()
        root_logger.setLevel(settings.LOG_LEVEL)
        root_logger.addHandler(self.log_handler)

        central = QWidget()
        central.setObjectName("Root")
        self.setCentralWidget(central)
        v = QVBoxLayout(central)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        # Top bar
        top = QWidget()
        top.setObjectName("TopBar")
        top.setFixedHeight(52)
        tl = QHBoxLayout(top)
        tl.setContentsMargins(24, 0, 24, 0)
        brand = QLabel("VoucherAutomate")
        brand.setStyleSheet("font-size: 22px;")
        brand.setObjectName("BrandLabel")
        tl.addWidget(brand)
        tl.addStretch()
        v.addWidget(top)

        # Body: side nav + stacked pages
        body = QWidget()
        bl = QHBoxLayout(body)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(0)

        side = QWidget()
        side.setObjectName("SideNav")
        side.setFixedWidth(72)
        sv = QVBoxLayout(side)
        sv.setContentsMargins(0, 12, 0, 12)
        sv.setSpacing(4)

        _nav_sp = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.processor_btn = QToolButton()
        self.processor_btn.setText("Processor")
        self.processor_btn.setIcon(_make_processor_icon(24))
        self.processor_btn.setIconSize(QSize(24, 24))
        self.processor_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.processor_btn.setObjectName("NavBtn")
        self.processor_btn.setCheckable(True)
        self.processor_btn.setChecked(True)
        self.processor_btn.setSizePolicy(_nav_sp)
        self.processor_btn.clicked.connect(lambda: self._switch(0))

        self.settings_btn = QToolButton()
        self.settings_btn.setText("Settings")
        self.settings_btn.setIcon(_make_settings_icon(24))
        self.settings_btn.setIconSize(QSize(24, 24))
        self.settings_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.settings_btn.setObjectName("NavBtn")
        self.settings_btn.setCheckable(True)
        self.settings_btn.setSizePolicy(_nav_sp)
        self.settings_btn.clicked.connect(lambda: self._switch(1))

        sv.addWidget(self.processor_btn)
        sv.addStretch()
        sv.addWidget(self.settings_btn)

        self.stack = QStackedWidget()
        self.processor_page = ProcessorPage(self.log_handler)
        self.settings_page = SettingsPage()
        self.stack.addWidget(self.processor_page)
        self.stack.addWidget(self.settings_page)

        bl.addWidget(side)
        bl.addWidget(self.stack, 1)
        v.addWidget(body, 1)

    def _switch(self, index):
        self.stack.setCurrentIndex(index)
        self.processor_btn.setChecked(index == 0)
        self.settings_btn.setChecked(index == 1)
        if index == 1:
            self.settings_page._load()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    app.setFont(QFont("Inter", 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
