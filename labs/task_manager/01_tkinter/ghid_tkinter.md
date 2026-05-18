# Ghid tkinter - Interfețe grafice native în Python

## Ce este tkinter?

`tkinter` este biblioteca standard Python pentru crearea de interfețe grafice desktop. Nu necesită instalare suplimentară - vine inclusă în orice distribuție Python. Învelește biblioteca grafică **Tk/Tcl**, disponibilă pe Windows, macOS și Linux.

Avantaje:
- Zero dependențe externe.
- Disponibil imediat, fără `pip install`.
- Potrivit pentru aplicații simple și medii.

Limitări:
- Aspect vizual de bază (nu urmărește stilul nativ al sistemului de operare).
- Componente UI limitate față de Qt sau alte framework-uri.

---

## Concepte cheie

### 1. Fereastra principală (`Tk`)

Orice aplicație tkinter pornește cu un obiect `Tk`, care reprezintă fereastra principală:

```python
root = tk.Tk()
root.title("Titlu fereastra")
root.geometry("500x400")  # lățime x înălțime
root.mainloop()           # pornește bucla de evenimente
```

`mainloop()` blochează execuția și procesează evenimentele (click, tastatură etc.) până la închiderea ferestrei.

### 2. Widget-uri

Widget-urile sunt elementele de interfață - butoane, câmpuri text, etichete etc.:

| Widget | Rol |
|--------|-----|
| `tk.Label` | Afișează text sau imagine |
| `tk.Entry` | Câmp de introducere text pe o linie |
| `tk.Button` | Buton cu acțiune |
| `tk.Checkbutton` | Casetă de selectare (checkbox) |
| `tk.Frame` | Container transparent pentru gruparea widget-urilor |

### 3. Gestiunea layout-ului

tkinter oferă trei sisteme de poziționare:

| Manager | Descriere |
|---------|-----------|
| `pack()` | Aranjare secvențială (sus, jos, stânga, dreapta) |
| `grid()` | Grilă de rânduri și coloane - mai flexibil |
| `place()` | Coordonate absolute - evitați pentru UI-uri dinamice |

**Regulă importantă:** nu amestecați `pack()` și `grid()` în același container.

### 4. Variabile tkinter

tkinter folosește clase speciale pentru a lega date de widget-uri:

```python
var = tk.BooleanVar(value=False)   # pentru Checkbutton
text = tk.StringVar(value="")      # pentru Entry/Label
```

Acestea notifică automat widget-urile atunci când valoarea se schimbă.

### 5. Evenimente și comenzi

Fiecare widget poate răspunde la interacțiuni:

```python
# Simplu - buton cu funcție
tk.Button(root, text="Click", command=functia_mea)

# Binding - orice eveniment pe un widget
entry.bind("<Return>", lambda event: functia_mea())
```

---

## Structura aplicației Task Manager

```
TaskManagerApp
├── __init__()         - inițializare, creare listă tasks
├── _build_ui()        - construiește interfața (apelat o singură dată)
├── add_task()         - citește Entry, adaugă Task în listă, refresh
├── _refresh()         - distruge toate rândurile și le recreează
├── _render_row(task)  - creează un Frame cu checkbox, label, buton ✕
├── _toggle(task, var) - actualizează task.done, refresh
└── _delete(task)      - elimină task din listă, refresh
```

### Patternul „refresh complet"

Aplicația folosește un pattern simplu: la orice modificare a datelor, toată lista de widget-uri se distruge și se recreează:

```python
def _refresh(self):
    for widget in self.frame_tasks.winfo_children():
        widget.destroy()      # elimină widget-urile vechi
    for task in self.tasks:
        self._render_row(task) # recreează din zero
```

Acest pattern este simplu de înțeles și de depanat. Dezavantaj: nu este eficient pentru liste foarte lungi (sute de elemente).

### Captarea variabilelor în lambda

Un aspect subtil în `_render_row`:

```python
# GREȘIT - toate lambda-urile vor folosi ultimul `task` din buclă
command=lambda: self._delete(task)

# CORECT - valoarea lui `task` este capturată la momentul creării
command=lambda t=task: self._delete(t)
```

---

## Instalare și rulare

tkinter este inclus în Python. Nu necesită instalare suplimentară.

```bash
# Verificare disponibilitate
python -c "import tkinter; print(tkinter.TkVersion)"

# Rulare aplicație
python task_manager_tk.py
```

### Creare mediu virtual (recomandat pentru consistență cu celelalte variante)

```bash
# În folderul 01_tkinter/
python -m venv .venv

# Activare Windows
.venv\Scripts\activate

# Activare macOS/Linux
source .venv/bin/activate

# tkinter nu necesita pip install
python task_manager_tk.py
```

---

## Exerciții

### Exercițiul 1 - Contor de task-uri

Adăugați un `tk.Label` în partea de jos a ferestrei care afișează:
`"3 task-uri | 1 rezolvat"` - actualizat automat la orice modificare.

**Indiciu:** Apelați o metodă `_update_counter()` la sfârșitul fiecărui `_refresh()`. Folosiți un `StringVar` legat la Label.

---

### Exercițiul 2 - Ștergere task-uri rezolvate

Adăugați un buton **„Șterge rezolvate"** care elimină toate task-urile cu `done=True` dintr-o singură acțiune.

**Indiciu:** `self.tasks = [t for t in self.tasks if not t.done]`

---

### Exercițiul 3 - Persistență în fișier JSON

La pornire, aplicația încarcă task-urile dintr-un fișier `tasks.json` (dacă există).
La orice modificare, salvează automat lista în același fișier.

**Indiciu:**
```python
import json

def _load(self):
    try:
        with open("tasks.json") as f:
            for item in json.load(f):
                t = Task(item["text"])
                t.done = item["done"]
                self.tasks.append(t)
    except FileNotFoundError:
        pass

def _save(self):
    with open("tasks.json", "w") as f:
        json.dump([{"text": t.text, "done": t.done} for t in self.tasks], f)
```

Apelați `_save()` la sfârșitul lui `add_task()`, `_toggle()` și `_delete()`.
