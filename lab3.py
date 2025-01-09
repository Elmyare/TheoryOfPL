from dataclasses import dataclass
from typing import Dict, List
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext
from os import path
import json
from functools import partial


@dataclass
class Machine:
    Q: List[str]
    V: List[str]
    Rules: List[List[str]]
    Start_state: str
    Current_state: str
    Start_stack: str
    Stack: str
    End: str


def machine_input(filename):
    try:
        with open(filename, "r") as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Файл с данными не найден.")
        return None
    states = data["states"]
    alphabet = data["alphabet"]
    in_stack = data["in_stack"]
    rules = data["rules"]
    start = data["start"]
    stack = data["start_stack"]
    end = data["end"]
    return Machine(states, alphabet, rules, start, start, stack, stack, end)


def generate_func_tab(machine, frame):
    lbl_sigma = Label(frame, text=f"Правила перехода (δ):", font=("Arial", 15), padx=5, pady=5)
    lbl_sigma.grid(row=0, column=0, columnspan=3, sticky="w")

    for i, rule in enumerate(machine.Rules):
        lbl_current = Label(frame, text=f"({rule[0]}, {rule[1]}, {rule[2]})", font=("Arial", 15), padx=5, pady=5)
        lbl_current.grid(row=1 + i, column=0, sticky="w")
        lbl_arrow = Label(frame, text=f"→", font=("Arial", 15), padx=5, pady=5)
        lbl_arrow.grid(row=1 + i, column=1)
        lbl_next = Label(frame, text=f"({rule[3]}, {rule[4]})", font=("Arial", 15), padx=5, pady=5)
        lbl_next.grid(row=1 + i, column=2, sticky="w")


def load_machine():
    file = filedialog.askopenfilename(filetypes=[("Json Files", "*.json"), ("All Files", "*.*")],
                                      initialdir=path.dirname(__file__))
    if not file:
        return
    machine = machine_input(file)
    if machine:
        display_machine(machine)


def display_machine(machine):
    # Очистка предыдущих данных
    for widget in func_frame.winfo_children():
        widget.destroy()
    for widget in input_frame.winfo_children():
        widget.destroy()

    # Отображение таблицы переходов
    generate_func_tab(machine, func_frame)

    # Отображение поля ввода цепочки
    lbl_check_word = Label(input_frame, text="Введите цепочку для проверки:", font=("Arial", 15), padx=5, pady=10)
    lbl_check_word.grid(row=0, column=0, sticky="w")

    global txt
    txt = Entry(input_frame, width=60)
    txt.grid(row=1, column=0, sticky="ew")

    btn_check_word = Button(input_frame, text="Проверить", command=partial(check_button, machine), padx=10, pady=10)
    btn_check_word.grid(row=1, column=1, sticky="e")

    # Очистка окна вывода
    output_text.delete(1.0, END)

    # Обновление области прокрутки
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))


def check_button(machine):
    text = txt.get()
    if text == 'quit':
        return 0
    machine.Current_state = machine.Start_state
    machine.Stack = machine.Start_stack
    if all([c in machine.V for c in text]):
        output_text.insert(END, "Цепочка состоит только из символов алфавита, начинаю проверку...\n")
        output_text.see(END)  # Автоматическая прокрутка вниз
        check_word(text, machine)
    else:
        output_text.insert(END, "Ошибка. Слово состоит из символов, которых нет в алфавите.\n")
        output_text.see(END)  # Автоматическая прокрутка вниз

    # Обновление области прокрутки
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))


