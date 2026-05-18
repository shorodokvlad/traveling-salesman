# Ghid PySide6 - Interfețe grafice moderne folosind Qt

## Ce este PySide6?

**PySide6** este binding-ul oficial Python pentru framework-ul **Qt6**, dezvoltat de Qt Group. Qt este unul dintre cele mai utilizate framework-uri GUI din industrie (KDE, VirtualBox, Autodesk Maya etc.).

PySide6 vs PyQt6:
- API practic identic.
- PySide6 are licență **LGPL** (mai permisivă).
- PySide6 este suportat oficial de Qt Group.
- Documentația oficială Qt folosește exemple PySide6.

---

## Instalare

```bash
# Creare mediu virtual (în folderul 02_pyside6/)
python -m venv .venv

# Activare Windows
.venv\Scripts\activate

# Activare macOS/Linux
source .venv/bin/activate

# Instalare PySide6
pip install PySide6

# Rulare aplicație
python task_manager_pyside.py
```

> **Notă:** PySide6 are ~100 MB. Instalarea poate dura câteva minute.

---

## Concepte cheie

### 1. Structura unei aplicații Qt

Orice aplicație PySide6 urmează același șablon:

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow

app = QApplication(sys.argv)   # un singur obiect per proces
window = QMainWindow()
window.show()
sys.exit(app.exec())           # pornește bucla de evenimente
```

`QApplication` gestionează resursele aplicației. `app.exec()` blochează execuția, similar cu `mainloop()` în tkinter.

### 2. Ierarhia de widget-uri

Widget-urile Qt se organizează într-un arbore părinte–copil:

```
QMainWindow
└── QWidget (central widget)
    └── QVBoxLayout
        ├── QHBoxLayout (input)
        │   ├── QLineEdit
        │   └── QPushButton
        └── QScrollArea
            └── QWidget (container)
                └── QVBoxLayout
                    ├── TaskRow (QFrame)
                    └── TaskRow (QFrame)
```

Când un widget-părinte este distrus, toți copiii sunt distruși automat.

### 3. Layout managers

Qt oferă layout-uri care gestionează automat redimensionarea:

| Layout | Comportament |
|--------|--------------|
| `QVBoxLayout` | Aranjare verticală |
| `QHBoxLayout` | Aranjare orizontală |
| `QGridLayout` | Grilă rânduri × coloane |
| `QFormLayout` | Perechi etichetă–câmp |

```python
layout = QVBoxLayout(parent_widget)  # layout legat de widget
layout.addWidget(buton)
layout.addLayout(alt_layout)         # layout-uri imbricate
```

### 4. Signals & Slots - mecanismul de evenimente

Acesta este conceptul central al Qt. Un **signal** este emis când se întâmplă ceva; un **slot** este o funcție conectată care răspunde.

```python
# Conectare: signal -> slot
buton.clicked.connect(self.add_task)        # fără argumente
checkbox.toggled.connect(self.on_toggle)    # transmite bool
line_edit.returnPressed.connect(self.add_task)
```

Câteva signals predefinite:
- `QPushButton.clicked` - emis la click
- `QCheckBox.toggled(bool)` - emis la schimbare stare, transmite noul state
- `QLineEdit.returnPressed` - emis la apăsarea Enter
- `QLineEdit.textChanged(str)` - emis la orice modificare a textului

Puteți crea propriile signals într-o clasă care moștenește `QObject`:
```python
from PySide6.QtCore import Signal

class MyWidget(QWidget):
    task_deleted = Signal(object)   # signal personalizat
