import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class Grammar:
    VT: List[str]  # Терминальные символы
    VN: List[str]  # Нетерминальные символы
    P: Dict[str, List[str]]  # Правила вывода
    S: str  # Начальный символ

def parse_grammar_input(VT: str, VN: str, rules: List[str], S: str) -> Grammar:
    VT_list = VT.split()
    VN_list = VN.split()
    P = {}
    for rule in rules:
        left, right = rule.split("->")
        left = left.strip()
        right_options = [opt.strip() for opt in right.split("|")]
        P[left] = right_options
    return Grammar(VT_list, VN_list, P, S)

def generate_chains(grammar: Grammar, min_len: int, max_len: int, leftmost: bool) -> List[str]:
    results = set()
    queue = [(grammar.S, [grammar.S])]  # (цепочка, история вывода)

    while queue:
        current, history = queue.pop(0)

        # Если цепочка состоит только из терминалов и её длина в пределах диапазона
        if all(c in grammar.VT for c in current):
            if min_len <= len(current) <= max_len:
                results.add(current)
            continue

        # Если длина цепочки превышает максимальную, пропускаем её
        if len(current) > max_len:
            continue

        # Находим все нетерминалы для замены
        for i, symbol in enumerate(current):
            if symbol in grammar.VN:
                for replacement in grammar.P[symbol]:
                    new_chain = current[:i] + replacement + current[i + 1:]
                    new_history = history + [new_chain]
                    queue.append((new_chain, new_history))
                break  # Заменяем только первый нетерминал (левосторонний вывод)

    return sorted(results)

def build_parse_tree(chain: str, grammar: Grammar, leftmost: bool) -> List[str]:
    tree = []
    current = grammar.S

    def replace_first_nonterminal(sequence, symbol, replacement):
        index = sequence.find(symbol)
        return sequence[:index] + replacement + sequence[index + 1:]

    while current != chain:
        for i, symbol in enumerate(current if leftmost else reversed(current)):
            if symbol in grammar.VN:
                for replacement in grammar.P[symbol]:
                    candidate = replace_first_nonterminal(current, symbol, replacement)
                    if chain.startswith(candidate) or chain.endswith(candidate):
                        tree.append((current, symbol, replacement))
                        current = candidate
                        break
                break
    return tree

class GrammarApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Генератор цепочек КС-языка")

        # Предустановленная грамматика
        self.default_grammar = Grammar(
            VT=["0", "1"],
            VN=["A", "B"],
            P={"A": ["0A1A", "1A0A", ""], "B": ["1B0", ""]},
            S="A"
        )
        self.use_default = tk.BooleanVar(value=True)

        # Грамматика и режим вывода
        self.grammar = None
        self.leftmost = tk.BooleanVar(value=True)

        # Выбор грамматики
        tk.Label(master, text="Использовать предустановленную грамматику:").grid(row=0, column=0, sticky="w")
        tk.Checkbutton(master, variable=self.use_default, command=self.toggle_grammar_input).grid(row=0, column=1, sticky="w")

        # Ввод грамматики
        tk.Label(master, text="Терминальные символы (через пробел):").grid(row=1, column=0, sticky="w")
        self.vt_entry = tk.Entry(master)
        self.vt_entry.grid(row=1, column=1)

        tk.Label(master, text="Нетерминальные символы (через пробел):").grid(row=2, column=0, sticky="w")
        self.vn_entry = tk.Entry(master)
        self.vn_entry.grid(row=2, column=1)

        tk.Label(master, text="Правила вывода (A -> aB | b):").grid(row=3, column=0, sticky="w")
        self.rules_text = tk.Text(master, height=5, width=30)
        self.rules_text.grid(row=3, column=1)

        tk.Label(master, text="Начальный символ:").grid(row=4, column=0, sticky="w")
        self.s_entry = tk.Entry(master)
        self.s_entry.grid(row=4, column=1)

        # Диапазон длин
        tk.Label(master, text="Минимальная длина цепочек:").grid(row=5, column=0, sticky="w")
        self.min_len_entry = tk.Entry(master)
        self.min_len_entry.grid(row=5, column=1)

        tk.Label(master, text="Максимальная длина цепочек:").grid(row=6, column=0, sticky="w")
        self.max_len_entry = tk.Entry(master)
        self.max_len_entry.grid(row=6, column=1)

        # Левый или правый вывод
        tk.Label(master, text="Режим вывода:").grid(row=7, column=0, sticky="w")
        tk.Radiobutton(master, text="Левосторонний", variable=self.leftmost, value=True).grid(row=7, column=1, sticky="w")
        tk.Radiobutton(master, text="Правосторонний", variable=self.leftmost, value=False).grid(row=8, column=1, sticky="w")

        # Кнопки управления
        tk.Button(master, text="Сгенерировать цепочки", command=self.generate_chains).grid(row=9, column=0, pady=10)
        tk.Button(master, text="Построить дерево вывода", command=self.build_tree).grid(row=9, column=1, pady=10)

        # Вывод результатов
        self.output = tk.Text(master, height=10, width=50)
        self.output.grid(row=10, column=0, columnspan=2, pady=5)

        self.toggle_grammar_input()

    def toggle_grammar_input(self):
        state = "disabled" if self.use_default.get() else "normal"
        self.vt_entry.config(state=state)
        self.vn_entry.config(state=state)
        self.rules_text.config(state=state)
        self.s_entry.config(state=state)

    def generate_chains(self):
        try:
            if self.use_default.get():
                self.grammar = self.default_grammar
            else:
                self.grammar = parse_grammar_input(
                    self.vt_entry.get(),
                    self.vn_entry.get(),
                    self.rules_text.get("1.0", tk.END).strip().splitlines(),
                    self.s_entry.get().strip(),
                )

            min_len = int(self.min_len_entry.get())
            max_len = int(self.max_len_entry.get())

            chains = generate_chains(self.grammar, min_len, max_len, self.leftmost.get())
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "\n".join(chains))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации: {e}")

    def build_tree(self):
        try:
            chain = self.output.get("sel.first", "sel.last").strip()
            tree = build_parse_tree(chain, self.grammar, self.leftmost.get())
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "\n".join(f"{step[0]} => {step[2]}" for step in tree))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка построения дерева: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GrammarApp(root)
    root.mainloop()