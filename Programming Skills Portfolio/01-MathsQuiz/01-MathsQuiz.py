import random                      # used to generate random numbers, operations and messages
import tkinter as tk               # the GUI toolkit
from tkinter import messagebox     # pop-up dialogs (used for the "play again?" prompt)

# Constants

TOTAL_QUESTIONS = 10       # number of problems in one game
FIRST_TRY_POINTS = 10      # points for a correct answer on the first attempt
SECOND_TRY_POINTS = 5      # points for a correct answer on the second attempt

# Each difficulty maps to the (min, max) range of the random numbers.
LEVELS = {
    "Easy": (0, 9),             # single-digit numbers
    "Moderate": (10, 99),       # double-digit numbers
    "Advanced": (1000, 9999),   # four-digit numbers
}

# Pastel colour palette (hex codes) so the theme is easy to change in one place.
BG = "#FFF5EE"            # soft cream background for the whole window
TEXT = "#4A4A68"          # dark slate-purple text (keeps pastel backgrounds readable)
MINT = "#B5EAD7"          # Easy button
SKY = "#BDE0FE"           # Moderate button
PINK = "#FFC8DD"          # Advanced button
LAVENDER = "#CDB4DB"      # accent colour (hover, entry highlight, grade badge)
PEACH = "#FFDAC1"         # Submit / Next button
GOOD = "#3A9D6E"          # feedback text colour: correct answer
BAD = "#D6546E"           # feedback text colour: wrong answer
WARN = "#D98A2B"          # feedback text colour: invalid input

# A round, friendly font. If it is not installed Tkinter falls back to a default.
FONT = "Comic Sans MS"

# Lists of cute messages; random.choice() picks a different one each time.
CORRECT_MESSAGES = ["Yay! You got it!", "Amazing!", "Math wizard!", "You're so smart!", "Purrfect!"]
RETRY_MESSAGES = ["Oopsie! Try once more!", "So close! Give it another go!", "You can do it!"]
WRONG_MESSAGES = ["Aww, no worries!", "That one was tricky!", "Next one will be better!"]

# Global state (kept in one dictionary to keep the functions simple)

state = {
    "level": "Easy",         # difficulty chosen from the menu
    "score": 0,              # running score out of 100
    "question": 0,           # how many problems have been shown so far
    "attempt": 1,            # 1 = first try, 2 = second try
    "answer": 0,             # correct answer of the current problem
    "waiting_next": False,   # True after a question is finished (button becomes "Next")
    "in_quiz": False,        # True while the quiz screen is showing (for the Enter key)
}

ui = {}  # holds references to widgets that need updating while the quiz runs

# Main window

root = tk.Tk()
root.title("Maths Quiz")
root.geometry("500x420")
root.resizable(False, False)       # fixed size keeps the layout tidy
root.configure(bg=BG)              # apply the pastel background to the window

# One frame holds whichever screen is showing (menu, quiz or results).
content = tk.Frame(root, padx=20, pady=20, bg=BG)
content.pack(fill="both", expand=True)


def clearFrame():
    """Remove every widget from the content frame before drawing a new screen."""
    for widget in content.winfo_children():
        widget.destroy()


def makeLabel(text="", size=12, bold=False, colour=TEXT):
    """Create a label that already uses the theme background and font."""
    weight = "bold" if bold else "normal"
    return tk.Label(content, text=text, font=(FONT, size, weight), bg=BG, fg=colour)


def makeButton(text, colour, command, width=30):
    """Create a flat pastel button; activebackground gives a hover/click effect."""
    return tk.Button(content, text=text, width=width, font=(FONT, 12),
                     bg=colour, fg=TEXT, activebackground=LAVENDER,
                     relief="flat", bd=0, pady=6, cursor="hand2", command=command)


def hearts(done):
    """Return a row of hearts: pink for finished questions, white for the rest."""
    return "💗" * done + "🤍" * (TOTAL_QUESTIONS - done)

# Required functions

