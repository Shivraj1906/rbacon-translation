from tkinter import *
from src.CoreGUI import CoreGUI

if __name__ == "__main__":
    root = Tk()
    root.title("Bacon Age-Depth Model")
    root.resizable(False, False)  # Disable window resizing
    gui = CoreGUI(root)
    root.mainloop()