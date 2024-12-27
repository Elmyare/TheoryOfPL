import tkinter as tk
from tkinter import filedialog, messagebox
import json
from itertools import product

class GrammarToDFAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grammar to DFA Converter")
        
        # Initialize grammar and DFA structures
        self.grammar = ""
        self.dfa = {}
        
        # Set up GUI
        self.setup_menu()
        self.setup_main_interface()

    def setup_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # Author and theme menu
        about_menu = tk.Menu(menu_bar, tearoff=0)
        about_menu.add_command(label="Author", command=self.show_author)
        about_menu.add_command(label="Theme", command=self.show_theme)
        menu_bar.add_cascade(label="About", menu=about_menu)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Grammar File", command=self.load_grammar_from_file)
        file_menu.add_command(label="Save Results", command=self.save_results_to_file)
        menu_bar.add_cascade(label="File", menu=file_menu)

        self.root.config(menu=menu_bar)

    def setup_main_interface(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Grammar type selection
        tk.Label(frame, text="Grammar Type:").grid(row=0, column=0, sticky="w")
        self.grammar_type = tk.StringVar(value="PL")  # Default to PL
        tk.Radiobutton(frame, text="Right-linear (PL)", variable=self.grammar_type, value="PL").grid(row=0, column=1, sticky="w")
        tk.Radiobutton(frame, text="Left-linear (LL)", variable=self.grammar_type, value="LL").grid(row=0, column=2, sticky="w")

        # Grammar input
        tk.Label(frame, text="Enter Regular Grammar:").grid(row=1, column=0, sticky="w")
        self.grammar_input = tk.Text(frame, height=5, width=50)
        self.grammar_input.grid(row=2, column=0, columnspan=3, pady=5)

        # Generate DFA button
        tk.Button(frame, text="Generate DFA", command=self.generate_dfa).grid(row=3, column=0, pady=5)
        
        # Chain generation and validation
        tk.Label(frame, text="Chain Length Range (min, max):").grid(row=4, column=0, sticky="w")
        self.min_length = tk.Entry(frame, width=5)
        self.min_length.grid(row=4, column=1, sticky="w")
        self.max_length = tk.Entry(frame, width=5)
        self.max_length.grid(row=4, column=1, sticky="e")

        tk.Button(frame, text="Generate and Validate Chains", command=self.generate_and_validate_chains).grid(row=5, column=0, pady=5)
        
        # Output area
        tk.Label(frame, text="Output:").grid(row=6, column=0, sticky="w")
        self.output_area = tk.Text(frame, height=10, width=50, state=tk.DISABLED)
        self.output_area.grid(row=7, column=0, columnspan=3, pady=5)

    def show_author(self):
        messagebox.showinfo("Author", "Developer: Маландий Иван\nEmail: ivanlocked55@gmail.com")

    def show_theme(self):
        messagebox.showinfo("Theme", "This program converts a given regular grammar to an equivalent DFA, generates chains, and validates them.")

    def load_grammar_from_file(self):
        file_path = filedialog.askopenfilename(title="Open Grammar File", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                self.grammar = file.read()
                self.grammar_input.delete("1.0", tk.END)
                self.grammar_input.insert(tk.END, self.grammar)

    def save_results_to_file(self):
        file_path = filedialog.asksaveasfilename(title="Save Results", defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.output_area.get("1.0", tk.END))

    def generate_dfa(self):
        self.grammar = self.grammar_input.get("1.0", tk.END).strip()
        if not self.grammar:
            messagebox.showerror("Error", "Grammar is empty!")
            return

        try:
            if self.grammar_type.get() == "PL":
                self.dfa = self.convert_grammar_to_dfa_pl(self.grammar)
            else:
                self.dfa = self.convert_grammar_to_dfa_ll(self.grammar)
            self.display_output("DFA generated successfully!\n\nTransition Table:\n" + json.dumps(self.dfa, indent=4))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate DFA: {e}")

    def convert_grammar_to_dfa_pl(self, grammar):
        rules = [line.strip() for line in grammar.split("\n") if line.strip()]
        states = set()
        alphabet = set()
        transitions = {}
        start_state = "q0"
        accept_states = set()

        state_map = {}  # Map grammar non-terminals to DFA states
        current_state_id = 0

        def get_state(non_terminal):
            nonlocal current_state_id
            if non_terminal not in state_map:
                state_map[non_terminal] = f"q{current_state_id}"
                current_state_id += 1
            return state_map[non_terminal]

        for rule in rules:
            if "->" not in rule:
                raise ValueError(f"Invalid grammar rule: {rule}")

            lhs, rhs = map(str.strip, rule.split("->"))
            from_state = get_state(lhs)
            states.add(from_state)

            for option in rhs.split("|"):
                option = option.strip()
                if len(option) == 1 and option.islower():
                    # Terminal-only production (e.g., S -> b)
                    alphabet.add(option)
                    if from_state not in transitions:
                        transitions[from_state] = {}
                    # Create a new accept state for the terminal
                    accept_state = f"q{current_state_id}"
                    current_state_id += 1
                    transitions[from_state][option] = accept_state
                    accept_states.add(accept_state)
                    states.add(accept_state)
                elif len(option) == 2 and option[0].islower() and option[1].isupper():
                    # Terminal followed by non-terminal (e.g., S -> aA)
                    symbol, next_non_terminal = option
                    alphabet.add(symbol)
                    to_state = get_state(next_non_terminal)
                    states.add(to_state)
                    if from_state not in transitions:
                        transitions[from_state] = {}
                    transitions[from_state][symbol] = to_state

        return {
            "states": list(states),
            "alphabet": list(alphabet),
            "transitions": transitions,
            "start_state": start_state,
            "accept_states": list(accept_states)
        }

    def convert_grammar_to_dfa_ll(self, grammar):
        rules = [line.strip() for line in grammar.split("\n") if line.strip()]
        states = set()
        alphabet = set()
        transitions = {}
        start_state = "q0"
        accept_states = set()

        state_map = {}  # Map grammar non-terminals to DFA states
        current_state_id = 0

        def get_state(non_terminal):
            nonlocal current_state_id
            if non_terminal not in state_map:
                state_map[non_terminal] = f"q{current_state_id}"
                current_state_id += 1
            return state_map[non_terminal]

        # Initialize start state
        start_state = get_state("S")
        states.add(start_state)
        print(start_state)
        for rule in rules:
            if "->" not in rule:
                raise ValueError(f"Invalid grammar rule: {rule}")

            lhs, rhs = map(str.strip, rule.split("->"))
            from_state = get_state(lhs)
            states.add(from_state)

            for option in rhs.split("|"):
                option = option.strip()
                if len(option) == 1 and option.islower():
                    # Terminal-only production (e.g., S -> b)
                    alphabet.add(option)
                    if from_state not in transitions:
                        transitions[from_state] = {}
                    # Create a new accept state for the terminal
                    accept_state = f"q{current_state_id}"
                    current_state_id += 1
                    transitions[from_state][option] = accept_state
                    accept_states.add(accept_state)
                    states.add(accept_state)
                elif len(option) == 2 and option[0].isupper() and option[1].islower():
                    # Non-terminal followed by terminal (e.g., S -> Aa)
                    next_non_terminal, symbol = option
                    alphabet.add(symbol)
                    to_state = get_state(next_non_terminal)
                    states.add(to_state)
                    if to_state not in transitions:
                        transitions[to_state] = {}
                    transitions[to_state][symbol] = from_state

        return {
            "states": list(states),
            "alphabet": list(alphabet),
            "transitions": transitions,
            "start_state": start_state,
            "accept_states": list(accept_states)
        }

    def generate_and_validate_chains(self):
        try:
            min_len = int(self.min_length.get())
            max_len = int(self.max_length.get())
            
            if min_len > max_len or min_len < 0:
                raise ValueError("Invalid length range.")

            chains = self.generate_chains(self.dfa, min_len, max_len)
            valid_chains = [chain for chain in chains if self.validate_chain(self.dfa, chain)]
            
            self.display_output(f"Generated Chains: {chains}\nValid Chains: {valid_chains}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate or validate chains: {e}")

    def generate_chains(self, dfa, min_len, max_len):
        alphabet = dfa.get("alphabet", [])
        chains = []
        for length in range(min_len, max_len + 1):
            chains.extend(["".join(p) for p in product(alphabet, repeat=length)])
        return chains

    # def validate_chain(self, dfa, chain):
    #     current_state = dfa["start_state"]
    #     for symbol in chain:
    #         if symbol not in dfa["alphabet"]:
    #             return False
    #         current_state = dfa["transitions"].get(current_state, {}).get(symbol)
    #         if current_state is None:
    #             return False
    #     return current_state in dfa["accept_states"]
    
    def validate_chain(self, dfa, chain):
        current_state = dfa["start_state"]
        # For LL grammar, process the chain from the end to the beginning
        if self.grammar_type.get() == "LL":
            chain = chain[::-1]  # Reverse the chain

        for symbol in chain:
            if symbol not in dfa["alphabet"]:
                return False
            current_state = dfa["transitions"].get(current_state, {}).get(symbol)
            if current_state is None:
                return False
        return current_state in dfa["accept_states"]

    def display_output(self, text):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert(tk.END, text)
        self.output_area.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = GrammarToDFAApp(root)
    root.mainloop()