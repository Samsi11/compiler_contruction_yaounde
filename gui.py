"""Desktop interface for the Yaounde Urban Language Analyzer."""

import tkinter as tk
from tkinter import ttk

from lexer import tokenize
from main import BASE_DIR, translate_to_plain_language
from parser import parse


BACKGROUND = "#f3f5f4"
SURFACE = "#ffffff"
INK = "#172b2b"
MUTED = "#617372"
ACCENT = "#006b60"
BORDER = "#dce5e2"


class AnalyzerWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Yaounde | Urban Language Analyzer")
        root.geometry("1040x740")
        root.minsize(760, 640)
        root.configure(bg=BACKGROUND)

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Tokens.Treeview", background=SURFACE, fieldbackground=SURFACE,
                        foreground=INK, rowheight=32, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Tokens.Treeview.Heading", background="#eaf0ee", foreground=INK,
                        relief="flat", font=("Segoe UI", 10, "bold"))
        style.map("Tokens.Treeview", background=[("selected", "#d7eee8")],
                  foreground=[("selected", INK)])
        style.configure("Examples.TCombobox", padding=7)

        container = tk.Frame(root, bg=BACKGROUND, padx=32, pady=24)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(2, weight=1)

        header = tk.Frame(container, bg=BACKGROUND)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 22))
        tk.Label(header, text="YAOUNDE  /  LANGUAGE TOOLS", bg=BACKGROUND,
                 fg=ACCENT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(header, text="Urban Language Analyzer", bg=BACKGROUND,
                 fg=INK, font=("Segoe UI Semibold", 25)).pack(anchor="w", pady=(4, 2))
        tk.Label(header, text="Explore how a phrase is tokenized, parsed, and interpreted.",
                 bg=BACKGROUND, fg=MUTED, font=("Segoe UI", 11)).pack(anchor="w")

        editor = tk.Frame(container, bg=SURFACE, padx=22, pady=20,
                          highlightbackground=BORDER, highlightthickness=1)
        editor.grid(row=1, column=0, sticky="nsew", padx=(0, 14), pady=(0, 14))
        editor.columnconfigure(0, weight=1)
        tk.Label(editor, text="PHRASE", bg=SURFACE, fg=MUTED,
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.input = tk.Text(editor, height=4, wrap="word", relief="flat", undo=True,
                             bg="#f6f9f8", fg=INK, insertbackground=INK,
                             font=("Segoe UI", 14), padx=12, pady=12,
                             highlightbackground=BORDER, highlightthickness=1)
        self.input.grid(row=1, column=0, sticky="ew", pady=(10, 18))
        self.input.bind("<Control-Return>", self.analyze_phrase)

        actions = tk.Frame(editor, bg=SURFACE)
        actions.grid(row=2, column=0, sticky="ew")
        tk.Button(actions, text="Analyze phrase", command=self.analyze_phrase,
                  bg=ACCENT, fg=SURFACE, activebackground="#00584f", activeforeground=SURFACE,
                  relief="flat", cursor="hand2", font=("Segoe UI", 10, "bold"),
                  padx=18, pady=10).pack(side="left")
        tk.Button(actions, text="Clear", command=self.clear, bg=SURFACE, fg=MUTED,
                  activebackground=BACKGROUND, relief="flat", cursor="hand2",
                  font=("Segoe UI", 10), padx=14, pady=10).pack(side="left", padx=8)
        tk.Label(editor, text="Ctrl+Enter to analyze", bg=SURFACE, fg=MUTED,
                 font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", pady=(15, 0))

        examples_panel = tk.Frame(container, bg=SURFACE, padx=22, pady=20,
                                  highlightbackground=BORDER, highlightthickness=1)
        examples_panel.grid(row=1, column=1, sticky="nsew", pady=(0, 14))
        examples_panel.columnconfigure(0, weight=1)
        tk.Label(examples_panel, text="EXAMPLES", bg=SURFACE, fg=MUTED,
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(examples_panel, text="Select a phrase to load it into the editor.",
                 bg=SURFACE, fg=MUTED, font=("Segoe UI", 10),
                 wraplength=280, justify="left").grid(row=1, column=0, sticky="w", pady=(8, 15))
        samples = [line.strip() for line in (BASE_DIR / "test_cases.txt").read_text(
            encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
        self.example = ttk.Combobox(examples_panel, values=samples, state="readonly",
                                    style="Examples.TCombobox", font=("Segoe UI", 10))
        self.example.grid(row=2, column=0, sticky="ew")
        self.example.bind("<<ComboboxSelected>>", self.load_example)

        results = tk.Frame(container, bg=SURFACE, padx=22, pady=20,
                           highlightbackground=BORDER, highlightthickness=1)
        results.grid(row=2, column=0, columnspan=2, sticky="nsew")
        results.columnconfigure(0, weight=1)
        results.rowconfigure(4, weight=1)
        tk.Label(results, text="ANALYSIS", bg=SURFACE, fg=MUTED,
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.status = tk.Label(results, text="Ready to analyze", bg=SURFACE, fg=INK,
                               font=("Segoe UI Semibold", 17), anchor="w")
        self.status.grid(row=1, column=0, sticky="ew", pady=(12, 2))
        self.detail = tk.Label(results, text="Choose an example or enter a phrase above.",
                               bg=SURFACE, fg=MUTED, font=("Segoe UI", 10), anchor="w",
                               justify="left", wraplength=880)
        self.detail.grid(row=2, column=0, sticky="ew")
        self.translation = tk.Label(results, text="", bg="#eaf4f0", fg=INK,
                                    font=("Segoe UI", 11), anchor="w", justify="left",
                                    wraplength=840, padx=12, pady=12)
        self.translation.grid(row=3, column=0, sticky="ew", pady=(16, 18))
        self.translation.grid_remove()

        token_frame = tk.Frame(results, bg=SURFACE)
        token_frame.grid(row=4, column=0, sticky="nsew")
        token_frame.columnconfigure(0, weight=1)
        token_frame.rowconfigure(1, weight=1)
        tk.Label(token_frame, text="TOKENS", bg=SURFACE, fg=MUTED,
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 9))
        self.tokens = ttk.Treeview(token_frame, columns=("position", "value", "kind"),
                                   show="headings", style="Tokens.Treeview", height=5)
        for column, title, width in (("position", "#", 55), ("value", "Word", 280),
                                     ("kind", "Token type", 180)):
            self.tokens.heading(column, text=title, anchor="w")
            self.tokens.column(column, width=width, minwidth=50, stretch=column != "position")
        self.tokens.grid(row=1, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(token_frame, orient="vertical", command=self.tokens.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tokens.configure(yscrollcommand=scrollbar.set)
        self.input.focus_set()

    def load_example(self, _event: tk.Event) -> None:
        self.input.delete("1.0", "end")
        self.input.insert("1.0", self.example.get())
        self.analyze_phrase()

    def clear(self) -> None:
        self.input.delete("1.0", "end")
        self.example.set("")
        self.status.configure(text="Ready to analyze", fg=INK)
        self.detail.configure(text="Choose an example or enter a phrase above.")
        self.translation.grid_remove()
        self.tokens.delete(*self.tokens.get_children())
        self.input.focus_set()

    def analyze_phrase(self, _event: tk.Event | None = None) -> str:
        sentence = self.input.get("1.0", "end-1c").strip()
        tokens = tokenize(sentence)
        result = parse(tokens)
        self.tokens.delete(*self.tokens.get_children())
        for position, token in enumerate(tokens, start=1):
            self.tokens.insert("", "end", values=(position, token.value, token.kind))
        self.status.configure(text="Accepted" if result.accepted else "Rejected",
                              fg=ACCENT if result.accepted else "#a44237")
        self.detail.configure(text=result.message)
        if result.accepted:
            self.translation.configure(text=f"Plain language   {translate_to_plain_language(sentence)}")
            self.translation.grid()
        else:
            self.translation.grid_remove()
        return "break"


def main() -> None:
    root = tk.Tk()
    AnalyzerWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()