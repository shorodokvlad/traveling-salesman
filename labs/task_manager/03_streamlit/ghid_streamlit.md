# Ghid Streamlit - Interfețe web în Python

## Ce este Streamlit?

**Streamlit** este o bibliotecă Python care transformă un script Python obișnuit într-o aplicație web interactivă, fără cunoștințe de HTML, CSS sau JavaScript. Aplicația rulează ca un server local și se accesează din browser.

Este folosit în mod curent pentru:
- Dashboarduri de date și vizualizări.
- Prototipuri rapide de aplicații AI/ML.
- Interfețe web pentru instrumente interne.

> **Important:** Spre deosebire de tkinter și PySide6, Streamlit rulează în **browser**, nu ca o fereastră desktop. Modelul de execuție este diferit față de GUI clasice.

---

## Instalare și rulare

```bash
# Creare mediu virtual (în folderul 03_streamlit/)
python -m venv .venv

# Activare Windows
.venv\Scripts\activate

# Activare macOS/Linux
source .venv/bin/activate

# Instalare Streamlit
pip install streamlit

# Rulare aplicație - NU python direct, ci prin streamlit
streamlit run task_manager_streamlit.py
```

Streamlit deschide automat browserul la `http://localhost:8501`.

---

## Conceptul fundamental: modelul de execuție „rerun"

Acesta este cel mai important lucru de înțeles despre Streamlit și diferă complet față de alte tehnologii GUI clasice.

### Cum funcționează o aplicație tkinter / PySide6

```
Pornire → build_ui() o singură dată → mainloop() rulează permanent
                                            ↓ eveniment (click)
                                       callback() actualizează UI
```

### Cum funcționează o aplicație Streamlit

```
Pornire → script rulează de sus în jos → pagina se afișează
              ↓ orice interacțiune a utilizatorului (click buton, 
              ↓ bifat checkbox, modificat text input)
          script-ul se REÎNCARCĂ COMPLET de la capăt
              ↓
          pagina se afișează din nou cu noul state
```

**La fiecare interacțiune, tot script-ul Python se execută din nou.** Aceasta înseamnă că variabilele obișnuite (`tasks = []`) sunt resetate la fiecare rerun - se pierd datele.

### `st.session_state` - soluția pentru persistența datelor

`st.session_state` este un dicționar special care **persistă între reruns**. Orice date pe care vreți să le păstrați trebuie stocate acolo:

```python
# Inițializare (se execută doar la primul run, nu la reruns)
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Citire
for task in st.session_state.tasks:
    ...

# Modificare
st.session_state.tasks.append({"text": "Nou task", "done": False})
```

### `st.rerun()` - forțarea unui rerun manual

De obicei, Streamlit declanșează rerun automat la interacțiuni. Uneori aveți nevoie să forțați manual un rerun (de exemplu, după ștergerea unui element din sesiune):

```python
if buton_sters:
    st.session_state.tasks.pop(index)
    st.rerun()   # forțează reîncărcarea imediată
```

---

## Widget-uri Streamlit

Streamlit oferă widget-uri simple, apelate ca funcții:

```python
st.title("Titlu pagină")
st.write("Text oarecare sau orice tip Python")
st.markdown("Text **bold**, *italic*, ~~tăiat~~")
st.divider()           # linie separator
st.info("Mesaj info")
st.warning("Atenție!")
st.error("Eroare!")
```

Widget-uri interactive (returnează valoarea curentă):

```python
text = st.text_input("Etichetă", placeholder="Hint text")
clicked = st.button("Click me")
checked = st.checkbox("Opțiune", value=False)
option = st.selectbox("Alege", ["A", "B", "C"])
```

### Layout cu coloane

```python
col1, col2, col3 = st.columns([4, 4, 1])  # proporții relative
with col1:
    st.write("Conținut coloana 1")
with col2:
    st.write("Conținut coloana 2")
```

### Formulare - grupare widget-uri cu submit explicit

Fără formulare, orice modificare a unui widget declanșează un rerun. Formularele grupează mai multe widget-uri și declanșează un singur rerun la apăsarea butonului de submit:

