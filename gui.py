import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit,
    QFileDialog, QComboBox, QListWidget, QMessageBox, QHBoxLayout, QMainWindow
)
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import networkx as nx
from rdflib import Graph, RDF
from collections import defaultdict

# ========= Helper for Graph Rendering =========
def local_name(uri):
    uri = str(uri)
    if "#" in uri:
        return uri.split("#")[-1]
    elif "/" in uri:
        return uri.split("/")[-1]
    return uri

class GraphViewerWindow(QMainWindow):
    def __init__(self, ttl_path, title):
        super().__init__()
        self.setWindowTitle(title)
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


# ========= Main Application =========
class GeminiComplianceChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ComplyVerify")
        self.setGeometry(100, 100, 950, 900)
        self.setStyle()

        self.law_files = []
        self.contract_files = []
        self.graph_windows = []

        layout = QVBoxLayout()

        layout.addWidget(self._make_label("Upload EU Law Documents (TXT):"))
        self.law_list = QListWidget()
        layout.addWidget(self.law_list)
        self.law_button = QPushButton("Upload Law Files")
        self.law_button.clicked.connect(self.load_law_files)
        layout.addWidget(self.law_button)

        layout.addWidget(self._make_label("Select Country:"))
        self.country_dropdown = QComboBox()
        self.country_dropdown.addItems([
            "Greece", "Germany", "France", "Italy", "Spain",
            "Netherlands", "Poland", "Sweden", "Denmark", "Romania", "Other"
        ])
        layout.addWidget(self.country_dropdown)

        layout.addWidget(self._make_label("Upload Contract Files (TXT):"))
        self.contract_list = QListWidget()
        layout.addWidget(self.contract_list)
        self.contract_button = QPushButton("Upload Contract Files")
        self.contract_button.clicked.connect(self.load_contract_files)
        layout.addWidget(self.contract_button)

        # Compliance Check
        button_layout = QHBoxLayout()
        self.check_button = QPushButton("Check Compliance")
        self.check_button.clicked.connect(self.check_compliance)
        button_layout.addWidget(self.check_button)
        layout.addLayout(button_layout)

        layout.addWidget(self._make_label("Compliance Report:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        # === Visualization of Law Files ===
        layout.addWidget(self._make_label("Visualization of Law Knowledge Graphs:"))
        law_vis_layout = QHBoxLayout()
        self.law_article_dropdown = QComboBox()
        self.law_article_dropdown.addItems([f"Article {i}" for i in range(1, 6)])
        law_vis_layout.addWidget(self.law_article_dropdown)
        self.law_vis_button = QPushButton("Visualize Graph")
        self.law_vis_button.clicked.connect(lambda: self.visualize_law_graph(self.law_article_dropdown.currentText()))
        law_vis_layout.addWidget(self.law_vis_button)
        layout.addLayout(law_vis_layout)

        # === Visualization of Policy File ===
        layout.addWidget(self._make_label("Visualization of Policy Knowledge Graphs:"))
        policy_vis_layout = QHBoxLayout()
        self.policy_section_dropdown = QComboBox()
        self.policy_section_dropdown.addItems([f"Section {i}" for i in range(1, 6)])
        policy_vis_layout.addWidget(self.policy_section_dropdown)
        self.policy_vis_button = QPushButton("Visualize Graph")
        self.policy_vis_button.clicked.connect(lambda: self.visualize_policy_graph(self.policy_section_dropdown.currentText()))
        policy_vis_layout.addWidget(self.policy_vis_button)
        layout.addLayout(policy_vis_layout)

        self.setLayout(layout)

    def _make_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        return label

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
        files, _ = QFileDialog.getOpenFileNames(self, "Select Policy File", "", "Documents (*.txt)")
        if files:
            self.contract_files = files
            self.contract_list.clear()
            self.contract_list.addItems([f.split("/")[-1] for f in files])

    def check_compliance(self):
        from SHACL_COMPLIANCE_TEST import get_compliance_test
        summary_file = get_compliance_test()
        with open(summary_file, "r") as file:
            content = file.read()
        self.result_text.setPlainText(content)

    def visualize_law_graph(self, article):
        article_path = './legal_compliance_hackathon/rdf_output_fixed/' + article.replace(' ', '_') + '.ttl'
        # try:
        graph_window = GraphViewerWindow(article_path, article)
        graph_window.show()
        self.graph_windows.append(graph_window)
        # except Exception as e:
            # QMessageBox.critical(self, "Error", f"Could not visualize graph:\n{e}")


    def visualize_policy_graph(self, section):
        section_path = './legal_compliance_hackathon/policy_rdf_output_fixed/' + section.replace(' ', '_') + '.ttl'
        # try:
        graph_window = GraphViewerWindow(section_path, section)
        graph_window.show()
        self.graph_windows.append(graph_window)
        # except Exception as e:
            # QMessageBox.critical(self, "Error", f"Could not visualize graph:\n{e}")


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeminiComplianceChecker()
    window.show()
    sys.exit(app.exec_())
