import os                          # used to build a reliable path to the data file
import tkinter as tk               # the GUI toolkit
from tkinter import messagebox     # pop-up dialogs for errors and hints

# Locate the data file next to this script, wherever it is run from.
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "studentMarks.txt")
TOTAL_MARKS = 160  # 60 coursework marks + 100 exam marks

# Pastel colour palette (change colours here and the whole app updates).
BG = "#FFF5EE"        # cream window background
PANEL = "#F3E8FF"     # soft lilac side menu
OUTPUT_BG = "#FFFDF9" # near-white output area (easy on the eyes)
TEXT = "#4A4A68"      # dark slate-purple text
MINT = "#B5EAD7"      # view-all button
SKY = "#BDE0FE"       # lookup button
PINK = "#FFC8DD"      # highest / lowest buttons
PEACH = "#FFDAC1"     # quit button
LAVENDER = "#CDB4DB"  # hover colour and borders

FONT = "Comic Sans MS"     # round, friendly font for labels and buttons
MONO = "Courier New"       # monospaced font so table columns line up

# A little emoji for each grade, shown at the end of each table row
# (placed last so the emoji width cannot push the columns out of line).
GRADE_EMOJI = {"A": "🌟", "B": "🌸", "C": "🍀", "D": "🌱", "F": "🌧️"}

# Data handling (no GUI code here, which keeps the logic easy to test)

def gradeFor(percentage):
    """Convert an overall percentage into a letter grade."""
    if percentage >= 70:
        return "A"
    if percentage >= 60:
        return "B"
    if percentage >= 50:
        return "C"
    if percentage >= 40:
        return "D"
    return "F"


def loadStudents(path):
    """Read the file and return a list of student dictionaries."""
    students = []
    with open(path, "r", encoding="utf-8") as file:
        # Strip each line and ignore completely blank ones.
        lines = [line.strip() for line in file if line.strip()]

    # Line 1 is the declared number of students; the rest are records.
    # (We trust the records themselves in case the count is wrong.)
    for line in lines[1:]:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 6:
            continue  # skip malformed lines
        code, name = parts[0], parts[1]
        try:
            # Convert the four mark fields to integers in one go.
            m1, m2, m3, exam = (int(p) for p in parts[2:])
        except ValueError:
            continue  # skip lines where a mark is not a number

        # Calculate everything once here so every menu option can reuse it.
        coursework = m1 + m2 + m3             # out of 60
        total = coursework + exam             # out of 160
        percentage = total / TOTAL_MARKS * 100
        students.append({
            "code": code, "name": name,
            "coursework": coursework, "exam": exam,
            "total": total, "percentage": percentage,
            "grade": gradeFor(percentage),
        })
    return students


def formatStudent(s):
    """Return a multi-line text block describing one student."""
    return (
        f"🎓 Name:               {s['name']}\n"
        f"🆔 Student ID:         {s['code']}\n"
        f"📝 Coursework total:   {s['coursework']} / 60\n"
        f"📚 Exam mark:          {s['exam']} / 100\n"
        f"⭐ Total score:        {s['total']} / {TOTAL_MARKS}\n"
        f"📊 Overall percentage: {s['percentage']:.1f}%\n"
        f"🏅 Grade:              {s['grade']} {GRADE_EMOJI[s['grade']]}\n"
    )

# GUI

