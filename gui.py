import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit,
    QFileDialog, QComboBox, QListWidget, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont, QColor, QPalette

# Configure Gemini API
# genai.configure(api_key="YOUR_GOOGLE_API_KEY")  # Replace with your API key

class GeminiComplianceChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ComplyVerify")
        self.setGeometry(100, 100, 950, 750)
        self.setStyle()

        self.law_files = []
        self.contract_files = []

        layout = QVBoxLayout()

        # Law file section
        layout.addWidget(self._make_label("Upload EU Law Documents (PDF/DOCX):"))
        self.law_list = QListWidget()
        layout.addWidget(self.law_list)

        self.law_button = QPushButton("Upload Law Files")
        self.law_button.clicked.connect(self.load_law_files)
        layout.addWidget(self.law_button)

        # Country selection
        layout.addWidget(self._make_label("Select Country:"))
        self.country_dropdown = QComboBox()
        self.country_dropdown.addItems([
            "European Union", "Germany", "France", "Italy", "Spain",
            "Netherlands", "Poland", "Sweden", "Denmark", "Romania", "Other"
        ])
        layout.addWidget(self.country_dropdown)

        # Contract file section
        layout.addWidget(self._make_label("Upload Contract Files (PDF/DOCX):"))
        self.contract_list = QListWidget()
        layout.addWidget(self.contract_list)

        self.contract_button = QPushButton("Upload Contract Files")
        self.contract_button.clicked.connect(self.load_contract_files)
        layout.addWidget(self.contract_button)

        # Action buttons
        button_layout = QHBoxLayout()

        self.check_button = QPushButton("Check Compliance with Gemini")
        self.check_button.clicked.connect(self.send_to_gemini)
        button_layout.addWidget(self.check_button)

        self.visualize_button = QPushButton("Visualize Graphs")
        self.visualize_button.clicked.connect(self.visualize_graphs)
        button_layout.addWidget(self.visualize_button)

        layout.addLayout(button_layout)

        # Output
        layout.addWidget(self._make_label("Compliance Report:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def _make_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        return label

    # def setStyle(self):
    #     palette = QPalette()
    #     palette.setColor(QPalette.Window, QColor("#f4f6f9"))
    #     palette.setColor(QPalette.Base, QColor("#ffffff"))
    #     palette.setColor(QPalette.Text, QColor("#222222"))
    #     self.setPalette(palette)
    #     self.setFont(QFont("Segoe UI", 10))

    def setStyle(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f9;
                font-family: 'Segoe UI', 'Arial';
                font-size: 10pt;
            }

            QPushButton {
                background-color: #1d3557;
                color: white;
                padding: 8px 14px;
                border-radius: 8px;
                border: none;
            }

            QPushButton:hover {
                background-color: #457b9d;
            }

            QListWidget, QComboBox, QTextEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                padding: 6px;
                border-radius: 10px;
            }

            QLabel {
                color: #333333;
            }
        """)


    def load_law_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select EU Law Files", "", "Documents (*.pdf *.docx)")
        if files:
            self.law_files = files
            self.law_list.clear()
            self.law_list.addItems([f.split("/")[-1] for f in files])

    def load_contract_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Contract Files", "", "Documents (*.pdf *.docx)")
        if files:
            self.contract_files = files
            self.contract_list.clear()
            self.contract_list.addItems([f.split("/")[-1] for f in files])

    def send_to_gemini(self):
        pass

    def visualize_graphs(self):
        QMessageBox.information(self, "Visualize Graphs", "Graph visualization feature coming soon!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeminiComplianceChecker()
    window.show()
    sys.exit(app.exec_())
