import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit,
    QFileDialog, QComboBox, QListWidget, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont, QColor, QPalette

from SHACL_COMPLIANCE_TEST import get_compliance_test

# Configure Gemini API
# genai.configure(api_key="YOUR_GOOGLE_API_KEY")  # Replace with your API key


from PyQt5.QtWidgets import QMainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import networkx as nx
from rdflib import Graph, RDF
from collections import defaultdict

def local_name(uri):
    uri = str(uri)
    if "#" in uri:
        return uri.split("#")[-1]
    elif "/" in uri:
        return uri.split("/")[-1]
    return uri

class GraphViewerWindow(QMainWindow):
    def __init__(self, ttl_path):
        super().__init__()
        self.setWindowTitle("Knowledge Graph")
        self.setGeometry(150, 150, 1000, 800)

        self.figure = plt.figure(figsize=(16, 10))
        self.canvas = FigureCanvas(self.figure)
        self.setCentralWidget(self.canvas)

        self.visualize_ttl(ttl_path)

    def visualize_ttl(self, ttl_path):
        g = Graph()
        g.parse(ttl_path, format="ttl")

        node_classes = defaultdict(lambda: "Unknown")
        for subj, pred, obj in g.triples((None, RDF.type, None)):
            node_classes[local_name(subj)] = local_name(obj)

        G = nx.DiGraph()
        for subj, pred, obj in g:
            subj_name = local_name(subj)
            pred_name = local_name(pred)
            obj_name = local_name(obj)

            if pred_name != "type":
                G.add_edge(subj_name, obj_name, label=pred_name)

        unique_classes = list(set(node_classes.values()))
        color_map = {cls: f"C{i % 10}" for i, cls in enumerate(unique_classes)}
        node_colors = [color_map.get(node_classes[n], "gray") for n in G.nodes]

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        pos = nx.spring_layout(G, k=0.9)

        nx.draw(
            G, pos, ax=ax,
            with_labels=True,
            node_color=node_colors,
            node_size=2500,
            font_size=9,
            font_color="black",
            edge_color="gray",
            linewidths=0.5,
            arrows=True
        )

        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)

        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label=cls,
                       markerfacecolor=color_map[cls], markersize=10)
            for cls in unique_classes
        ]
        ax.legend(handles=legend_elements, title="Node Types (RDF Classes)", loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=3)
        self.figure.tight_layout()
        self.canvas.draw()
# 

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
        layout.addWidget(self._make_label("Upload EU Law Documents (TXT):"))
        self.law_list = QListWidget()
        layout.addWidget(self.law_list)

        self.law_button = QPushButton("Upload Law Files")
        self.law_button.clicked.connect(self.load_law_files)
        layout.addWidget(self.law_button)

        # Country selection
        layout.addWidget(self._make_label("Select Country:"))
        self.country_dropdown = QComboBox()
        self.country_dropdown.addItems([
            "Greece", "Germany", "France", "Italy", "Spain",
            "Netherlands", "Poland", "Sweden", "Denmark", "Romania", "Other"
        ])
        layout.addWidget(self.country_dropdown)

        # Contract file section
        layout.addWidget(self._make_label("Upload Contract Files (TXT):"))
        self.contract_list = QListWidget()
        layout.addWidget(self.contract_list)

        self.contract_button = QPushButton("Upload Contract Files")
        self.contract_button.clicked.connect(self.load_contract_files)
        layout.addWidget(self.contract_button)

        # Action buttons
        button_layout = QHBoxLayout()

        self.check_button = QPushButton("Check Compliance")
        self.check_button.clicked.connect(self.check_compliance)
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
        files, _ = QFileDialog.getOpenFileNames(self, "Select EU Law Files", "", "Documents (*.txt)")
        if files:
            self.law_files = files
            self.law_list.clear()
            self.law_list.addItems([f.split("/")[-1] for f in files])

    def load_contract_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Contract Files", "", "Documents (*.txt)")
        if files:
            self.contract_files = files
            self.contract_list.clear()
            self.contract_list.addItems([f.split("/")[-1] for f in files])

    def check_compliance(self):
        summary_file = get_compliance_test()
        with open(summary_file, "r") as file:
            content = file.read()
        self.result_text.setPlainText(content)

    def visualize_graphs(self):
        QMessageBox.information(self, "Visualize Graphs", "Graph visualization feature coming soon!")
        
        # ttl_path = "output.ttl"  # Or wherever your generated TTL is saved
        # try:
        #     self.graph_window = GraphViewerWindow(ttl_path)
        #     self.graph_window.show()
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Could not visualize graph:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeminiComplianceChecker()
    window.show()
    sys.exit(app.exec_())
