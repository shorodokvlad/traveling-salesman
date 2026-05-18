# Interfețe grafice în Python

## Scopul laboratorului

Construiți aceeași aplicație - un **Task Manager** simplu - folosind trei stack-uri grafice diferite. La finalul laboratorului veți putea evalua care tehnologie se potrivește cel mai bine proiectului vostru de echipă.

**Durata:** \~2 ore | **Echipe:** 2–3 persoane

---

## Aplicația Task Manager

Funcționalități identice în toate variantele:

| Funcționalitate  | Descriere                                           |
| ---------------- | --------------------------------------------------- |
| Adăugare task    | Câmp text + buton „Adaugă" (sau Enter)              |
| Marcare rezolvat | Checkbox - bifat = task rezolvat (text tăiat / gri) |
| Ștergere task    | Buton ✕ per task                                    |
| Validare         | Câmpul nu poate fi gol                              |

---

## Structura proiectului

```
task_manager/
├── README.md                          ← acest fișier
│
├── 01_tkinter/
│   ├── ghid_tkinter.md               ← citiți înainte de cod
│   └── task_manager_tk.py
│
├── 02_pyside6/
│   ├── ghid_pyside6.md
│   └── task_manager_pyside.py
│
├── 03_streamlit/
│   ├── ghid_streamlit.md
│   └── task_manager_streamlit.py
│
└── anexa_customtkinter/               ← opțional, dacă rămâne timp
    ├── ghid_customtkinter.md
    └── task_manager_ctk.py
```

---

## Pregătire mediu de lucru în VSCode

### 1. Deschideți folderul în VSCode

```
File → Open Folder → selectați folderul task_manager/
```

### 2. Creați un mediu virtual separat pentru fiecare subfolder

Fiecare activitate are propriul mediu virtual, deoarece dependențele diferă.

Deschideți un terminal în VSCode (`Ctrl+`` `) și navigați în subfolderul dorit:

```bash
cd 01_tkinter
python -m venv .venv
```

**Activare mediu virtual:**

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Windows (Command Prompt):

```cmd
.venv\Scripts\activate.bat
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Când mediul este activ, promptul terminalului va afișa `(.venv)` la început.

### 3. Instalați dependențele

| Folder                 | Comandă                     |
| ---------------------- | --------------------------- |
| `01_tkinter/`          | (nicio instalare necesară)  |
| `02_pyside6/`          | `pip install PySide6`       |
| `03_streamlit/`        | `pip install streamlit`     |
| `anexa_customtkinter/` | `pip install customtkinter` |

Dependințele vor fi salvate în fișier `requirements.txt`.

### 4. Selectați interpretorul Python în VSCode

Utilizati terminalul din VSC pentru a interacționa cu interpretorul de Python dorit.

Alternativ, `Ctrl+Shift+P` → `Python: Select Interpreter` → alegeți interpretorul din `.venv` al folderului curent.

---

## Cum rulați fiecare variantă a stack-ului grafic

| Variantă      | Comandă                                   |
| ------------- | ----------------------------------------- |
| tkinter       | `python task_manager_tk.py`               |
| PySide6       | `python task_manager_pyside.py`           |
| Streamlit     | `streamlit run task_manager_streamlit.py` |
| CustomTkinter | `python task_manager_ctk.py`              |

> **Streamlit** este diferit: nu deschide o fereastră, ci pornește un server local. Browserul se deschide automat la `http://localhost:8501`. Opriți serverul cu `Ctrl+C` în terminal.

---

## ## Flux de lucru recomandat pentru fiecare activitate

1. **Citiți ghidul** (`ghid_*.md`) - concepte cheie, 5–10 minute.
2. **Rulați aplicația** ca atare și testați toate funcționalitățile.
3. **Citiți codul** cu ghidul deschis alături - identificați unde apar conceptele descrise.
4. **Faceți exercițiile** - modificați codul, testați, discutați în echipă.

---

## Comparație tehnologii

| Criteriu                  | tkinter                              | PySide6                         | Streamlit                          |
| ------------------------- | ------------------------------------ | ------------------------------- | ---------------------------------- |
| Instalare                 | Inclusă în Python                    | `pip install PySide6` (~100 MB) | `pip install streamlit`            |
| Tip interfață             | Desktop nativ                        | Desktop nativ                   | Web (browser)                      |
| Aspect vizual             | Minimal, retro                       | Profesional, modern             | Modern, web                        |
| Curbă de învățare         | Mică                                 | Medie                           | Mică (model diferit)               |
| Widget-uri disponibile    | Puține, de bază                      | Foarte multe                    | Suficiente pentru date/formulare   |
| Potrivit pentru           | Utilitare simple, prototipuri rapide | Aplicații desktop complete      | Dashboarduri, AI/ML, formulare web |
| Comunitate / documentație | Mare                                 | Foarte mare (Qt ecosystem)      | Mare și în creștere                |

### Alegere tehnologie

**Alegeți tkinter** dacă:

- Aplicația este un utilitar simplu fără cerințe vizuale.
- Vreți zero dependențe externe.

**Alegeți PySide6** dacă:

- Aplicația desktop trebuie să arate profesional.
- Aveți nevoie de widget-uri avansate (tabele, diagrame, arbori, dialoguri complexe).
- Echipa poate aloca timp pentru a învăța conceptul de signals & slots.

**Alegeți Streamlit** dacă:

- Aplicația afișează date, grafice, sau rezultate de modele.
- Vreți să fie accesibilă din browser (inclusiv de pe alte mașini din rețea).
- Viteza de prototipare primează față de controlul complet al UI-ului.
