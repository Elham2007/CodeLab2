import os                          # used to build a reliable path to the jokes file
import random                      # used to pick a random joke
import tkinter as tk               # the GUI toolkit
from tkinter import messagebox     # error pop-ups

# Locate the jokes file next to this script, wherever it is run from.
JOKES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "randomJokes.txt")

# Pastel colour palette (change colours here and the whole app updates).
BG = "#FFF5EE"        # cream window background
CARD = "#FFFFFF"      # white "card" behind the joke text
TEXT = "#4A4A68"      # dark slate-purple text
PUNCH = "#9B6BB5"     # deeper lavender so the punchline stands out
MINT = "#B5EAD7"      # "Alexa tell me a Joke" button
PINK = "#FFC8DD"      # "Show Punchline" button
SKY = "#BDE0FE"       # "Next Joke" button
PEACH = "#FFDAC1"     # "Quit" button
LAVENDER = "#CDB4DB"  # hover colour and card border

FONT = "Comic Sans MS"   # round, friendly font (Tkinter falls back if missing)

# Greeting shown before any joke has been told.
GREETING = "Hi hi! 👋 Press the button and I'll tell you a joke!"


def loadJokes(path):
    """Read the jokes file and return a list of (setup, punchline) tuples."""
    jokes = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()                 # remove spaces and the newline
            # Skip blank or badly formatted lines (no question mark).
            if "?" not in line:
                continue
            # Split on the FIRST question mark only, so punchlines containing
            # a "?" are not cut short. The "?" is added back to the setup.
            setup, punchline = line.split("?", 1)
            jokes.append((setup.strip() + "?", punchline.strip()))
    return jokes


class JokeApp:
    """The joke assistant window."""

    def __init__(self, root, jokes):
        self.root = root
        self.jokes = jokes       # all jokes loaded from the file
        self.current = None      # the (setup, punchline) currently on screen

        root.title("Alexa Joke Teller")
        root.geometry("600x480")
        root.resizable(False, False)
        root.configure(bg=BG)

        # --- Title and mood face at the top ---
        tk.Label(root, text="🎀 Joke Time! 🎀", font=(FONT, 22, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(15, 0))
        # The face changes: 😊 waiting, 🤔 setup shown, 🤣 punchline revealed.
        self.face_label = tk.Label(root, text="😊", font=(FONT, 36), bg=BG)
        self.face_label.pack()

        # --- Display frame: a white card holding the setup and punchline ---
        display = tk.Frame(root, padx=20, pady=5, bg=BG)
        display.pack(fill="x")
        card = tk.Frame(display, bg=CARD, padx=15, pady=10,
                        highlightthickness=2, highlightbackground=LAVENDER)
        card.pack(fill="x")

        # Label for the joke setup. wraplength makes long text wrap onto new
        # lines, and a fixed height stops the window jumping around.
        self.setup_label = tk.Label(
            card, text=GREETING, font=(FONT, 14, "bold"),
            wraplength=500, height=3, bg=CARD, fg=TEXT,
        )
        self.setup_label.pack(pady=(10, 5))

        # Label for the punchline, shown below the setup (empty until revealed).
        self.punchline_label = tk.Label(
            card, text="", font=(FONT, 14, "italic"),
            fg=PUNCH, wraplength=500, height=3, bg=CARD,
        )
        self.punchline_label.pack(pady=5)

        # --- Button frame: four buttons arranged in a 2x2 grid ---
        buttons = tk.Frame(root, padx=20, pady=10, bg=BG)
        buttons.pack()

        # NOTE: button labels match the exercise brief exactly.
        self.tell_button = self.makeButton(
            buttons, "Alexa tell me a Joke", MINT, self.tellJoke)
        self.tell_button.grid(row=0, column=0, padx=6, pady=6)

        # Starts disabled: there is no punchline until a joke has been told.
        self.punch_button = self.makeButton(
            buttons, "Show Punchline", PINK, self.showPunchline)
        self.punch_button.config(state="disabled")
        self.punch_button.grid(row=0, column=1, padx=6, pady=6)

        # Also disabled at first, because "next" only makes sense after a joke.
        self.next_button = self.makeButton(
            buttons, "Next Joke", SKY, self.tellJoke)
        self.next_button.config(state="disabled")
        self.next_button.grid(row=1, column=0, padx=6, pady=6)

        self.quit_button = self.makeButton(buttons, "Quit", PEACH, self.quitApp)
        self.quit_button.grid(row=1, column=1, padx=6, pady=6)

    @staticmethod
    def makeButton(parent, text, colour, command):
        """Create a flat pastel button with a lavender click/hover colour."""
        return tk.Button(parent, text=text, width=20, font=(FONT, 11),
                         bg=colour, fg=TEXT, activebackground=LAVENDER,
                         disabledforeground="#A0A0B8", relief="flat", bd=0,
                         pady=6, cursor="hand2", command=command)

    def tellJoke(self):
        """Pick a random joke (different from the last one) and show its setup."""
        # Exclude the current joke so the same one is not shown twice in a row;
        # "or self.jokes" is a fallback for files containing only one joke.
        choices = [j for j in self.jokes if j != self.current] or self.jokes
        self.current = random.choice(choices)

        self.setup_label.config(text=self.current[0])   # show the setup
        self.punchline_label.config(text="")            # hide the old punchline
        self.face_label.config(text="🤔")               # curious face while we wait
        self.punch_button.config(state="normal")        # allow revealing the new one
        self.next_button.config(state="normal")

    def showPunchline(self):
        """Reveal the punchline below the setup."""
        if self.current:
            self.punchline_label.config(text=f"✨ {self.current[1]} ✨")
            self.face_label.config(text="🤣")           # laughing face!
            self.punch_button.config(state="disabled")  # can only be revealed once

    def quitApp(self):
        """Say goodbye, then close the application."""
        messagebox.showinfo("Bye bye! 👋", "Thanks for laughing with me! 💖")
        self.root.destroy()


def main():
    """Load the jokes, then start the app (or show an error if loading fails)."""
    root = tk.Tk()
    try:
        jokes = loadJokes(JOKES_FILE)
    except FileNotFoundError:
        messagebox.showerror("File not found", f"Could not find:\n{JOKES_FILE}")
        root.destroy()
        return

    if not jokes:
        messagebox.showerror("No jokes", "randomJokes.txt contains no valid jokes.")
        root.destroy()
        return

    JokeApp(root, jokes)
    root.mainloop()        # start Tkinter's event loop


if __name__ == "__main__":
    main()