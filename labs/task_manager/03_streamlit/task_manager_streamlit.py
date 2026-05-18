import streamlit as st
import uuid

st.set_page_config(page_title="Task Manager", page_icon="✅", layout="centered")
st.title("Task Manager - Streamlit")

# session_state persistă datele între reruns (reîncărcările script-ului)
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --- Formular adăugare ---
# clear_on_submit=True golește câmpurile după trimitere
with st.form("form_adaugare", clear_on_submit=True):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        text_nou = st.text_input("Task nou", placeholder="Descriere task...",
                                  label_visibility="collapsed")
    with col_btn:
        adaugat = st.form_submit_button("Adaugă", use_container_width=True)

if adaugat:
    if text_nou.strip():
        st.session_state.tasks.append({
            "id": str(uuid.uuid4()),  # ID unic pentru chei stabile la ștergere
            "text": text_nou.strip(),
            "done": False,
        })
    else:
        st.warning("Câmpul nu poate fi gol.")

st.divider()

# --- Lista de task-uri ---
if not st.session_state.tasks:
    st.info("Niciun task adăugat. Folosiți formularul de mai sus.")
else:
    to_delete = None  # Index task de șters (după iterație, nu în timpul ei)

    for i, task in enumerate(st.session_state.tasks):
        col_task, col_del = st.columns([10, 1])

        with col_task:
            # Cheia unică bazată pe ID asigură că starea nu se amestecă la ștergere
            done = st.checkbox(
                task["text"],
                value=task["done"],
                key=f"cb_{task['id']}"
            )
            st.session_state.tasks[i]["done"] = done

        with col_del:
            if st.button("✕", key=f"del_{task['id']}"):
                to_delete = i

    # Ștergerea se face după terminarea buclei
    if to_delete is not None:
        st.session_state.tasks.pop(to_delete)
        st.rerun()
