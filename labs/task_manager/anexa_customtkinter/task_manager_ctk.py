import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

ctk.set_appearance_mode("System")    # "Light", "Dark", "System"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class Task:
    def __init__(self, text: str):
        self.text = text
        self.done = False


class TaskManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager - CustomTkinter")
        self.geometry("520x520")
        self.tasks: list[Task] = []
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Input
        frame_input = ctk.CTkFrame(self)
        frame_input.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")
        frame_input.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(frame_input, placeholder_text="Descriere task...")
        self.entry.grid(row=0, column=0, padx=(10, 6), pady=10, sticky="ew")
        self.entry.bind("<Return>", lambda _: self.add_task())

        ctk.CTkButton(frame_input, text="Adaugă", width=100,
                      command=self.add_task).grid(row=0, column=1, padx=(0, 10), pady=10)

        # CTkScrollableFrame - scrollbar integrat, fără configurare manuală
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Task-uri")
        self.scroll_frame.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def add_task(self):
        text = self.entry.get().strip()
        if not text:
            messagebox.showwarning("Atenție", "Câmpul nu poate fi gol.")
            return
        self.tasks.append(Task(text))
        self.entry.delete(0, "end")
        self._refresh()

    def _refresh(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        for task in self.tasks:
            self._render_row(task)

    def _render_row(self, task: Task):
        row = ctk.CTkFrame(self.scroll_frame, corner_radius=6)
        row.pack(fill="x", pady=3, padx=4)
        row.grid_columnconfigure(1, weight=1)

        # tk.BooleanVar - CustomTkinter se bazează pe tkinter pentru variabile
        var = tk.BooleanVar(value=task.done)
        ctk.CTkCheckBox(
            row, text="", variable=var, width=24,
            command=lambda t=task, v=var: self._toggle(t, v)
        ).grid(row=0, column=0, padx=(8, 4), pady=6)

        color = "gray" if task.done else None
        ctk.CTkLabel(row, text=task.text, text_color=color, anchor="w").grid(
            row=0, column=1, sticky="ew", padx=4
        )

        ctk.CTkButton(
            row, text="✕", width=30, height=28,
            fg_color="transparent", hover_color="#FF4444",
            text_color=("gray10", "gray90"),
            command=lambda t=task: self._delete(t)
        ).grid(row=0, column=2, padx=(4, 8), pady=6)

    def _toggle(self, task: Task, var: tk.BooleanVar):
        task.done = var.get()
        self._refresh()

    def _delete(self, task: Task):
        self.tasks.remove(task)
        self._refresh()


if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()
