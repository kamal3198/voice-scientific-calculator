from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from memory_manager import MemoryManager


class JarvisGUI:
    def __init__(self, on_submit, on_listen, on_clear, on_plot) -> None:
        self.on_submit = on_submit
        self.on_listen = on_listen
        self.on_clear = on_clear
        self.on_plot = on_plot

        self.root = tk.Tk()
        self.root.title("Jarvis Voice Scientific Calculator")
        self.root.geometry("880x520")

        self._build_layout()

    def _build_layout(self) -> None:
        self.root.configure(bg="#0f1117")

        title = tk.Label(self.root, text="Jarvis Voice Scientific Calculator", fg="#e6e6e6", bg="#0f1117", font=("Segoe UI", 18, "bold"))
        title.pack(pady=10)

        top_frame = tk.Frame(self.root, bg="#0f1117")
        top_frame.pack(fill="x", padx=16)

        self.input_var = tk.StringVar()
        entry = tk.Entry(top_frame, textvariable=self.input_var, font=("Consolas", 14))
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        entry.bind("<Return>", lambda _e: self._submit())

        ttk.Button(top_frame, text="Compute", command=self._submit).pack(side="left", padx=4)
        ttk.Button(top_frame, text="Speak", command=self._listen).pack(side="left", padx=4)
        ttk.Button(top_frame, text="Plot", command=self._plot).pack(side="left", padx=4)
        ttk.Button(top_frame, text="Clear", command=self._clear).pack(side="left", padx=4)

        result_frame = tk.Frame(self.root, bg="#0f1117")
        result_frame.pack(fill="x", padx=16, pady=(10, 0))

        self.result_var = tk.StringVar(value="Result will appear here")
        result_label = tk.Label(result_frame, textvariable=self.result_var, fg="#9ef0ff", bg="#0f1117", font=("Consolas", 14))
        result_label.pack(anchor="w")

        history_frame = tk.Frame(self.root, bg="#0f1117")
        history_frame.pack(fill="both", expand=True, padx=16, pady=12)

        history_label = tk.Label(history_frame, text="History", fg="#c0c0c0", bg="#0f1117", font=("Segoe UI", 12, "bold"))
        history_label.pack(anchor="w")

        self.history_list = tk.Listbox(history_frame, font=("Consolas", 12))
        self.history_list.pack(fill="both", expand=True, pady=6)

    def _submit(self) -> None:
        text = self.input_var.get().strip()
        if text:
            result = self.on_submit(text)
            if result is not None:
                self.result_var.set(result)

    def _listen(self) -> None:
        result = self.on_listen()
        if result:
            self.input_var.set(result)

    def _clear(self) -> None:
        self.on_clear()
        self.history_list.delete(0, tk.END)
        self.result_var.set("History cleared")

    def _plot(self) -> None:
        text = self.input_var.get().strip()
        if text:
            message = self.on_plot(text)
            if message:
                self.result_var.set(message)

    def update_history(self, memory: MemoryManager) -> None:
        self.history_list.delete(0, tk.END)
        for item in memory.history():
            self.history_list.insert(tk.END, f"{item.query} = {item.result}")

    def start(self) -> None:
        self.root.mainloop()
