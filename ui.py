from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QApplication, QFileDialog, QDialog
)
from PyQt6.QtCore import QTimer, Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from datetime import datetime

from system_info import get_cpu, get_ram, get_disks, get_system


APP_NAME = "Echo System Info Viewer"
APP_VERSION = "1.0"
WEBSITE_URL = "https://echotechnology-dev.github.io/"

COLORS = {
    "Normal": "#2ecc71",
    "High": "#f1c40f",
    "Critical": "#e74c3c"
}

STYLE = """
QWidget {
    background-color: #f4f5f7;
    color: #1e1e1e;
    font-family: Segoe UI;
    font-size: 10.5pt;
}
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #dcdcdc;
    border-radius: 10px;
    margin-top: 10px;
    padding: 8px;
}
QGroupBox:title {
    left: 12px;
    padding: 0 6px;
    font-weight: bold;
}
QPushButton {
    background-color: #ffffff;
    border: 1px solid #cfcfcf;
    padding: 8px;
    border-radius: 8px;
}
QPushButton:hover {
    background-color: #f0f0f0;
}
"""


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setFixedSize(380, 260)

        layout = QVBoxLayout()

        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:14pt; font-weight:bold;")

        version = QLabel(f"Version {APP_VERSION}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text = QLabel(
            "Lightweight system information utility.\n\n"
            "• Works fully offline\n"
            "• No telemetry\n"
            "• No background services\n"
            "• Low system impact\n\n"
            "Developed by Echo Technology"
        )
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setWordWrap(True)

        site_btn = QPushButton("Visit website")
        site_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(WEBSITE_URL)))

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addSpacing(10)
        layout.addWidget(text)
        layout.addStretch()
        layout.addWidget(site_btn)
        layout.addWidget(close_btn)

        self.setLayout(layout)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setFixedSize(540, 580)
        self.setStyleSheet(STYLE)

        self.paused = False

        self.cpu_label = QLabel()
        self.ram_label = QLabel()
        self.disk_label = QLabel()
        self.sys_label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.box("CPU", self.cpu_label))
        layout.addWidget(self.box("Memory", self.ram_label))
        layout.addWidget(self.box("Disks", self.disk_label))
        layout.addWidget(self.box("System", self.sys_label))

        btns = QHBoxLayout()
        self.pause_btn = QPushButton("Pause")
        self.copy_btn = QPushButton("Copy report")
        self.save_btn = QPushButton("Save report")
        self.about_btn = QPushButton("About")

        self.pause_btn.clicked.connect(self.toggle_pause)
        self.copy_btn.clicked.connect(self.copy_report)
        self.save_btn.clicked.connect(self.save_report)
        self.about_btn.clicked.connect(self.show_about)

        for b in (self.pause_btn, self.copy_btn, self.save_btn, self.about_btn):
            btns.addWidget(b)

        self.footer = QLabel("Auto-refresh: 5s • Offline • No telemetry • Portable")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setStyleSheet("color:#666; font-size:9pt;")

        layout.addLayout(btns)
        layout.addWidget(self.footer)

        self.setLayout(layout)

        self.refresh()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(5000)

    def box(self, title, label):
        label.setWordWrap(True)
        box = QGroupBox(title)
        l = QVBoxLayout()
        l.addWidget(label)
        box.setLayout(l)
        return box

    def badge(self, status):
        return f"<span style='color:{COLORS[status]};'><b>{status}</b></span>"

    def refresh(self):
        if self.paused:
            return

        cpu = get_cpu()
        ram = get_ram()
        disks = get_disks()
        sys = get_system()

        self.cpu_label.setText(
            f"{cpu['name']}<br>"
            f"Usage: {cpu['usage']}% — {self.badge(cpu['status'])}<br>"
            f"{cpu['message']}"
        )

        self.ram_label.setText(
            f"{ram['used']} / {ram['total']} GB ({ram['percent']}%) — "
            f"{self.badge(ram['status'])}<br>"
            f"{ram['message']}"
        )

        self.disk_label.setText("<br>".join(
            f"{d['name']} {d['free']} / {d['total']} GB — {self.badge(d['status'])}"
            for d in disks
        ) if disks else "No disks detected")

        self.sys_label.setText(
            f"{sys['os']} ({sys['arch']})<br>"
            f"Uptime: {sys['uptime']}"
        )

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.setText("Resume" if self.paused else "Pause")
        self.footer.setText("Paused • No system polling" if self.paused else
                            "Auto-refresh: 5s • Offline • No telemetry • Portable")

    def build_report(self):
        lines = [
            APP_NAME,
            "----------------------",
            f"CPU usage: {get_cpu()['usage']}%",
            f"RAM usage: {get_ram()['percent']}%",
            "Disks:"
        ]
        for d in get_disks():
            lines.append(f"  {d['name']} {d['free']} / {d['total']} GB ({d['status']})")
        lines.append(f"OS: {get_system()['os']}")
        lines.append(f"Uptime: {get_system()['uptime']}")
        lines.append(f"Website: {WEBSITE_URL}")
        return "\n".join(lines)

    def copy_report(self):
        QApplication.clipboard().setText(self.build_report())

    def save_report(self):
        name = f"echo-system-info-{datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt"
        path, _ = QFileDialog.getSaveFileName(self, "Save report", name, "Text files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.build_report())

    def show_about(self):
        AboutDialog(self).exec()
