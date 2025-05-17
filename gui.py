import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit,
    QFileDialog, QLineEdit, QMessageBox, QComboBox
)
from PyQt5.QtGui import QTextCharFormat, QTextCursor, QColor

class ComplianceChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EU Law Compliance Checker")
        self.setGeometry(100, 100, 900, 700)

        layout = QVBoxLayout()

        self.law_label = QLabel("EU Law or Directive:")
        layout.addWidget(self.law_label)

        self.law_input = QLineEdit()
        layout.addWidget(self.law_input)

        self.country_label = QLabel("Select Country:")
        layout.addWidget(self.country_label)

        self.country_dropdown = QComboBox()
        self.country_dropdown.addItems(["Germany", "France", "Italy", "Spain", 
            "Netherlands", "Poland", "Sweden", "Denmark", "Romania", "Other"
        ])
        layout.addWidget(self.country_dropdown)

        self.upload_button = QPushButton("Upload Contract Files")
        self.upload_button.clicked.connect(self.load_contracts)
        layout.addWidget(self.upload_button)

        self.contract_text = QTextEdit()
        layout.addWidget(self.contract_text)

        self.check_button = QPushButton("Check Compliance")
        self.check_button.clicked.connect(self.check_compliance)
        layout.addWidget(self.check_button)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def load_contracts(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Contract Files", "", "Text Files (*.pdf);;pdf Files (*.pdf);;All Files (*)"
        )
        # all_text = ""
        # for path in paths:
        #     try:
        #         with open(path, 'r', encoding='utf-8') as file:
        #             content = file.read()
        #             all_text += f"\n--- File: {path.split('/')[-1]} ---\n{content}\n"
        #     except Exception as e:
        #         QMessageBox.warning(self, "File Error", f"Could not read {path}: {e}")
        # self.contract_text.setText(all_text)

    def check_compliance(self):
        pass

    def display_highlighted(self, marked_text):
        self.result_text.clear()
        cursor = self.result_text.textCursor()

        i = 0
        while i < len(marked_text):
            if marked_text.startswith("[COMPLIANT]", i):
                i += len("[COMPLIANT]")
                end = marked_text.find("[/COMPLIANT]", i)
                self.insert_colored_text(cursor, marked_text[i:end], QColor("blue"))
                i = end + len("[/COMPLIANT]")
            elif marked_text.startswith("[NONCOMPLIANT]", i):
                i += len("[NONCOMPLIANT]")
                end = marked_text.find("[/NONCOMPLIANT]", i)
                self.insert_colored_text(cursor, marked_text[i:end], QColor("red"))
                i = end + len("[/NONCOMPLIANT]")
            else:
                end = i + 1
                while end < len(marked_text) and not marked_text.startswith("[", end):
                    end += 1
                self.insert_colored_text(cursor, marked_text[i:end], QColor("black"))
                i = end

    def insert_colored_text(self, cursor: QTextCursor, text: str, color: QColor):
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        cursor.insertText(text, fmt)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ComplianceChecker()
    window.show()
    sys.exit(app.exec_())