def displayMenu():
    """Show the difficulty selection menu and reset the game state."""
    # Reset everything so a replay always starts from scratch.
    state.update(score=0, question=0, attempt=1, waiting_next=False, in_quiz=False)
    clearFrame()

    makeLabel("✨ Maths Quiz ✨", 26, True).pack(pady=(10, 2))
    makeLabel("Ten little problems, you've got this! 🌈", 11).pack()
    makeLabel("Pick your level:", 13).pack(pady=10)

    # (level name, button text, button colour)
    options = [
        ("Easy", "🌱  Easy  (single-digit numbers)", MINT),
        ("Moderate", "🌸  Moderate  (double-digit numbers)", SKY),
        ("Advanced", "🔥  Advanced  (4-digit numbers)", PINK),
    ]
    for level, text, colour in options:
        # lvl=level captures the current value, otherwise every button would
        # start the last level in the loop.
        makeButton(text, colour, lambda lvl=level: startQuiz(lvl)).pack(pady=6)


def randomInt(level):
    """Return a random integer suited to the chosen difficulty level."""
    low, high = LEVELS[level]          # look up the allowed range for this level
    return random.randint(low, high)   # randint includes both end points


def decideOperation():
    """Randomly choose between addition and subtraction."""
    return random.choice(["+", "-"])


def displayProblem():
    """Generate a new problem and show it on screen."""
    state["question"] += 1        # move on to the next question number
    state["attempt"] = 1          # every new question starts on attempt 1
    state["waiting_next"] = False

    num1 = randomInt(state["level"])
    num2 = randomInt(state["level"])
    operation = decideOperation()

    # Work out and store the correct answer so isCorrect() can check it later.
    state["answer"] = num1 + num2 if operation == "+" else num1 - num2

    # Update the labels instead of rebuilding the screen (faster, no flicker).
    ui["progress"].config(text=f"Question {state['question']} of {TOTAL_QUESTIONS}")
    ui["hearts"].config(text=hearts(state["question"] - 1))
    ui["problem"].config(text=f"{num1} {operation} {num2} = ?")
    ui["feedback"].config(text="")
    ui["score"].config(text=f"⭐ Score: {state['score']}")
    ui["submit"].config(text="Submit 💌")

    # Re-enable and clear the entry box, then put the cursor in it.
    ui["entry"].config(state="normal")
    ui["entry"].delete(0, tk.END)
    ui["entry"].focus_set()


def isCorrect(user_answer):
    """Return True if the user's answer matches the current problem's answer."""
    return user_answer == state["answer"]


def displayResults():
    """Show the final score out of 100 with a grade, then offer to play again."""
    state["in_quiz"] = False
    score = state["score"]
    grade, message = gradeFor(score)

    clearFrame()
    makeLabel("🎉 Quiz Complete! 🎉", 24, True).pack(pady=(15, 8))
    makeLabel(f"Difficulty: {state['level']}", 13).pack()
    makeLabel(f"Final score: {score} / 100", 18).pack(pady=8)

    # The grade sits in a lavender "badge" to make it stand out.
    tk.Label(content, text=f"Grade: {grade}", font=(FONT, 22, "bold"),
             bg=LAVENDER, fg=TEXT, padx=20, pady=6).pack(pady=6)
    makeLabel(message, 13).pack(pady=6)
    root.update_idletasks()   # draw the results now so they are visible behind the dialog

    # Prompt the user to play again.
    if messagebox.askyesno("Play again? 💖", "That was fun! Would you like to play again?"):
        displayMenu()          # back to the difficulty menu
    else:
        messagebox.showinfo("Bye bye! 👋", "Thanks for playing, see you soon!")
        root.destroy()         # close the program

# Helper functions

def gradeFor(score):
    """Convert a score out of 100 into a (letter grade, cute message) pair."""
    if score >= 90:
        return "A+", "Superstar! 🌟"
    if score >= 80:
        return "A", "Fantastic work! 🎀"
    if score >= 70:
        return "B", "Great job! 🌸"
    if score >= 60:
        return "C", "Nice effort! 🍀"
    if score >= 50:
        return "D", "Keep practising, you're getting there! 🌱"
    return "F", "Every wizard starts somewhere, try again! 🪄"


