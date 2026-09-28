"""Desktop interface for the Yaounde Urban Language Analyzer."""

import tkinter as tk
from tkinter import ttk

from analysis import analyze_corpus, format_report
from corpus import find_entry, test_entries
from grammar import (
    EPSILON,
    FIRST,
    FOLLOW,
    LL1_GRAMMAR,
    NO_LEFT_RECURSION_GRAMMAR,
    RAW_GRAMMAR,
    TABLE,
    format_grammar,
    format_sets,
)
from lexer import tokenize
from parser import TreeNode, parse

BACKGROUND = "#f3f5f4"
SURFACE = "#ffffff"
INK = "#172b2b"
MUTED = "#617372"
ACCENT = "#006b60"
BORDER = "#dce5e2"
REJECT = "#a44237"
ACCEPT_BG = "#e3f3ee"
REJECT_BG = "#fbe9e6"
ERROR_ROW = "#f6c9c3"
NOTE_BG = "#eef2f1"

LANG_COLORS = {"EN": "#e6eef8", "FR": "#f8e8f0", "PDG": "#fbf0da", "SLG": "#e5f4e3", "UNK": "#eeeeee"}
LANG_NAMES = {"EN": "English", "FR": "French", "PDG": "Pidgin", "SLG": "Slang", "UNK": "Unknown"}

MONO = ("Consolas", 10)
UI = "Segoe UI"


def flat_button(parent: tk.Misc, text: str, command, primary: bool = False,
                compact: bool = False) -> tk.Button:
    if primary:
        return tk.Button(parent, text=text, command=command, bg=ACCENT, fg=SURFACE,
                         activebackground="#00584f", activeforeground=SURFACE, relief="flat",
                         cursor="hand2", font=(UI, 10, "bold"), padx=18, pady=10)
    return tk.Button(parent, text=text, command=command, bg=SURFACE, fg=ACCENT,
                     activebackground=BACKGROUND, relief="flat", cursor="hand2",
                     font=(UI, 10), padx=10 if compact else 14, pady=3 if compact else 8,
                     highlightbackground=BORDER,
                     highlightthickness=1)


def card(parent: tk.Misc) -> tk.Frame:
    return tk.Frame(parent, bg=SURFACE, padx=22, pady=18,
                    highlightbackground=BORDER, highlightthickness=1)


def scrolled_tree(parent: tk.Misc, horizontal: bool = False, **options) -> tuple[tk.Frame, ttk.Treeview]:
    frame = tk.Frame(parent, bg=SURFACE)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    tree = ttk.Treeview(frame, **options)
    tree.grid(row=0, column=0, sticky="nsew")
    vertical = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    vertical.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=vertical.set)
    if horizontal:
        bar = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        bar.grid(row=1, column=0, sticky="ew")
        tree.configure(xscrollcommand=bar.set)
    return frame, tree


def is_empty(node: TreeNode) -> bool:
    """True if this node derives nothing (an epsilon expansion)."""
    if node.token is not None:
        return False
    if node.symbol == EPSILON:
        return True
    return all(is_empty(child) for child in node.children)


def visible_children(node: TreeNode, hide_helpers: bool):
    """Children to display; helper nodes (names ending in ') are spliced away."""
    for child in node.children:
        if hide_helpers and is_empty(child):
            continue
        if hide_helpers and child.symbol.endswith("'"):
            yield from visible_children(child, hide_helpers)
        else:
            yield child


class AnalyzerWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.entries = test_entries()
        self.last_result = None
        root.title("Yaoundé | Urban Language Analyzer")
        width = min(1120, root.winfo_screenwidth() - 80)
        height = min(840, root.winfo_screenheight() - 100)
        root.geometry(f"{width}x{height}+30+10")
        root.minsize(900, 640)
        root.configure(bg=BACKGROUND)
        self._configure_styles()

        container = tk.Frame(root, bg=BACKGROUND, padx=30, pady=14)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=2, minsize=440)
        container.columnconfigure(1, weight=3)
        container.rowconfigure(1, weight=1)

        self._build_header(container)
        left = tk.Frame(container, bg=BACKGROUND)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 14))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1)
        self._build_editor(left)
        self._build_examples(left)
        self._build_results(container, left)
        self.input.focus_set()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        for name, font in (("Tokens", (UI, 10)), ("Trace", MONO), ("Tree", MONO)):
            style.configure(f"{name}.Treeview", background=SURFACE, fieldbackground=SURFACE,
                            foreground=INK, rowheight=28, borderwidth=0, font=font)
            style.configure(f"{name}.Treeview.Heading", background="#eaf0ee", foreground=INK,
                            relief="flat", font=(UI, 10, "bold"))
            style.map(f"{name}.Treeview", background=[("selected", "#d7eee8")],
                      foreground=[("selected", INK)])
        style.configure("Examples.TCombobox", padding=7)
        style.configure("TNotebook", background=SURFACE, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 8), font=(UI, 10))
        style.map("TNotebook.Tab", background=[("selected", SURFACE)],
                  foreground=[("selected", ACCENT)], expand=[("selected", (0, 0, 0, 0))])

    def _build_header(self, container: tk.Frame) -> None:
        header = tk.Frame(container, bg=BACKGROUND)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)
        titles = tk.Frame(header, bg=BACKGROUND)
        titles.grid(row=0, column=0, sticky="w")
        tk.Label(titles, text="YAOUNDÉ  /  LANGUAGE TOOLS", bg=BACKGROUND, fg=ACCENT,
                 font=(UI, 10, "bold")).pack(anchor="w")
        tk.Label(titles, text="Urban Language Analyzer", bg=BACKGROUND, fg=INK,
                 font=("Segoe UI Semibold", 21)).pack(anchor="w", pady=(2, 0))
        tools = tk.Frame(header, bg=BACKGROUND)
        tools.grid(row=0, column=1, sticky="ne")
        for text, command in (("All results", self.show_results),
                              ("Statistics", self.show_statistics),
                              ("Grammar & LL(1) table", self.show_grammar)):
            flat_button(tools, text, command).pack(side="left", padx=(8, 0))

    def _build_editor(self, container: tk.Frame) -> None:
        editor = card(container)
        editor.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        editor.columnconfigure(0, weight=1)
        tk.Label(editor, text="PHRASE", bg=SURFACE, fg=MUTED,
                 font=(UI, 10, "bold")).grid(row=0, column=0, sticky="w")
        self.input = tk.Text(editor, height=2, wrap="word", relief="flat", undo=True,
                             bg="#f6f9f8", fg=INK, insertbackground=INK, font=(UI, 14),
                             padx=12, pady=10, highlightbackground=BORDER, highlightthickness=1)
        self.input.grid(row=1, column=0, sticky="ew", pady=(8, 12))
        self.input.bind("<Control-Return>", self.analyze_phrase)
        actions = tk.Frame(editor, bg=SURFACE)
        actions.grid(row=2, column=0, sticky="ew")
        flat_button(actions, "Analyze phrase", self.analyze_phrase, primary=True).pack(side="left")
        tk.Button(actions, text="Clear", command=self.clear, bg=SURFACE, fg=MUTED,
                  activebackground=BACKGROUND, relief="flat", cursor="hand2",
                  font=(UI, 10), padx=14, pady=10).pack(side="left", padx=8)
        tk.Label(actions, text="Ctrl+Enter to analyze", bg=SURFACE, fg=MUTED,
                 font=(UI, 9)).pack(side="right")

    def _build_examples(self, container: tk.Frame) -> None:
        panel = card(container)
        panel.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        panel.columnconfigure(0, weight=1)
        tk.Label(panel, text="50 COLLECTED UTTERANCES", bg=SURFACE, fg=MUTED,
                 font=(UI, 10, "bold")).grid(row=0, column=0, sticky="w")
        nav = tk.Frame(panel, bg=SURFACE)
        nav.grid(row=0, column=1, sticky="e")
        flat_button(nav, "‹ Prev", lambda: self.step_example(-1), compact=True).pack(side="left")
        flat_button(nav, "Next ›", lambda: self.step_example(1), compact=True).pack(side="left", padx=(6, 0))
        self.example = ttk.Combobox(panel, values=[f"{e.id}   {e.text}" for e in self.entries],
                                    state="readonly", style="Examples.TCombobox", font=(UI, 10))
        self.example.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.example.bind("<<ComboboxSelected>>", self.load_example)

    def _build_results(self, container: tk.Frame, left: tk.Frame) -> None:
        results = card(left)
        results.grid(row=2, column=0, sticky="nsew")
        results.columnconfigure(0, weight=1)
        self.status = tk.Label(results, text="Ready to analyze", bg=SURFACE, fg=INK,
                               font=("Segoe UI Semibold", 17), anchor="w")
        self.status.grid(row=1, column=0, sticky="w")
        self.detail = tk.Label(results, text="Choose an example or type a phrase above.",
                               bg=SURFACE, fg=MUTED, font=(UI, 10), anchor="w",
                               justify="left", wraplength=390)
        self.detail.grid(row=2, column=0, sticky="ew", pady=(0, 2))
        self.context = tk.Label(results, bg=NOTE_BG, fg=INK, font=(UI, 10), anchor="w",
                                justify="left", wraplength=390, padx=12, pady=6)
        self.context.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        self.translation = tk.Label(results, bg="#eaf4f0", fg=INK, font=(UI, 11), anchor="w",
                                    justify="left", wraplength=390, padx=12, pady=6)
        self.translation.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        self.context.grid_remove()
        self.translation.grid_remove()

        right = card(container)
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)
        self.tabs = ttk.Notebook(right)
        self.tabs.grid(row=0, column=0, sticky="nsew")
        self._build_tokens_tab()
        self._build_tree_tab()
        self._build_trace_tab()

    def _build_tokens_tab(self) -> None:
        tab = tk.Frame(self.tabs, bg=SURFACE, pady=10)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        legend = tk.Frame(tab, bg=SURFACE)
        legend.grid(row=0, column=0, sticky="w", pady=(0, 8))
        for lang in ("EN", "FR", "PDG", "SLG", "UNK"):
            tk.Label(legend, text=LANG_NAMES[lang], bg=LANG_COLORS[lang], fg=INK, font=(UI, 9),
                     padx=6, pady=2).pack(side="left", padx=(0, 4))
        tk.Label(legend, text="Stopped here", bg=ERROR_ROW, fg=INK, font=(UI, 9),
                 padx=6, pady=2).pack(side="left")
        frame, self.tokens = scrolled_tree(tab, columns=("position", "value", "kind", "lang"),
                                           show="headings", style="Tokens.Treeview", height=6)
        frame.grid(row=1, column=0, sticky="nsew")
        for column, title, width in (("position", "#", 40), ("value", "Word", 150),
                                     ("kind", "Token type", 100), ("lang", "Language", 90)):
            self.tokens.heading(column, text=title, anchor="w")
            self.tokens.column(column, width=width, minwidth=50, stretch=column != "position")
        for lang, color in LANG_COLORS.items():
            self.tokens.tag_configure(lang, background=color)
        self.tokens.tag_configure("error", background=ERROR_ROW)
        self.tabs.add(tab, text="Tokens")

    def _build_tree_tab(self) -> None:
        tab = tk.Frame(self.tabs, bg=SURFACE, pady=10)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        self.hide_helpers = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text="Hide helper nodes (names ending in ') and empty nodes",
                        variable=self.hide_helpers,
                        command=lambda: self._fill_tree(self.last_result)).grid(
            row=0, column=0, sticky="w", pady=(0, 8))
        frame, self.tree = scrolled_tree(tab, show="tree", style="Tree.Treeview", height=6)
        frame.grid(row=1, column=0, sticky="nsew")
        self.tabs.add(tab, text="Parse tree")

    def _build_trace_tab(self) -> None:
        tab = tk.Frame(self.tabs, bg=SURFACE, pady=10)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        tk.Label(tab, text="Each row is one step of the LL(1) algorithm. The top of the stack "
                 "is on the right.", bg=SURFACE, fg=MUTED, font=(UI, 9)).grid(
            row=0, column=0, sticky="w", pady=(0, 8))
        frame, self.trace = scrolled_tree(tab, horizontal=True, columns=("step", "stack", "input", "action"),
                                          show="headings", style="Trace.Treeview", height=6)
        frame.grid(row=1, column=0, sticky="nsew")
        for column, title, width in (("step", "Step", 45), ("stack", "Stack", 235),
                                     ("input", "Remaining input", 135), ("action", "Action", 165)):
            self.trace.heading(column, text=title, anchor="w")
            self.trace.column(column, width=width, minwidth=50, stretch=False)
        self.tabs.add(tab, text="Parse trace")

    # ---- actions -------------------------------------------------------

    def load_example(self, _event: tk.Event | None = None) -> None:
        index = self.example.current()
        if index < 0:
            return
        self.input.delete("1.0", "end")
        self.input.insert("1.0", self.entries[index].text)
        self.analyze_phrase()

    def step_example(self, delta: int) -> None:
        index = self.example.current()
        self.example.current(0 if index < 0 else (index + delta) % len(self.entries))
        self.load_example()

    def clear(self) -> None:
        self.input.delete("1.0", "end")
        self.example.set("")
        self.last_result = None
        self.status.configure(text="Ready to analyze", fg=INK)
        self.detail.configure(text="Choose an example or type a phrase above.")
        self.context.grid_remove()
        self.translation.grid_remove()
        for tree in (self.tokens, self.tree, self.trace):
            tree.delete(*tree.get_children())
        self.input.focus_set()

    def analyze_phrase(self, _event: tk.Event | None = None) -> str:
        sentence = self.input.get("1.0", "end-1c").strip()
        tokens = tokenize(sentence)
        result = parse(tokens)
        self.last_result = result
        entry = find_entry(sentence)

        self.status.configure(text="Accepted" if result.accepted else "Rejected",
                              fg=ACCENT if result.accepted else REJECT)
        self.detail.configure(text=result.message)
        self._show_context(entry, result.accepted)

        self.tokens.delete(*self.tokens.get_children())
        for index, token in enumerate(tokens):
            tag = "error" if index == result.error_index else token.lang
            self.tokens.insert("", "end", iid=str(index), tags=(tag,),
                               values=(index + 1, token.value, token.kind, LANG_NAMES.get(token.lang, token.lang)))

        self._fill_tree(result)
        self.trace.delete(*self.trace.get_children())
        for number, step in enumerate(result.trace, start=1):
            self.trace.insert("", "end", values=(number, " ".join(step.stack),
                                                 " ".join(step.remaining_input), step.action))
        return "break"

    def _show_context(self, entry, accepted: bool) -> None:
        if entry is None:
            self.context.grid_remove()
            self.translation.grid_remove()
            return
        verdict = "ACCEPT" if accepted else "REJECT"
        if entry.expected in ("ACCEPT", "REJECT"):
            relation = "matches" if verdict == entry.expected else "DIFFERS from"
            text = f"{entry.id}  ·  {entry.topic}  ·  {entry.contributor}  ·  {relation} the expected {entry.expected}"
            if entry.note:
                text += f"\n{'Why: ' if entry.expected == 'REJECT' else 'Note: '}{entry.note}"
        else:
            text = f"Entry {entry.id} was excluded from testing: {entry.note}"
        self.context.configure(text=text)
        self.context.grid()
        if entry.gloss:
            self.translation.configure(text=f"Contributor's translation   {entry.gloss}")
            self.translation.grid()
        else:
            self.translation.grid_remove()

    def _fill_tree(self, result) -> None:
        self.tree.delete(*self.tree.get_children())
        if result is None:
            return
        if result.tree is None:
            self.tree.insert("", "end", text="No parse tree: the utterance was rejected.")
            return
        self._insert_node("", result.tree, self.hide_helpers.get())

    def _insert_node(self, parent: str, node: TreeNode, hide_helpers: bool) -> None:
        label = node.symbol
        if node.token is not None:
            label = f'{node.symbol}   "{node.token.value}"   ({LANG_NAMES.get(node.token.lang, node.token.lang)})'
        item = self.tree.insert(parent, "end", text=label, open=True)
        for child in visible_children(node, hide_helpers):
            self._insert_node(item, child, hide_helpers)

    # ---- secondary windows --------------------------------------------

    def _toplevel(self, title: str, size: str) -> tk.Toplevel:
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(size)
        window.configure(bg=BACKGROUND)
        return window

    def show_results(self) -> None:
        window = self._toplevel("Results for every collected utterance",
                                f"{min(1500, self.root.winfo_screenwidth() - 40)}x680")
        rows = []
        for index, entry in enumerate(self.entries):
            result = parse(tokenize(entry.text))
            rows.append((index, entry, result))
        accepted = sum(r.accepted for _, _, r in rows)
        tk.Label(window, text=f"{accepted} accepted, {len(rows) - accepted} rejected "
                 f"of {len(rows)} collected utterances. Double-click a row to open it.",
                 bg=BACKGROUND, fg=INK, font=(UI, 11), anchor="w").pack(fill="x", padx=20, pady=(16, 8))
        frame, tree = scrolled_tree(window, columns=("id", "topic", "text", "result", "note"),
                                    show="headings", style="Tokens.Treeview")
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        for column, title, width in (("id", "ID", 55), ("topic", "Topic", 110),
                                     ("text", "Utterance", 330), ("result", "Result", 90),
                                     ("note", "Why / note", 900)):
            tree.heading(column, text=title, anchor="w")
            tree.column(column, width=width, minwidth=50, stretch=column == "note")
        tree.tag_configure("accept", background=ACCEPT_BG)
        tree.tag_configure("reject", background=REJECT_BG)
        for index, entry, result in rows:
            tree.insert("", "end", iid=str(index), tags=("accept" if result.accepted else "reject",),
                        values=(entry.id, entry.topic, entry.text,
                                "Accepted" if result.accepted else "Rejected", entry.note))

        def open_selected(_event: tk.Event) -> None:
            selected = tree.selection()
            if selected:
                self.example.current(int(selected[0]))
                self.load_example()
                self.root.lift()

        tree.bind("<Double-1>", open_selected)

    def show_statistics(self) -> None:
        window = self._toplevel("Token frequency and variation", "820x760")
        text = tk.Text(window, wrap="none", bg=SURFACE, fg=INK, font=MONO, padx=18, pady=16,
                       relief="flat")
        text.pack(fill="both", expand=True, padx=20, pady=20)
        text.insert("1.0", format_report(analyze_corpus(self.entries)))
        text.configure(state="disabled")

    def show_grammar(self) -> None:
        window = self._toplevel("Grammar and LL(1) parsing table", "1240x720")
        notebook = ttk.Notebook(window)
        notebook.pack(fill="both", expand=True, padx=20, pady=20)

        def text_tab(title: str, caption: str, body: str) -> None:
            tab = tk.Frame(notebook, bg=SURFACE, padx=16, pady=14)
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(1, weight=1)
            tk.Label(tab, text=caption, bg=SURFACE, fg=MUTED, font=(UI, 10), wraplength=1100,
                     justify="left", anchor="w").grid(row=0, column=0, sticky="ew", pady=(0, 10))
            text = tk.Text(tab, wrap="none", bg="#f6f9f8", fg=INK, font=MONO, padx=14, pady=12,
                           relief="flat")
            text.grid(row=1, column=0, sticky="nsew")
            text.insert("1.0", body)
            text.configure(state="disabled")
            notebook.add(tab, text=title)

        text_tab("1  Raw CFG",
                 "The grammar as designed for the collected utterances. S is a whole utterance, "
                 "UTT is clauses joined by a conjunction, CLAUSE is one clause, NP a noun phrase, "
                 "VP a verb phrase, PP a preposition phrase. Words such as NOUN, VERB or CONJ are "
                 "token types produced by the lexer. ε means 'nothing'.",
                 format_grammar(RAW_GRAMMAR))
        text_tab("2  Left recursion removed",
                 "UTT, ADJP and NBAR used to call themselves on the left (UTT -> UTT CONJ CLAUSE). "
                 "A top-down parser would loop forever on that, so each is rewritten with a helper "
                 "nonterminal ending in ' (UTT', ADJP', NBAR') that handles the repetition.",
                 format_grammar(NO_LEFT_RECURSION_GRAMMAR))
        text_tab("3  Left factored",
                 "CLAUSE, COMP and NBAR had rules starting with the same symbols (for example "
                 "CLAUSE -> NP PRED and CLAUSE -> NP), so one token of lookahead could not choose "
                 "between them. The shared start is pulled out and the difference goes into a new "
                 "helper (CLAUSE', COMP', NBAR''). This is the grammar the parser uses.",
                 format_grammar(LL1_GRAMMAR))
        text_tab("4  FIRST and FOLLOW",
                 "FIRST(X) is the set of token types that can start X. FOLLOW(X) is the set of token "
                 "types that can come right after X. ε in FIRST means X can be empty. The parsing "
                 "table is built from these two sets.",
                 "FIRST sets\n" + format_sets(FIRST) + "\n\nFOLLOW sets\n" + format_sets(FOLLOW))

        table_tab = tk.Frame(notebook, bg=SURFACE, padx=16, pady=14)
        table_tab.columnconfigure(0, weight=1)
        table_tab.rowconfigure(1, weight=1)
        tk.Label(table_tab, text="Row: what the parser is trying to build. Column: the next token type it "
                 "sees. Cell: the rule to use. An empty cell means a syntax error. Scroll right for "
                 "more columns.", bg=SURFACE, fg=MUTED, font=(UI, 10), wraplength=1100,
                 justify="left", anchor="w").grid(row=0, column=0, sticky="ew", pady=(0, 10))
        terminals = sorted({t for (_, t) in TABLE if t != "$"}) + ["$"]
        columns = ["nt"] + terminals
        frame, table = scrolled_tree(table_tab, horizontal=True, columns=columns, show="headings",
                                     style="Trace.Treeview")
        frame.grid(row=1, column=0, sticky="nsew")
        cells = {(nt, t): " ".join(prod) or EPSILON for (nt, t), prod in TABLE.items()}
        table.heading("nt", text="", anchor="w")
        table.column("nt", width=90, stretch=False)
        for terminal in terminals:
            widest = max([len(terminal)] + [len(v) for (nt, t), v in cells.items() if t == terminal])
            table.heading(terminal, text=terminal, anchor="w")
            table.column(terminal, width=max(70, widest * 9 + 20), stretch=False)
        for nt in LL1_GRAMMAR:
            table.insert("", "end", values=[nt] + [cells.get((nt, t), "") for t in terminals])
        notebook.add(table_tab, text="5  LL(1) table")


def main() -> None:
    root = tk.Tk()
    AnalyzerWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
