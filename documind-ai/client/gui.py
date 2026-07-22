import tkinter as tk

window = tk.Tk()

window.title("DocuMind AI")
window.geometry("700x500")

title = tk.Label(
    window,
    text="Welcome to DocuMind AI",
    font=("Arial", 20)
)

title.pack(pady=20)

window.mainloop()
