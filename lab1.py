import tkinter as tk
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Grammar:
    VT: List[str]
    VN: List[str]
    P: Dict[str, List[str]]
    S: str

def grammar_input():
    result = dict()
    VT = list(map(str, input("Введите терминальные символы: ").split()))
    VN = list(map(str, input("Введите нетерминальные символы: ").split()))
    n = int(input("Введите количество правил: "))
    P = dict()
    for _ in range(n):
        r = input("Введите левую часть правила: ")
        rs = input("Введите правую часть правила: ").split()
        P[r] = rs
    S = str(input("Введите начальный символ: "))
    VT.append("_")
    return {"VT": VT, "VN": VN, "P": P, "S": S}

def count_non_term_sym(grammar, sequence):
    length = 0
    for sym in sequence:
        if sym in grammar.VT:
            length += 1
    return length

class App:
    def __init__(self, master):
        self.master = master
        master.title("Генератор цепочек")

        self.data = {"VT": ["a", "b", "c"],
                     "VN": ["A", "B", "C"],
                     "P": {"A": ["aBbbC"], "B": ["aaBb", ""], "C": ["cC", ""]},
                     "S": "A"}

        self.grammar = Grammar(self.data["VT"], self.data["VN"], self.data["P"], self.data["S"])

        self.left_border = tk.IntVar()
        self.right_border = tk.IntVar()

        tk.Label(master, text="Введите диапазон цепочек от и до:").grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(master, textvariable=self.left_border).grid(row=1, column=0, padx=10, pady=5)
        tk.Entry(master, textvariable=self.right_border).grid(row=2, column=0, padx=10, pady=5)

        tk.Button(master, text="Генерировать цепочки", command=self.generate).grid(row=3, column=0, padx=10, pady=10)

        self.result = tk.Text(master, height=10, width=50)
        self.result.grid(row=4, column=0, padx=10, pady=5)

    def generate(self):
        self.result.delete(1.0, tk.END)
        rules = list(self.grammar.S)
        used_sequence = set()
        while rules:
            sequence = rules.pop()
            if sequence in used_sequence:
                continue
            used_sequence.add(sequence)
            no_term = True
            for i, symbol in enumerate(sequence):
                if symbol in self.grammar.VN:
                    no_term = False
                    for elem in self.grammar.P[symbol]:
                        temp = sequence[:i] + elem + sequence[i + 1:]
                        if count_non_term_sym(self.grammar, temp) <= self.right_border.get() and temp not in rules:
                            rules.append(temp)
                elif symbol not in self.grammar.VT:
                    no_term = False
                    self.result.insert(tk.END, "Цепочка " + sequence + " не разрешима\n")
                    break
            if no_term and self.left_border.get() <= len(sequence) <= self.right_border.get():
                self.result.insert(tk.END, sequence if sequence else "лямбда\n")

root = tk.Tk()
app = App(root)
root.mainloop()
