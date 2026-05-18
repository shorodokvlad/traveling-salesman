"""PySide6 application entry point."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget

from src.gui.nlp_tab import NLPTab
from src.gui.tsp_tab import TSPTab
from src.system_info import get_machine_info


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IA — TSP & NLP Laboratory")
        self.resize(1200, 780)

        tabs = QTabWidget()
        tabs.addTab(TSPTab(), "TSP (BKT, NN, HC, SA, GA)")
        tabs.addTab(NLPTab(), "NLP Classification")

        about = QWidget()
        layout = QVBoxLayout(about)
        info = get_machine_info()
        layout.addWidget(
            QLabel(
                "<h3>Runtime environment</h3>"
                f"<pre>{info.as_text()}</pre>"
                "<p>All experiment outputs include machine metadata for reproducibility.</p>"
                "<p><b>TSP:</b> Backtracking (BKT), Nearest Neighbor, Hill Climbing, "
                "Simulated Annealing, Genetic Algorithm.</p>"
                "<p><b>NLP:</b> TF-IDF pipeline with Naive Bayes, SVM, Logistic Regression, "
                "Random Forest on English datasets.</p>"
            )
        )
        layout.addStretch()
        tabs.addTab(about, "Machine info")

        self.setCentralWidget(tabs)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