```

### 5. Clase principale de widget-uri

| Widget | Echivalent tkinter | Rol |
|--------|--------------------|-----|
| `QLabel` | `tk.Label` | Afișare text |
| `QLineEdit` | `tk.Entry` | Câmp text o linie |
| `QPushButton` | `tk.Button` | Buton |
| `QCheckBox` | `tk.Checkbutton` | Casetă de selectare |
| `QFrame` | `tk.Frame` | Container cu bordură opțională |
| `QScrollArea` | - | Zonă cu scroll |
| `QMessageBox` | `messagebox` | Dialog mesaj |

### 6. StyleSheets - stilizare CSS

Qt suportă un subset de CSS pentru stilizare:

```python
label.setStyleSheet("color: gray; text-decoration: line-through; font-size: 14px;")
button.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 4px;")
```

---

## Structura aplicației Task Manager

```
TaskManagerApp (QMainWindow)
├── __init__()        - inițializare
├── _build_ui()       - construiește interfața Qt
├── add_task()        - validare + adăugare în self.tasks + refresh
├── _refresh()        - elimină toate TaskRow și le recreează
├── _toggle()         - actualizează task.done + refresh
└── _delete()         - elimină din self.tasks + refresh

TaskRow (QFrame)
├── __init__()        - construiește rândul: checkbox + label + buton
└── _update_style()   - aplică stilul CSS în funcție de task.done
```

### Widget personalizat: `TaskRow`

În PySide6 este natural să creați widget-uri personalizate prin subclasare:

```python
class TaskRow(QFrame):
    def __init__(self, task, on_toggle, on_delete):
        super().__init__()
        # construiește layout intern
        self.checkbox.toggled.connect(lambda checked: on_toggle(task, checked))
```

`TaskRow` primește callback-urile `on_toggle` și `on_delete` ca parametri, păstrând logica în `TaskManagerApp`.

### Curățarea layout-ului în `_refresh()`

```python
def _refresh(self):
    while self.tasks_layout.count():
        item = self.tasks_layout.takeAt(0)  # extrage (nu distruge)
        if item.widget():
            item.widget().deleteLater()      # planifică ștergerea
```

`deleteLater()` este metoda Qt recomandată - amână distrugerea widget-ului până după ce evenimentul curent (ex. click) se termină complet. Aceasta evită crash-uri când un widget se auto-distruge în timpul unui handler.

---

## Exerciții

### Exercițiul 1 - Buton „Șterge rezolvate"

Adăugați un `QPushButton("Șterge rezolvate")` lângă butonul „Adaugă".
La click, elimină toate task-urile cu `done=True` și apelează `_refresh()`.

**Indiciu:**
```python
btn_clear = QPushButton("Șterge rezolvate")
btn_clear.clicked.connect(self.delete_done)
input_layout.addWidget(btn_clear)

def delete_done(self):
    self.tasks = [t for t in self.tasks if not t.done]
    self._refresh()
```

---

### Exercițiul 2 - Bară de progres

Adăugați un `QProgressBar` sub zona de input care arată procentul de task-uri rezolvate.

**Indiciu:**
```python
from PySide6.QtWidgets import QProgressBar

# În _build_ui():
self.progress = QProgressBar()
self.progress.setRange(0, 100)
main_layout.addWidget(self.progress)

# La sfârșitul lui _refresh():
if self.tasks:
    done_count = sum(1 for t in self.tasks if t.done)
    self.progress.setValue(int(done_count / len(self.tasks) * 100))
else:
    self.progress.setValue(0)
```

---

### Exercițiul 3 - Sortare task-uri

Adăugați un `QComboBox` cu opțiunile: „Toate", „Active", „Rezolvate".
La schimbarea selecției, lista afișată se filtrează corespunzător.

**Indiciu:**
```python
from PySide6.QtWidgets import QComboBox

# În _build_ui():
self.filter_box = QComboBox()
self.filter_box.addItems(["Toate", "Active", "Rezolvate"])
self.filter_box.currentTextChanged.connect(lambda _: self._refresh())
input_layout.addWidget(self.filter_box)

# În _refresh(), înlocuiți `for task in self.tasks:` cu:
filtru = self.filter_box.currentText()
tasks_afisate = self.tasks
if filtru == "Active":
    tasks_afisate = [t for t in self.tasks if not t.done]
elif filtru == "Rezolvate":
    tasks_afisate = [t for t in self.tasks if t.done]

for task in tasks_afisate:
    ...
```
