from dataclasses import dataclass
from typing import Dict, List, Optional
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

@dataclass
class Grammar:
    VT: List[str]
    VN: List[str]
    P: Dict[str, List[str]]
    S: str

def count_non_term_sym(grammar, sequence):
    length = 0
    for sym in sequence:
        if sym in grammar.VT:
            length += 1
    return length

def generate_chains(grammar, left_border, right_border):
    rules = list(grammar.S)
    used_sequence = set()
    chains = []
    while rules:
        sequence = rules.pop()
        if sequence in used_sequence:
            continue
        used_sequence.add(sequence)
        no_term = True
        for i, symbol in enumerate(sequence):
            if symbol in grammar.VN:
                no_term = False
                for elem in grammar.P[symbol]:
                    temp = sequence[:i] + elem + sequence[i + 1:]
                    if count_non_term_sym(grammar, temp) <= right_border and temp not in rules:
                        rules.append(temp)
            elif symbol not in grammar.VT:
                no_term = False
                break
        if no_term and left_border <= len(sequence) <= right_border:
            chains.append(sequence if sequence else "λ")
    return chains

class TreeNode:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.children: List[TreeNode] = []

    def add_child(self, child: "TreeNode"):
        self.children.append(child)

    def __repr__(self):
        return f"TreeNode({self.symbol})"

class GrammarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор цепочек языка")
        
        self.grammar = None
        self.chains = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Выбор грамматики
        self.grammar_frame = ttk.LabelFrame(self.root, text="Грамматика")
        self.grammar_frame.pack(padx=10, pady=10, fill="x")
        
        self.grammar_choice = ttk.Combobox(self.grammar_frame, values=["Предопределенная", "Ввести вручную"])
        self.grammar_choice.pack(padx=5, pady=5)
        self.grammar_choice.current(0)
        self.grammar_choice.bind("<<ComboboxSelected>>", self.toggle_grammar_input)
        
        # Поля для ввода грамматики
        self.custom_grammar_frame = ttk.Frame(self.grammar_frame)
        
        self.vt_label = ttk.Label(self.custom_grammar_frame, text="Терминальные символы (VT):")
        self.vt_label.grid(row=0, column=0, padx=5, pady=5)
        self.vt_entry = ttk.Entry(self.custom_grammar_frame)
        self.vt_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.vn_label = ttk.Label(self.custom_grammar_frame, text="Нетерминальные символы (VN):")
        self.vn_label.grid(row=1, column=0, padx=5, pady=5)
        self.vn_entry = ttk.Entry(self.custom_grammar_frame)
        self.vn_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.p_label = ttk.Label(self.custom_grammar_frame, text="Правила (P):")
        self.p_label.grid(row=2, column=0, padx=5, pady=5)
        self.p_text = ScrolledText(self.custom_grammar_frame, width=40, height=5)
        self.p_text.grid(row=2, column=1, padx=5, pady=5)
        
        self.s_label = ttk.Label(self.custom_grammar_frame, text="Целевой символ (S):")
        self.s_label.grid(row=3, column=0, padx=5, pady=5)
        self.s_entry = ttk.Entry(self.custom_grammar_frame)
        self.s_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Диапазон длин цепочек
        self.range_frame = ttk.LabelFrame(self.root, text="Диапазон длин цепочек")
        self.range_frame.pack(padx=10, pady=10, fill="x")
        
        self.range_label = ttk.Label(self.range_frame, text="ОТ и ДО:")
        self.range_label.grid(row=0, column=0, padx=5, pady=5)
        self.range_entry = ttk.Entry(self.range_frame)
        self.range_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Кнопка генерации
        self.generate_button = ttk.Button(self.root, text="Сгенерировать цепочки", command=self.generate_chains)
        self.generate_button.pack(padx=10, pady=10)
        
        # Список сгенерированных цепочек
        self.chains_frame = ttk.LabelFrame(self.root, text="Сгенерированные цепочки")
        self.chains_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.chains_listbox = tk.Listbox(self.chains_frame)
        self.chains_listbox.pack(padx=5, pady=5, fill="both", expand=True)
        
        # Кнопка построения дерева
        self.tree_button = ttk.Button(self.root, text="Построить дерево вывода", command=self.build_tree)
        self.tree_button.pack(padx=10, pady=10)
        
        # Окно для вывода дерева
        self.tree_output = ScrolledText(self.root, width=50, height=10, state="disabled")
        self.tree_output.pack(padx=10, pady=10, fill="both", expand=True)
    
    def toggle_grammar_input(self, event=None):
        if self.grammar_choice.get() == "Ввести вручную":
            self.custom_grammar_frame.pack(padx=5, pady=5, fill="x")
        else:
            self.custom_grammar_frame.pack_forget()
    
    def generate_chains(self):
        try:
            left_border, right_border = map(int, self.range_entry.get().split())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный диапазон")
            return
        
        if self.grammar_choice.get() == "Предопределенная":
            # Предопределенная грамматика: S -> aSb | ab
            data = {"VT": ["a", "b"],
                    "VN": ["S"],
                    "P": {"S": ["aSb", "ab"]},
                    "S": "S"}
            self.grammar = Grammar(data["VT"], data["VN"], data["P"], data["S"])
        else:
            try:
                VT = self.vt_entry.get().split()
                VN = self.vn_entry.get().split()
                P = {}
                rules = self.p_text.get("1.0", tk.END).strip().split("\n")
                for rule in rules:
                    if "->" in rule:
                        lhs, rhs = rule.split("->")
                        lhs = lhs.strip()
                        rhs = [r.strip() for r in rhs.split("|")]
                        P[lhs] = rhs
                S = self.s_entry.get().strip()
                self.grammar = Grammar(VT, VN, P, S)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Некорректный ввод грамматики: {e}")
                return
        
        self.chains = generate_chains(self.grammar, left_border, right_border)
        self.chains_listbox.delete(0, tk.END)
        for chain in self.chains:
            self.chains_listbox.insert(tk.END, chain)
    
    def build_tree(self):
        selected_chain = self.chains_listbox.get(tk.ACTIVE)
        if not selected_chain:
            messagebox.showerror("Ошибка", "Выберите цепочку для построения дерева")
            return
        
        # Построение дерева вывода
        tree_root = self.generate_tree(self.grammar.S, selected_chain)
        if tree_root:
            tree_structure = self.tree_to_string(tree_root)
            self.tree_output.config(state="normal")
            self.tree_output.delete("1.0", tk.END)
            self.tree_output.insert(tk.END, tree_structure)
            self.tree_output.config(state="disabled")
        else:
            messagebox.showerror("Ошибка", "Не удалось построить дерево для выбранной цепочки")
    
    def generate_tree(self, current_symbol: str, target_chain: str) -> Optional[TreeNode]:
        if current_symbol in self.grammar.VT:
            if target_chain.startswith(current_symbol):
                return TreeNode(current_symbol)
            else:
                return None
        
        if current_symbol in self.grammar.VN:
            for production in self.grammar.P[current_symbol]:
                node = TreeNode(current_symbol)
                remaining_chain = target_chain
                valid = True
                for symbol in production:
                    if symbol in self.grammar.VT:
                        if remaining_chain.startswith(symbol):
                            node.add_child(TreeNode(symbol))
                            remaining_chain = remaining_chain[len(symbol):]
                        else:
                            valid = False
                            break
                    else:
                        child_node = self.generate_tree(symbol, remaining_chain)
                        if not child_node:
                            valid = False
                            break
                        node.add_child(child_node)
                        remaining_chain = remaining_chain[len(self.tree_to_string(child_node).replace("\n", "")):]
                if valid and not remaining_chain:
                    return node
        return None
    
    def tree_to_string(self, node: TreeNode, level=0) -> str:
        result = "  " * level + node.symbol + "\n"
        for child in node.children:
            result += self.tree_to_string(child, level + 1)
        return result

if __name__ == '__main__':
    root = tk.Tk()
    app = GrammarApp(root)
    root.mainloop()