"""TSP tab: algorithms, parameters, visualization."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QCheckBox,
    QTextEdit,
)

from src.gui.plot_canvas import PlotCanvas
from src.gui.workers import WorkerThread
from src.system_info import get_machine_info
from src.tsp.algorithms import (
    BKTParams,
    GAParams,
    HCParams,
    NNParams,
    SAParams,
    SOLVERS,
    TSPResult,
)
from src.tsp.benchmarks import run_tsp_benchmark
from src.tsp.utils import format_tour, generate_cities, load_matrix_file, matrix_from_coords, tour_cost


class TSPTab(QWidget):
    def __init__(self):
        super().__init__()
        self.cities: list[tuple[float, float]] = []
        self.dist_matrix: list[list[float]] = []
        self._worker: WorkerThread | None = None
        self._build_ui()
        self._generate_cities()

    def _build_ui(self):
        root = QHBoxLayout(self)

        controls = QVBoxLayout()
        root.addLayout(controls, 0)

        form = QFormLayout()
        self.spin_n = QSpinBox()
        self.spin_n.setRange(3, 80)
        self.spin_n.setValue(10)
        form.addRow("Number of cities:", self.spin_n)

        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 99999)
        self.seed_spin.setValue(42)
        form.addRow("Random seed:", self.seed_spin)
        controls.addLayout(form)

        btn_row = QHBoxLayout()
        self.btn_gen = QPushButton("Generate cities")
        self.btn_load = QPushButton("Load matrix file…")
        btn_row.addWidget(self.btn_gen)
        btn_row.addWidget(self.btn_load)
        controls.addLayout(btn_row)

        self.algo_combo = QComboBox()
        self.algo_combo.addItems(list(SOLVERS.keys()))
        controls.addWidget(QLabel("Algorithm:"))
        controls.addWidget(self.algo_combo)

        self.params_box = QGroupBox("Parameters")
        self.params_layout = QFormLayout(self.params_box)
        controls.addWidget(self.params_box)
        self._param_widgets: dict[str, QWidget] = {}
        self.algo_combo.currentTextChanged.connect(self._rebuild_params)
        self._rebuild_params(self.algo_combo.currentText())

        self.btn_run = QPushButton("Run algorithm")
        self.btn_compare = QPushButton("Compare all algorithms")
        self.btn_bench = QPushButton("Benchmark (time vs N)")
        controls.addWidget(self.btn_run)
        controls.addWidget(self.btn_compare)
        controls.addWidget(self.btn_bench)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(140)
        controls.addWidget(QLabel("Results:"))
        controls.addWidget(self.result_text)
        controls.addStretch()

        self.canvas = PlotCanvas()
        root.addWidget(self.canvas, 1)

        self.btn_gen.clicked.connect(self._generate_cities)
        self.btn_load.clicked.connect(self._load_file)
        self.btn_run.clicked.connect(self._run_single)
        self.btn_compare.clicked.connect(self._run_compare)
        self.btn_bench.clicked.connect(self._run_benchmark)

    def _clear_params(self):
        while self.params_layout.rowCount():
            self.params_layout.removeRow(0)
        self._param_widgets.clear()

    def _rebuild_params(self, algo: str):
        self._clear_params()
        if algo == "BKT":
            self._add_combo("mode", ["exhaustiv", "prima", "y_solutii", "timp"], 0)
            self._add_spin("y_solutions", 1, 1000, 5)
            self._add_float("time_limit_s", 1.0, 600.0, 30.0, 1)
        elif algo == "NN":
            self._add_spin("start", 0, 100, 0)
            self._add_check("multistart", False)
        elif algo == "HC":
            self._add_spin("max_iterations", 100, 100000, 5000)
            self._add_spin("restarts", 1, 200, 10)
        elif algo == "SA":
            self._add_float("initial_temp", 1.0, 50000.0, 1000.0, 0)
            self._add_float("cooling_rate", 0.8, 0.9999, 0.995, 4)
            self._add_float("min_temp", 0.0001, 10.0, 0.01, 4)
            self._add_spin("max_iterations", 100, 100000, 5000)
        elif algo == "GA":
            self._add_spin("population_size", 10, 500, 80)
            self._add_spin("generations", 10, 2000, 150)
            self._add_float("mutation_rate", 0.01, 1.0, 0.15, 2)
            self._add_float("crossover_rate", 0.1, 1.0, 0.85, 2)
            self._add_spin("elitism", 0, 20, 2)

    def _add_spin(self, name: str, lo: int, hi: int, val: int):
        w = QSpinBox()
        w.setRange(lo, hi)
        w.setValue(val)
        self.params_layout.addRow(name, w)
        self._param_widgets[name] = w

    def _add_float(self, name: str, lo: float, hi: float, val: float, decimals: int):
        w = QDoubleSpinBox()
        w.setRange(lo, hi)
        w.setDecimals(decimals)
        w.setValue(val)
        self.params_layout.addRow(name, w)
        self._param_widgets[name] = w

    def _add_combo(self, name: str, items: list[str], index: int):
        w = QComboBox()
        w.addItems(items)
        w.setCurrentIndex(index)
        self.params_layout.addRow(name, w)
        self._param_widgets[name] = w

    def _add_check(self, name: str, checked: bool):
        w = QCheckBox()
        w.setChecked(checked)
        self.params_layout.addRow(name, w)
        self._param_widgets[name] = w

    def _current_params(self, algo: str):
        w = self._param_widgets
        if algo == "BKT":
            return BKTParams(
                mode=w["mode"].currentText(),
                y_solutions=w["y_solutions"].value(),
                time_limit_s=w["time_limit_s"].value(),
            )
        if algo == "NN":
            return NNParams(start=w["start"].value(), multistart=w["multistart"].isChecked())
        if algo == "HC":
            return HCParams(
                max_iterations=w["max_iterations"].value(),
                restarts=w["restarts"].value(),
                seed=self.seed_spin.value(),
            )
        if algo == "SA":
            return SAParams(
                initial_temp=w["initial_temp"].value(),
                cooling_rate=w["cooling_rate"].value(),
                min_temp=w["min_temp"].value(),
                max_iterations=w["max_iterations"].value(),
                seed=self.seed_spin.value(),
            )
        if algo == "GA":
            return GAParams(
                population_size=w["population_size"].value(),
                generations=w["generations"].value(),
                mutation_rate=w["mutation_rate"].value(),
                crossover_rate=w["crossover_rate"].value(),
                elitism=w["elitism"].value(),
                seed=self.seed_spin.value(),
            )
        return None

    def _generate_cities(self):
        n = self.spin_n.value()
        self.cities = generate_cities(n, seed=self.seed_spin.value())
        self.dist_matrix = matrix_from_coords(self.cities)
        self._draw_path([], "Cities generated")
        self.result_text.setPlainText(f"Generated {n} cities.")

    def _load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open TSP matrix", "", "Text (*.txt);;All (*)")
        if not path:
            return
        n, matrix = load_matrix_file(path)
        self.dist_matrix = matrix
        self.cities = [(float(i), 0.0) for i in range(n)]
        self.spin_n.setValue(n)
        self._draw_path([], f"Loaded matrix N={n}")
        self.result_text.setPlainText(f"Loaded {path}")

    def _draw_path(self, path: list[int], title: str):
        self.canvas.clear()
        ax = self.canvas.ax
        if self.cities:
            xs = [c[0] for c in self.cities]
            ys = [c[1] for c in self.cities]
            ax.scatter(xs, ys, c="crimson", s=40, zorder=3)
            for i, (x, y) in enumerate(self.cities):
                ax.annotate(str(i), (x, y), fontsize=8, xytext=(3, 3), textcoords="offset points")
        if path:
            px = [self.cities[i][0] for i in path] + [self.cities[path[0]][0]]
            py = [self.cities[i][1] for i in path] + [self.cities[path[0]][1]]
            ax.plot(px, py, "b-", linewidth=1.5, zorder=2)
        ax.set_title(title)
        ax.set_aspect("equal", adjustable="datalim")
        self.canvas.refresh()

    def _set_busy(self, busy: bool):
        self.btn_run.setEnabled(not busy)
        self.btn_compare.setEnabled(not busy)
        self.btn_bench.setEnabled(not busy)

    def _run_async(self, fn, on_ok):
        if self._worker and self._worker.isRunning():
            return
        self._set_busy(True)
        self._worker = WorkerThread(fn)
        self._worker.finished_ok.connect(on_ok)
        self._worker.failed.connect(self._on_error)
        self._worker.finished.connect(lambda: self._set_busy(False))
        self._worker.start()

    def _on_error(self, msg: str):
        self.result_text.setPlainText(f"Error: {msg}")

    def _run_single(self):
        if not self.dist_matrix:
            return
        algo = self.algo_combo.currentText()
        if algo == "BKT" and len(self.dist_matrix) > 12:
            self.result_text.setPlainText("BKT is limited to N ≤ 12 in the GUI.")
            return
        params = self._current_params(algo)
        matrix = self.dist_matrix

        def job():
            return algo, SOLVERS[algo](matrix, params)

        def done(payload):
            algo_name, result = payload
            self._show_result(algo_name, result)

        self._run_async(job, done)

    def _show_result(self, algo: str, result: TSPResult):
        machine = get_machine_info().as_text()
        text = (
            f"Algorithm: {algo}\n"
            f"Cost: {result.cost:.4f}\n"
            f"Time: {result.elapsed_s:.4f} s\n"
            f"Tour: {format_tour(result.path)}\n"
            f"Meta: {result.meta}\n\n"
            f"--- Machine ---\n{machine}"
        )
        self.result_text.setPlainText(text)
        self._draw_path(result.path, f"{algo} — cost {result.cost:.2f}")

    def _run_compare(self):
        if not self.dist_matrix:
            return
        matrix = self.dist_matrix
        n = len(matrix)

        def job():
            rows = []
            for algo, fn in SOLVERS.items():
                if algo == "BKT" and n > 12:
                    continue
                params = None
                if algo == "NN":
                    params = NNParams(multistart=True)
                elif algo == "BKT":
                    params = BKTParams(mode="exhaustiv" if n <= 10 else "timp", time_limit_s=5.0)
                r = fn(matrix, params) if params else fn(matrix)
                rows.append((algo, r))
            return rows

        def done(rows):
            self.canvas.clear()
            ax = self.canvas.ax
            names = [a for a, _ in rows]
            costs = [r.cost for _, r in rows]
            times = [r.elapsed_s for _, r in rows]
            x = range(len(names))
            ax2 = ax.twinx()
            ax.bar([i - 0.2 for i in x], costs, width=0.4, label="Cost", color="steelblue")
            ax2.bar([i + 0.2 for i in x], times, width=0.4, label="Time (s)", color="coral")
            ax.set_xticks(list(x))
            ax.set_xticklabels(names)
            ax.set_ylabel("Tour cost")
            ax2.set_ylabel("Time (s)")
            ax.set_title("Algorithm comparison")
            self.canvas.fig.legend(loc="upper right")
            self.canvas.refresh()

            lines = [f"{a}: cost={r.cost:.2f}, time={r.elapsed_s:.4f}s" for a, r in rows]
            lines.append("\n" + get_machine_info().as_text())
            self.result_text.setPlainText("\n".join(lines))
            best = min(rows, key=lambda t: t[1].cost)
            self._draw_path(best[1].path, f"Best: {best[0]}")

        self._run_async(job, done)

    def _run_benchmark(self):
        def job():
            return run_tsp_benchmark(sizes=[5, 7, 8, 10, 12, 15, 20], repeats=1, seed=self.seed_spin.value())

        def done(rows):
            self.canvas.clear()
            ax = self.canvas.ax
            algos = sorted({r.algorithm for r in rows})
            for algo in algos:
                subset = [r for r in rows if r.algorithm == algo]
                ns = [r.n for r in subset]
                ts = [r.time_s for r in subset]
                ax.plot(ns, ts, marker="o", label=algo)
            ax.set_xlabel("N (cities)")
            ax.set_ylabel("Time (s)")
            ax.set_yscale("log")
            ax.set_title("Runtime vs problem size")
            ax.legend()
            self.canvas.refresh()
            self.result_text.setPlainText(
                f"Benchmark on {get_machine_info().hostname}\n"
                + "\n".join(f"N={r.n} {r.algorithm}: cost={r.cost:.1f} t={r.time_s:.4f}s" for r in rows)
            )

        self._run_async(job, done)
