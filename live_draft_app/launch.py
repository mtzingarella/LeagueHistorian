import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
from directed_continuous_scraper import DirectedContinuousScraper
from live_draft_tool import LiveDraftTool
7
login_url = 'https://fantasy.nfl.com'
update_frequency = 10  # in seconds
output_dir = 'output'
live_data_dir = 'SavedData/draftclient/livedata'

class ScraperThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, login_url, update_frequency, output_dir, live_data_dir, live_draft_tool):
        super().__init__()
        self.login_url = login_url
        self.update_frequency = update_frequency
        self.output_dir = output_dir
        self.live_data_dir = live_data_dir
        self.live_draft_tool = live_draft_tool
        self.running = True

    def run(self):
        while self.running:
            try:
                dcs = DirectedContinuousScraper(self.login_url, self.update_frequency, self.output_dir)
                dcs.scrape(self.update_frequency, self.live_data_dir, self.output_dir, self.live_draft_tool)
                self.update_signal.emit("Scraping stopped")
            except Exception as e:
                self.update_signal.emit(f"Scraper crashed: {e}")
                self.running = False

    def stop(self):
        self.running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scraper GUI")
        self.setGeometry(100, 100, 400, 200)

        self.status_label = QLabel("Status: Idle")
        self.start_button = QPushButton("Start Scraper")
        self.start_button.clicked.connect(self.start_scraper)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.scraper_thread = None

    def start_scraper(self):
        if self.scraper_thread is not None:
            self.scraper_thread.stop()
            self.scraper_thread.wait()

        self.status_label.setText("Status: Running")
        self.scraper_thread = ScraperThread(login_url, update_frequency, output_dir, live_data_dir, live_draft_tool)
        self.scraper_thread.update_signal.connect(self.update_status)
        self.scraper_thread.start()

    def update_status(self, message):
        self.status_label.setText(f"Status: {message}")
        if "crashed" in message:
            self.status_label.setText("Status: Crashed. Press 'Start Scraper' to restart.")

if __name__ == "__main__":
    live_draft_tool = LiveDraftTool(update_frequency, live_data_dir)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())