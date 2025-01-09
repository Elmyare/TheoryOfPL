from dataclasses import dataclass
from typing import Dict, List
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext
from functools import partial
from os import path
import json


@dataclass
class Machine:
    Q: List[str]
    V: List[str]
    Func: Dict[str, Dict[str, str]]
    Start: str
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
    func = data["Func"]
    start = data["start"]
    ends = data["ends"]
    return Machine(states, alphabet, func, start, ends)


def generate_func_tab(machine, frame):
    lbl_sigma = Label(frame, text=f"δ", font=("Arial", 15), padx=5, pady=5)
    lbl_sigma.grid(row=0, column=0)
    for i in range(len(machine.V)):
        lbl_alphabet = Label(frame, text=f"'{list(machine.V)[i]}'", font=("Arial", 15), padx=5, pady=5)
        lbl_alphabet.grid(row=0, column=1 + i)
    for i in range(len(machine.Q)):
        lbl_state = Label(frame, text=f"{list(machine.Q)[i]}:", font=("Arial", 15), padx=5, pady=5)
        lbl_state.grid(row=1 + i, column=0)
        for j in range(len(machine.V)):
            text = "λ"
            if (state := machine.Func.get(list(machine.Q)[i])) is not None:
                if (passage := state.get(list(machine.V)[j])) is not None:
                    text = passage
            lbl_alphabet = Label(frame, text=text, font=("Arial", 15), padx=5, pady=5)
            lbl_alphabet.grid(row=1 + i, column=1 + j)


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


def check_button(machine):
    text = txt.get()
    if text == 'quit':
        return 0
    if all([c in machine.V for c in text]):
        output_text.insert(END, "Цепочка состоит только из символов алфавита, начинаю проверку...\n")
        check_word(text, machine, machine.Start)
    else:
        output_text.insert(END, "Ошибка. Слово состоит из символов, которых нет в алфавите.\n")


def check_word(word, machine, state):
    if word == "λ":
        output_text.insert(END, f"Конечное состояние: {state}\n")
        if state in machine.End:
            output_text.insert(END, "Цепочка принадлежит заданному ДКА.\n")
        else:
            output_text.insert(END, "Ошибка. Конечное состояние не принадлежит множеству конечных состояний ДКА.\n")
        return

    output_text.insert(END, f"({state}, {word})\n")
    if len(word) > 1:
        try:
            state = machine.Func[state][word[0]]
        except KeyError:
            output_text.insert(END, "Ошибка. Отсутствует переход для данного состояния.\n")
            return
        word = word[1:]
    else:
        try:
            state = machine.Func[state][word[0]]
        except KeyError:
            output_text.insert(END, "Ошибка. Отсутствует переход для данного состояния.\n")
            return
        word = "λ"
    check_word(word, machine, state)


if __name__ == '__main__':
    window = Tk()
    window.title("Проверка цепочек на принадлежность ДКА")
    window.geometry('800x600')

    # Меню
    menubar = Menu(window)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Загрузить ДКА", command=load_machine)
    filemenu.add_separator()
    filemenu.add_command(label="Выход", command=window.quit)
    menubar.add_cascade(label="Файл", menu=filemenu)
    window.config(menu=menubar)

    # Фрейм для таблицы переходов
    func_frame = Frame(master=window, padx=10, pady=15)
    func_frame.pack(fill="both", expand=True)

    # Фрейм для ввода цепочки
    input_frame = Frame(master=window, padx=10, pady=15)
    input_frame.pack(fill="x")

    # Окно вывода
    output_text = scrolledtext.ScrolledText(window, width=100, height=20, state="normal")
    output_text.pack(fill="both", expand=True, padx=10, pady=10)

    window.mainloop()