def check_word(word, machine):
    output_text.insert(END, f"Начальное состояние стека: {machine.Stack}\n")
    output_text.see(END)  # Автоматическая прокрутка вниз
    step = 1
    for i in word:
        output_text.insert(END, f"Шаг {step}\n")
        output_text.see(END)  # Автоматическая прокрутка вниз
        rule_skip = 0
        output_text.insert(END, f"Текущий символ: {i}\n")
        output_text.see(END)  # Автоматическая прокрутка вниз
        output_text.insert(END, f"Текущий стек: {machine.Stack}\n")
        output_text.see(END)  # Автоматическая прокрутка вниз
        for j in machine.Rules:
            if machine.Current_state != j[0]:
                rule_skip += 1
                continue
            if i != j[1]:
                rule_skip += 1
                continue
            if machine.Stack[0] != j[2]:
                rule_skip += 1
                continue

            output_text.insert(END, f"Применено правило: ({j[0]}, {j[1]}, {j[2]}) -> ({j[3]}, {j[4]})\n\n")
            output_text.see(END)  # Автоматическая прокрутка вниз
            machine.Current_state = j[3]
            if j[4] == "EPS":
                machine.Stack = machine.Stack[1:]
            elif len(j[4]) == 2:
                machine.Stack = i + machine.Stack
            elif j[4] == "ε":
                machine.Stack = machine.Stack[1:]
            break
        step += 1
        if rule_skip == len(machine.Rules):
            output_text.insert(END, "Ошибка. Отсутствует переход для данного состояния.\n\n")
            output_text.see(END)  # Автоматическая прокрутка вниз
            return

    while True:
        if len(machine.Stack) == 0 and machine.Current_state == machine.End:
            output_text.insert(END, "Цепочка принадлежит заданному ДМПА.\n\n")
            output_text.see(END)  # Автоматическая прокрутка вниз
            return
        output_text.insert(END, f"Шаг {step}\n")
        output_text.see(END)  # Автоматическая прокрутка вниз
        rule_skip = 0
        output_text.insert(END, f"Текущий символ: ε\n")
        output_text.see(END)  # Автоматическая прокрутка вниз
        output_text.insert(END, f"Текущий стек: {machine.Stack}\n")
        output_text.see(END)  # Автоматическая прокрутка вниз
        for j in machine.Rules:
            if machine.Current_state != j[0]:
                rule_skip += 1
                continue
            if "ε" != j[1] and "EPS" != j[1]:
                rule_skip += 1
                continue
            if machine.Stack[0] != j[2]:
                rule_skip += 1
                continue

            output_text.insert(END, f"Применено правило: ({j[0]}, {j[1]}, {j[2]}) -> ({j[3]}, {j[4]})\n\n")
            output_text.see(END)  # Автоматическая прокрутка вниз
            machine.Current_state = j[3]
            if j[4] == "ε" or j[4] == "EPS":
                machine.Stack = machine.Stack[1:]
                break
        step += 1
        if rule_skip == len(machine.Rules):
            output_text.insert(END, "Ошибка. Отсутствует переход для данного состояния.\n\n")
            output_text.see(END)  # Автоматическая прокрутка вниз
            return

    # Обновление области прокрутки
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))


if __name__ == '__main__':
    window = Tk()
    window.title("Проверка цепочек на принадлежность ДМПА")
    window.geometry('800x600')

    # Меню
    menubar = Menu(window)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Загрузить ДМПА", command=load_machine)
    filemenu.add_separator()
    filemenu.add_command(label="Выход", command=window.quit)
    menubar.add_cascade(label="Файл", menu=filemenu)
    window.config(menu=menubar)

    # Создание Canvas и Scrollbar
    canvas = Canvas(window)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(window, command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    # Фрейм для размещения всех элементов
    main_frame = Frame(canvas)
    canvas.create_window((0, 0), window=main_frame, anchor="nw")

    # Обновление области прокрутки при изменении содержимого
    def update_scrollregion(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    main_frame.bind("<Configure>", update_scrollregion)

    # Фрейм для таблицы переходов
    func_frame = Frame(master=main_frame, padx=10, pady=15)
    func_frame.pack(fill="both", expand=True)

    # Фрейм для ввода цепочки
    input_frame = Frame(master=main_frame, padx=10, pady=15)
    input_frame.pack(fill="x")

    # Окно вывода
    output_text = scrolledtext.ScrolledText(main_frame, width=100, height=20, state="normal")
    output_text.pack(fill="both", expand=True, padx=10, pady=10)

    window.mainloop()