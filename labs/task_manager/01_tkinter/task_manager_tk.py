import tkinter as tk
from tkinter import messagebox


class Task:
    def __init__(self, text: str):
        self.text = text
        self.done = False


class TaskManagerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Task Manager - tkinter")
        self.root.geometry("520x500")
        self.root.resizable(True, True)
        self.tasks: list[Task] = []
        self._build_ui()

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Zona de input
        frame_input = tk.Frame(self.root, pady=8, padx=10)
        frame_input.grid(row=0, column=0, sticky="ew")
        frame_input.columnconfigure(0, weight=1)

        self.entry = tk.Entry(frame_input, font=("Arial", 12))
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.entry.bind("<Return>", lambda _: self.add_task())

        tk.Button(frame_input, text="Adaugă", width=10,
                  command=self.add_task).grid(row=0, column=1)

        # Container lista de task-uri
        frame_lista = tk.Frame(self.root, padx=10)
        frame_lista.grid(row=1, column=0, sticky="nsew")
        frame_lista.columnconfigure(0, weight=1)

        self.frame_tasks = tk.Frame(frame_lista)
        self.frame_tasks.pack(fill=tk.BOTH, expand=True)

    def add_task(self):
        text = self.entry.get().strip()
        if not text:
            messagebox.showwarning("Atenție", "Câmpul nu poate fi gol.")
            return
        self.tasks.append(Task(text))
        self.entry.delete(0, tk.END)
        self._refresh()

    def _refresh(self):
        # Distruge toate widget-urile din container și le recreează
        for widget in self.frame_tasks.winfo_children():
            widget.destroy()
        for task in self.tasks:
            self._render_row(task)

    def _render_row(self, task: Task):
        row = tk.Frame(self.frame_tasks, pady=4)
        row.pack(fill=tk.X)

        var = tk.BooleanVar(value=task.done)
        tk.Checkbutton(
            row, variable=var,
            command=lambda t=task, v=var: self._toggle(t, v)
        ).pack(side=tk.LEFT)

        font = ("Arial", 11, "overstrike") if task.done else ("Arial", 11)
        color = "gray" if task.done else "black"
        tk.Label(row, text=task.text, font=font, fg=color, anchor="w").pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

        tk.Button(
            row, text="✕", fg="red", bd=0, cursor="hand2",
            command=lambda t=task: self._delete(t)
        ).pack(side=tk.RIGHT)

    def _toggle(self, task: Task, var: tk.BooleanVar):
        task.done = var.get()
        self._refresh()

    def _delete(self, task: Task):
        self.tasks.remove(task)
        self._refresh()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