```python
with st.form("nume_form", clear_on_submit=True):
    text = st.text_input("Câmp text")
    submit = st.form_submit_button("Trimite")

# Procesare DUPĂ form (important: în afara blocului with)
if submit and text.strip():
    st.session_state.tasks.append(...)
```

`clear_on_submit=True` resetează câmpurile formularului după submit - util pentru câmpurile de adăugare.

---

## Structura aplicației Task Manager

```
task_manager_streamlit.py (script, nu clasă)
│
├── Inițializare session_state        - o singură dată la pornire
├── Formular adăugare (st.form)       - input + buton submit
├── Procesare adăugare                - dacă submit, adaugă în session_state
├── Separator vizual (st.divider)
└── Buclă afișare task-uri
    ├── checkbox (bifat = done)
    ├── buton ✕ (marchează pentru ștergere)
    └── ștergere + st.rerun()
```

### Chei unice pentru widget-uri

Fiecare widget interactiv din Streamlit are o cheie (`key`) care identifică starea sa în `session_state`. Când task-urile se șterg și ordinea se schimbă, cheile bazate pe indice (`key="cb_0"`, `key="cb_1"`) pot asocia stări greșite cu task-uri noi.

Soluția din aplicație: fiecare task primește un **ID unic** (`uuid4`) la creare, iar cheile widget-urilor folosesc acest ID:

```python
# La adăugare:
{"id": str(uuid.uuid4()), "text": "...", "done": False}

# La afișare:
st.checkbox(task["text"], key=f"cb_{task['id']}")   # cheie stabilă
st.button("✕",            key=f"del_{task['id']}")  # cheie stabilă
```

### De ce ștergeerea se face dupa buclă, nu în timpul ei

```python
to_delete = None

for i, task in enumerate(st.session_state.tasks):
    if st.button("✕", key=f"del_{task['id']}"):
        to_delete = i          # nu ștergem imediat!

if to_delete is not None:
    st.session_state.tasks.pop(to_delete)
    st.rerun()
```

Modificarea unei liste în timp ce iterăm prin ea produce erori sau comportament imprevizibil. Se salvează indexul și se șterge după terminarea buclei.

---

## Exerciții

### Exercițiul 1 - Statistici în sidebar

Adăugați un sidebar (`st.sidebar`) care afișează:
- Numărul total de task-uri
- Numărul de task-uri rezolvate
- Un `st.progress` cu procentul de completare

**Indiciu:**
```python
total = len(st.session_state.tasks)
done = sum(1 for t in st.session_state.tasks if t["done"])

with st.sidebar:
    st.header("Statistici")
    st.metric("Total", total)
    st.metric("Rezolvate", done)
    if total > 0:
        st.progress(done / total)
```

---

### Exercițiul 2 - Filtrare task-uri

Adăugați trei butoane de filtrare: **„Toate"**, **„Active"**, **„Rezolvate"**.
Lista afișată se actualizează în funcție de filtrul selectat.

**Indiciu:** Salvați filtrul activ în `session_state`:
```python
if "filter" not in st.session_state:
    st.session_state.filter = "Toate"

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Toate"):
        st.session_state.filter = "Toate"
# ... similar pentru celelalte

tasks_afisate = st.session_state.tasks
if st.session_state.filter == "Active":
    tasks_afisate = [t for t in st.session_state.tasks if not t["done"]]
elif st.session_state.filter == "Rezolvate":
    tasks_afisate = [t for t in st.session_state.tasks if t["done"]]
```

---

### Exercițiul 3 - Export JSON

Adăugați un buton **„Descarcă task-uri"** care exportă lista curentă ca fișier JSON.

**Indiciu:**
```python
import json

if st.session_state.tasks:
    json_data = json.dumps(st.session_state.tasks, ensure_ascii=False, indent=2)
    st.download_button(
        label="⬇ Descarcă tasks.json",
        data=json_data,
        file_name="tasks.json",
        mime="application/json"
    )
```
