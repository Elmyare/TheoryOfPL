import json
from tkinter import *
from tkinter import filedialog, messagebox
from os import path

class MPTransformer:
    def __init__(self, states, alphabet, stack_alphabet, rules, start_state, start_stack, end_states):
        self.states = states
        self.alphabet = alphabet
        self.stack_alphabet = stack_alphabet
        self.rules = self._normalize_rules(rules)  # Нормализуем правила
        self.start_state = start_state
        self.start_stack = start_stack
        self.end_states = end_states

    def _normalize_rules(self, rules):
        # Заменяем "EPS" на "ε" в правилах
        normalized_rules = []
        for rule in rules:
            normalized_rule = [
                rule[0],
                rule[1] if rule[1] != "EPS" else "ε",
                rule[2] if rule[2] != "EPS" else "ε",
                rule[3],
                rule[4] if rule[4] != "EPS" else "ε",
                rule[5] if rule[5] != "EPS" else "ε",
            ]
            normalized_rules.append(normalized_rule)
        return normalized_rules

    def translate(self, input_chain):
        self.current_state = self.start_state
        self.stack = [self.start_stack]
        self.output = ""
        self.steps = []

        for symbol in input_chain:
            if symbol not in self.alphabet:
                return False, f"Ошибка: символ '{symbol}' не принадлежит алфавиту."

            if not self.stack:
                return False, "Ошибка: стек пуст, дальнейшая обработка невозможна."

            step_info = self._process_symbol(symbol)
            if not step_info:
                return False, "Ошибка: отсутствует правило для данного символа и состояния."

        # Обработка завершающих ε-переходов
        while self.stack:
            step_info = self._process_epsilon()
            if not step_info:
                return False, "Ошибка: невозможно завершить обработку (стек не пуст)."

        if self.current_state in self.end_states:
            return True, f"Цепочка переведена успешно. Результат: {self.output}"
        else:
            return False, "Ошибка: конечное состояние не достигнуто."

    def _process_symbol(self, symbol):
        if not self.stack:
            return False

        for rule in self.rules:
            if (rule[0] == self.current_state and
                rule[1] == symbol and
                rule[2] == self.stack[-1]):
                self.current_state = rule[3]
                self.stack.pop()
                if rule[4] != "ε":
                    self.stack.extend(reversed(list(rule[4])))
                if rule[5] != "ε":
                    self.output += rule[5]
                self.steps.append(f"({rule[0]}, {symbol}, {rule[2]}) -> ({rule[3]}, {rule[4]}, {rule[5]})")
                return True
        return False

    def _process_epsilon(self):
        if not self.stack:
            return False

        for rule in self.rules:
            if (rule[0] == self.current_state and
                rule[1] == "ε" and
                rule[2] == self.stack[-1]):
                self.current_state = rule[3]
                self.stack.pop()
                if rule[4] != "ε":
                    self.stack.extend(reversed(list(rule[4])))
                if rule[5] != "ε":
                    self.output += rule[5]
                self.steps.append(f"({rule[0]}, ε, {rule[2]}) -> ({rule[3]}, {rule[4]}, {rule[5]})")
                return True
        return False


class MPTransformerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("МП-преобразователь")
        self.root.geometry("600x400")

        self.machine = None

        # Меню
        self.menu_bar = Menu(root)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Загрузить МП-преобразователь", command=self.load_machine)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Выход", command=root.quit)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)
        self.root.config(menu=self.menu_bar)

        # Интерфейс
        self.label = Label(root, text="МП-преобразователь", font=("Arial", 16))
        self.label.pack(pady=10)

        self.chain_entry = Entry(root, width=50)
        self.chain_entry.pack(pady=10)

        self.check_button = Button(root, text="Проверить цепочку", command=self.check_chain)
        self.check_button.pack(pady=10)

        self.output_text = Text(root, width=70, height=15, wrap=WORD)
        self.output_text.pack(pady=10)

    def load_machine(self):
        file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], initialdir=path.dirname(__file__))
        if not file:
            return

        try:
            with open(file, "r") as f:
                data = json.load(f)

            self.machine = MPTransformer(
                states=data["states"],
                alphabet=data["alphabet"],
                stack_alphabet=data["in_stack"],
                rules=data["rules"],
                start_state=data["start"],
                start_stack=data["start_stack"],
                end_states=data["end"]
            )

            self.output_text.insert(END, "МП-преобразователь загружен успешно.\n")
            self.output_text.insert(END, f"Алфавит: {data['alphabet']}\n")
            self.output_text.insert(END, f"Начальное состояние: {data['start']}\n")
            self.output_text.insert(END, f"Конечные состояния: {data['end']}\n\n")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить МП-преобразователь: {e}")

    def check_chain(self):
        if not self.machine:
            messagebox.showerror("Ошибка", "Сначала загрузите МП-преобразователь.")
            return

        chain = self.chain_entry.get()
        if not chain:
            messagebox.showerror("Ошибка", "Введите цепочку для проверки.")
            return

        self.output_text.insert(END, f"Проверка цепочки: {chain}\n")

        success, message = self.machine.translate(chain)
        if success:
            self.output_text.insert(END, f"Результат: {message}\n")
        else:
            self.output_text.insert(END, f"Ошибка: {message}\n")

        self.output_text.insert(END, "Шаги перевода:\n")
        for step in self.machine.steps:
            self.output_text.insert(END, f"{step}\n")
        self.output_text.insert(END, "\n")


if __name__ == "__main__":
    root = Tk()
    app = MPTransformerApp(root)
    root.mainloop()