class StudentManagerApp:
    """The main window: a menu on the left and an output area on the right."""

    def __init__(self, root, students):
        self.root = root
        self.students = students

        root.title("Student Manager")
        root.geometry("840x560")
        root.configure(bg=BG)

        # --- Left frame: menu buttons ---
        menu = tk.Frame(root, padx=12, pady=12, bg=PANEL)
        menu.pack(side="left", fill="y")
        tk.Label(menu, text="🎀 Menu 🎀", font=(FONT, 16, "bold"),
                 bg=PANEL, fg=TEXT).pack(pady=(0, 10))

        # (button text, colour, method to run when clicked)
        for text, colour, command in [
            ("📋 1. View all records", MINT, self.viewAll),
            ("🏆 3. Highest total score", PINK, self.showHighest),
            ("🌱 4. Lowest total score", PINK, self.showLowest),
        ]:
            self.makeButton(menu, text, colour, command).pack(pady=4)

        # Individual lookup: label + search box + button (option 2).
        tk.Label(menu, text="🔍 2. Individual record\n(name or ID):",
                 font=(FONT, 10), bg=PANEL, fg=TEXT).pack(pady=(20, 2))
        self.search_entry = tk.Entry(menu, width=24, bg="white", fg=TEXT, relief="flat",
                                    highlightthickness=2, highlightbackground=SKY,
                                    highlightcolor=LAVENDER)
        self.search_entry.pack(pady=2)
        # Pressing Enter in the box works the same as clicking the button.
        self.search_entry.bind("<Return>", lambda e: self.viewIndividual())
        self.makeButton(menu, "💕 View student", SKY, self.viewIndividual).pack(pady=4)

        # Quit button pinned to the bottom of the menu.
        self.makeButton(menu, "👋 Quit", PEACH, self.quitApp).pack(side="bottom", pady=4)

        # --- Right frame: read-only output area with a scrollbar ---
        output = tk.Frame(root, padx=12, pady=12, bg=BG)
        output.pack(side="right", fill="both", expand=True)
        scrollbar = tk.Scrollbar(output)
        scrollbar.pack(side="right", fill="y")

        # A Text widget supports multi-line output; the monospaced font keeps
        # table columns lined up. It is disabled so users cannot edit it.
        self.text = tk.Text(output, font=(MONO, 10), wrap="none",
                            yscrollcommand=scrollbar.set, state="disabled",
                            bg=OUTPUT_BG, fg=TEXT, relief="flat", padx=10, pady=10,
                            highlightthickness=2, highlightbackground=LAVENDER)
        self.text.pack(fill="both", expand=True)
        scrollbar.config(command=self.text.yview)   # link the scrollbar to the text

        # Welcome message shown on start-up.
        self.show(f"Hello! 👋\n\nI've loaded {len(students)} students for you. 🎓\n"
                  "Pick an option from the menu to get started! 💖")

    @staticmethod
    def makeButton(parent, text, colour, command):
        """Create a flat pastel button with a lavender click/hover colour."""
        return tk.Button(parent, text=text, width=24, font=(FONT, 10),
                         bg=colour, fg=TEXT, activebackground=LAVENDER,
                         relief="flat", bd=0, pady=5, cursor="hand2", command=command)

    def show(self, message):
        """Replace the contents of the output area with a message."""
        self.text.config(state="normal")    # unlock so we can change the text
        self.text.delete("1.0", tk.END)     # clear the old contents
        self.text.insert(tk.END, message)   # insert the new message
        self.text.config(state="disabled")  # lock again to prevent editing

    def quitApp(self):
        """Say goodbye, then close the application."""
        messagebox.showinfo("Bye bye! 👋", "See you next time! 💖")
        self.root.destroy()

    # --- Option 1 ---
    def viewAll(self):
        """Show every student in a table plus class size and average."""
        # Header row; "<22" means left-align in 22 chars, ">5" right-align in 5.
        header = f"{'Name':<22}{'ID':<8}{'CW':>5}{'Exam':>6}{'%':>8}{'Grade':>7}\n"
        lines = ["📋 All student records\n\n", header, "-" * 56 + "\n"]
        for s in self.students:
            lines.append(
                f"{s['name']:<22}{s['code']:<8}{s['coursework']:>5}{s['exam']:>6}"
                f"{s['percentage']:>8.1f}{s['grade']:>7} {GRADE_EMOJI[s['grade']]}\n"
            )
        # Average of every student's overall percentage.
        average = sum(s["percentage"] for s in self.students) / len(self.students)
        lines.append("-" * 56 + "\n")
        lines.append(f"👩‍🎓 Class size:         {len(self.students)}\n")
        lines.append(f"📊 Average percentage: {average:.1f}%\n")
        lines.append("\n(CW = coursework total out of 60, Exam out of 100, % out of 160)")
        self.show("".join(lines))

    # --- Option 2 ---
    def viewIndividual(self):
        """Find a student by exact ID or by (partial, case-insensitive) name."""
        query = self.search_entry.get().strip().lower()
        if not query:
            messagebox.showinfo("Search 🔍", "Please type a student name or ID first! 💌")
            return

        # Match on exact ID, or on any part of the name.
        matches = [s for s in self.students
                   if s["code"].lower() == query or query in s["name"].lower()]
        if not matches:
            self.show(f"Oh no! 🥺 I couldn't find anyone matching '{query}'.")
        else:
            self.show("\n".join(formatStudent(s) for s in matches))

    # --- Options 3 and 4 ---
    def showHighest(self):
        """max() with a key function finds the student with the biggest total."""
        best = max(self.students, key=lambda s: s["total"])
        self.show("🏆 Our top scorer! Congratulations! 🎉\n\n" + formatStudent(best))

    def showLowest(self):
        """min() with a key function finds the student with the smallest total."""
        worst = min(self.students, key=lambda s: s["total"])
        self.show("🌱 Lowest total score. Let's cheer them on! 💪\n\n" + formatStudent(worst))


def main():
    """Load the data, then start the app (or show an error if loading fails)."""
    root = tk.Tk()
    try:
        students = loadStudents(DATA_FILE)
    except FileNotFoundError:
        messagebox.showerror("File not found", f"Could not find:\n{DATA_FILE}")
        root.destroy()
        return

    if not students:
        messagebox.showerror("No data", "studentMarks.txt contains no valid records.")
        root.destroy()
        return

    StudentManagerApp(root, students)
    root.mainloop()        # start Tkinter's event loop


if __name__ == "__main__":
    main()