def startQuiz(level):
    """Build the quiz screen and start the first problem."""
    state.update(level=level, score=0, question=0, in_quiz=True)
    clearFrame()

    # Progress, hearts and score labels at the top of the screen.
    ui["progress"] = makeLabel(size=12)
    ui["progress"].pack(pady=(0, 0))
    ui["hearts"] = makeLabel(size=11)
    ui["hearts"].pack()
    ui["score"] = makeLabel(size=12)
    ui["score"].pack()

    # The big arithmetic problem in the middle.
    ui["problem"] = makeLabel(size=32, bold=True)
    ui["problem"].pack(pady=15)

    # Entry box for the answer; the lavender border appears when it has focus.
    ui["entry"] = tk.Entry(content, font=(FONT, 18), width=10, justify="center",
                           bg="white", fg=TEXT, relief="flat",
                           highlightthickness=2, highlightbackground=SKY,
                           highlightcolor=LAVENDER)
    ui["entry"].pack()

    # Feedback message (correct / try again / wrong); wraplength stops it overflowing.
    ui["feedback"] = tk.Label(content, font=(FONT, 12), bg=BG, wraplength=420)
    ui["feedback"].pack(pady=10)

    # The same button is used for "Submit" and "Next Question".
    ui["submit"] = makeButton("Submit 💌", PEACH, onSubmit, width=18)
    ui["submit"].pack()

    displayProblem()


def onSubmit():
    """Handle the Submit / Next button (also triggered by the Enter key)."""
    # After a finished question the same button moves on to the next one.
    if state["waiting_next"]:
        if state["question"] >= TOTAL_QUESTIONS:
            displayResults()      # that was the last question
        else:
            displayProblem()
        return

    # Make sure the input is a whole number (negative numbers are allowed).
    try:
        user_answer = int(ui["entry"].get().strip())
    except ValueError:
        ui["feedback"].config(text="Please type a whole number 🔢", fg=WARN)
        return

    if isCorrect(user_answer):
        # 10 points on the first attempt, 5 on the second.
        points = FIRST_TRY_POINTS if state["attempt"] == 1 else SECOND_TRY_POINTS
        state["score"] += points
        ui["feedback"].config(text=f"{random.choice(CORRECT_MESSAGES)} 🎀  +{points} points", fg=GOOD)
        finishQuestion()
    elif state["attempt"] == 1:
        # Wrong on the first try: give one more chance.
        state["attempt"] = 2
        ui["feedback"].config(text=f"{random.choice(RETRY_MESSAGES)} 💪", fg=BAD)
        ui["entry"].delete(0, tk.END)
    else:
        # Wrong on the second try: reveal the answer.
        ui["feedback"].config(
            text=f"{random.choice(WRONG_MESSAGES)} The answer was {state['answer']} 🌧️", fg=BAD)
        finishQuestion()


def finishQuestion():
    """Lock the entry box and turn the button into 'Next' (or 'See Results')."""
    state["waiting_next"] = True
    ui["score"].config(text=f"⭐ Score: {state['score']}")
    ui["hearts"].config(text=hearts(state["question"]))   # fill in this question's heart
    ui["entry"].config(state="disabled")                  # stop further typing
    last = state["question"] >= TOTAL_QUESTIONS
    ui["submit"].config(text="See Results 🎉" if last else "Next Question ➡️")


def onEnter(_event):
    """Allow the Enter key to act as the Submit / Next button during a quiz."""
    if state["in_quiz"]:
        onSubmit()

# Program entry point

if __name__ == "__main__":
    root.bind("<Return>", onEnter)   # listen for the Enter key anywhere in the window
    displayMenu()                    # show the difficulty menu first
    root.mainloop()                  # hand control to Tkinter's event loop