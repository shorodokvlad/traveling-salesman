# Anexă: CustomTkinter - tkinter cu aspect modern

## Ce este CustomTkinter?

`customtkinter` este o bibliotecă construită **peste tkinter** care înlocuiește widget-urile clasice cu variante moderne, cu suport pentru teme Light/Dark și culori personalizabile.

Puncte cheie:
- Aceeași logică ca tkinter - dacă tkinter este o tehnologie cunoscută, migrarea durează minute.
- Widget-urile CTk au un aspect vizual contemporan.
- Suportă teme Light, Dark și System (urmărește tema OS).
- **Nu** înlocuiește complet tkinter - variabilele (`BooleanVar`, `StringVar`) rămân din `tkinter`.

Când să alegeți față de tkinter pur:
- Când aspectul vizual contează, dar nu vreți complexitatea Qt-ului.
- Aplicații desktop simple cu UI plăcut fără efort suplimentar.

---

## Instalare

```bash
# Creare mediu virtual (în folderul anexa_customtkinter/)
python -m venv .venv

# Activare Windows
.venv\Scripts\activate

# Activare macOS/Linux
source .venv/bin/activate

pip install customtkinter

python task_manager_ctk.py
```

---

## Diferențe față de tkinter standard

### Fereastra principală

```python
# tkinter
root = tk.Tk()

# CustomTkinter
app = ctk.CTk()   # subclasă a Tk
```

### Widget-uri prefixate cu CTk

Fiecare widget tkinter are un echivalent CTk:

| tkinter | CustomTkinter |
|---------|---------------|
| `tk.Frame` | `ctk.CTkFrame` |
| `tk.Label` | `ctk.CTkLabel` |
| `tk.Entry` | `ctk.CTkEntry` |
| `tk.Button` | `ctk.CTkButton` |
| `tk.Checkbutton` | `ctk.CTkCheckBox` |
| - | `ctk.CTkScrollableFrame` |

### Variabilele rămân cele din tkinter

`CTkCheckBox` folosește `tk.BooleanVar`, nu `ctk.BooleanVar`:

```python
import tkinter as tk
import customtkinter as ctk

var = tk.BooleanVar(value=False)         # din tkinter
ctk.CTkCheckBox(parent, variable=var)    # CTk widget
```

### Setarea temei globale

```python
ctk.set_appearance_mode("System")   # "Light", "Dark", "System"
ctk.set_default_color_theme("blue") # "blue", "green", "dark-blue"
```

Tema se setează o singură dată, înainte de crearea oricărui widget.

### `CTkScrollableFrame` - scrollbar integrat

Cel mai util widget exclusiv CTk: un Frame cu scrollbar vertical integrat, fără configurare manuală:

```python
scroll_frame = ctk.CTkScrollableFrame(parent, label_text="Lista mea")
scroll_frame.pack(fill="both", expand=True)

# Adăugați widget-uri direct în scroll_frame
ctk.CTkLabel(scroll_frame, text="Element").pack()
```

---

## Ce rămâne identic față de tkinter

- Sistemele de layout: `pack()`, `grid()`, `place()`.
- `bind()` pentru evenimente de tastatură/mouse.
- Logica aplicației (clase, metode, patternul refresh).
- `mainloop()` pentru bucla de evenimente.
- Variabilele `BooleanVar`, `StringVar` etc.

---

## Cod comparat: tkinter vs CustomTkinter

**tkinter:**
```python
root = tk.Tk()
root.title("App")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill="x")

entry = tk.Entry(frame, font=("Arial", 12))
entry.pack(side="left", fill="x", expand=True)

tk.Button(frame, text="Adaugă").pack(side="left")

root.mainloop()
```

**CustomTkinter (cod aproape identic):**
```python
app = ctk.CTk()
app.title("App")

frame = ctk.CTkFrame(app)
frame.pack(fill="x", padx=10, pady=10)
frame.grid_columnconfigure(0, weight=1)

entry = ctk.CTkEntry(frame, placeholder_text="Hint...")
entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

ctk.CTkButton(frame, text="Adaugă", width=100).grid(row=0, column=1)

app.mainloop()
```

Diferențele sunt minime: prefixul `CTk`, câțiva parametri în plus (`placeholder_text`, `corner_radius`), și folosirea `grid()` în loc de `pack()` pentru layout mai controlat.

---

## Exercițiu opțional

Modificați `task_manager_ctk.py` pentru a adăuga un `CTkOptionMenu` cu opțiunile `"Light"`, `"Dark"`, `"System"` care schimbă tema aplicației la run-time:

```python
def schimba_tema(self, alegere: str):
    ctk.set_appearance_mode(alegere)
```

Adăugați widget-ul în `frame_input`, alături de butonul „Adaugă".
