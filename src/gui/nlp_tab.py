"""NLP tab: datasets, classifiers, comparisons."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QTextEdit,
)

from src.gui.plot_canvas import PlotCanvas
from src.gui.workers import WorkerThread
from src.nlp.classification import CLASSIFIERS, NLPParams, compare_classifiers, evaluate, study_max_features, study_ngram
from src.nlp.datasets import DATASET_LABELS, TextDataset, load_dataset
from src.system_info import get_machine_info


class NLPTab(QWidget):
    def __init__(self):
        super().__init__()
        self.dataset: TextDataset | None = None
        self._worker: WorkerThread | None = None
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        left = QVBoxLayout()
        root.addLayout(left, 0)

        self.dataset_combo = QComboBox()
        for key, label in DATASET_LABELS.items():
            self.dataset_combo.addItem(label, key)
        left.addWidget(QLabel("Dataset (English):"))
        left.addWidget(self.dataset_combo)

        self.btn_load = QPushButton("Load dataset")
        self.btn_train = QPushButton("Train & evaluate")
        self.btn_compare = QPushButton("Compare classifiers")
        self.btn_ngram = QPushButton("Study ngram_range")
        self.btn_features = QPushButton("Study max_features")
        left.addWidget(self.btn_load)
        left.addWidget(self.btn_train)
        left.addWidget(self.btn_compare)
        left.addWidget(self.btn_ngram)
        left.addWidget(self.btn_features)

        params_box = QGroupBox("Pipeline parameters")
        form = QFormLayout(params_box)
        self.clf_combo = QComboBox()
        self.clf_combo.addItems(list(CLASSIFIERS.keys()))
        form.addRow("Classifier:", self.clf_combo)

        self.ngram1 = QSpinBox()
        self.ngram1.setRange(1, 3)
        self.ngram1.setValue(1)
        self.ngram2 = QSpinBox()
        self.ngram2.setRange(1, 3)
        self.ngram2.setValue(2)
        ng_row = QHBoxLayout()
        ng_row.addWidget(self.ngram1)
        ng_row.addWidget(QLabel("to"))
        ng_row.addWidget(self.ngram2)
        form.addRow("ngram_range:", ng_row)

        self.max_feat = QSpinBox()
        self.max_feat.setRange(0, 200000)
        self.max_feat.setSpecialValueText("all")
        self.max_feat.setValue(10000)
        form.addRow("max_features (0=all):", self.max_feat)
        left.addWidget(params_box)

        self.info_label = QLabel("No dataset loaded.")
        self.info_label.setWordWrap(True)
        left.addWidget(self.info_label)

        self.report = QTextEdit()
        self.report.setReadOnly(True)
        left.addWidget(self.report)
        left.addStretch()

        self.canvas = PlotCanvas()
        root.addWidget(self.canvas, 1)

        self.btn_load.clicked.connect(self._load_dataset)
        self.btn_train.clicked.connect(self._train)
        self.btn_compare.clicked.connect(self._compare)
        self.btn_ngram.clicked.connect(self._study_ngram)
        self.btn_features.clicked.connect(self._study_features)

    def _params(self) -> NLPParams:
        mf = self.max_feat.value()
        return NLPParams(
            classifier=self.clf_combo.currentText(),
            ngram_range=(self.ngram1.value(), self.ngram2.value()),
            max_features=None if mf == 0 else mf,
        )

    def _set_busy(self, busy: bool):
        for btn in (self.btn_load, self.btn_train, self.btn_compare, self.btn_ngram, self.btn_features):
            btn.setEnabled(not busy)

    def _run_async(self, fn, on_ok):
        if self._worker and self._worker.isRunning():
            return
        self._set_busy(True)
        self._worker = WorkerThread(fn)
        self._worker.finished_ok.connect(on_ok)
        self._worker.failed.connect(lambda m: self.report.setPlainText(f"Error: {m}"))
        self._worker.finished.connect(lambda: self._set_busy(False))
        self._worker.start()

    def _load_dataset(self):
        key = self.dataset_combo.currentData()

        def job():
            return load_dataset(key)

        def done(ds: TextDataset):
            self.dataset = ds
            self.info_label.setText(
                f"{ds.name}\n{ds.description}\nTrain: {ds.n_train} | Test: {ds.n_test}\n"
                f"Classes: {', '.join(ds.target_names)}"
            )
            self.report.setPlainText("Dataset loaded. Run training or a study.")

        self._run_async(job, done)

    def _train(self):
        if not self.dataset:
            self.report.setPlainText("Load a dataset first.")
            return
        ds, params = self.dataset, self._params()

        def job():
            return evaluate(ds, params)

        def done(res):
            self.report.setPlainText(
                f"Accuracy: {res.accuracy:.4f}\nTrain time: {res.train_time_s:.2f} s\n\n"
                f"{res.report}\n\n--- Machine ---\n{get_machine_info().as_text()}"
            )
            self._plot_confusion(res.confusion, ds.target_names, f"{params.classifier} — acc {res.accuracy:.3f}")

        self._run_async(job, done)

    def _compare(self):
        if not self.dataset:
            return
        ds = self.dataset
        base = self._params()

        def job():
            return compare_classifiers(ds, base)

        def done(results):
            names = [r.params.classifier for r in results]
            accs = [r.accuracy for r in results]
            self._plot_bars(names, accs, "Classifier comparison", "Accuracy")
            lines = [
                f"{r.params.classifier}: acc={r.accuracy:.4f}, time={r.train_time_s:.2f}s"
                for r in results
            ]
            best = max(results, key=lambda r: r.accuracy)
            lines.append(f"\nBest: {best.params.classifier}")
            lines.append(get_machine_info().as_text())
            self.report.setPlainText("\n".join(lines))
            self._plot_confusion(
                best.confusion, ds.target_names, f"Best — {best.params.classifier}"
            )

        self._run_async(job, done)

    def _study_ngram(self):
        if not self.dataset:
            return
        ds = self.dataset
        base = self._params()

        def job():
            return study_ngram(ds, base=base)

        def done(results):
            labels = [str(r.params.ngram_range) for r in results]
            accs = [r.accuracy for r in results]
            self._plot_bars(labels, accs, "ngram_range study (SVM)", "ngram_range")
            self.report.setPlainText(
                "\n".join(f"ngram={r.params.ngram_range}: {r.accuracy:.4f}" for r in results)
            )

        self._run_async(job, done)

    def _study_features(self):
        if not self.dataset:
            return
        ds = self.dataset
        base = self._params()

        def job():
            return study_max_features(ds, base=base)

        def done(results):
            labels = [str(r.params.max_features or "all") for r in results]
            accs = [r.accuracy for r in results]
            self._plot_bars(labels, accs, "max_features study", "max_features")
            self.report.setPlainText(
                "\n".join(f"max_features={r.params.max_features}: {r.accuracy:.4f}" for r in results)
            )

        self._run_async(job, done)

    def _plot_bars(self, labels: list[str], values: list[float], title: str, xlabel: str):
        self.canvas.clear()
        ax = self.canvas.ax
        ax.bar(labels, values, color="steelblue", edgecolor="black")
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Accuracy")
        ax.set_xlabel(xlabel)
        ax.set_title(title)
        for i, v in enumerate(values):
            ax.text(i, v + 0.01, f"{v:.3f}", ha="center", fontsize=9)
        ax.tick_params(axis="x", rotation=25)
        self.canvas.refresh()

    def _plot_confusion(self, cm, labels: list[str], title: str):
        self.canvas.clear()
        ax = self.canvas.ax
        im = ax.imshow(cm, cmap="Blues")
        self.canvas.fig.colorbar(im, ax=ax, fraction=0.046)
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=35, ha="right")
        ax.set_yticklabels(labels)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_title(title)
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=8)
        self.canvas.refresh()
