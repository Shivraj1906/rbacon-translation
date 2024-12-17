from tkinter import *
import tkinter as tk
from tkinter import filedialog
from src.Bacon import Bacon
from tkinter import ttk
import threading
from pandastable import Table
import pandas as pd
from tkinter import messagebox

class CoreGUI(object):
    def __init__(self, parent):
        self.parent = parent
        self.bacon_model = None  # Initialize the Bacon model as None
        self.InitUI()

    def InitUI(self):
        self.mainframe = tk.Frame(self.parent)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        self.leftframe = tk.Frame(self.mainframe)
        self.leftframe.grid(column=0, row=0, sticky=(N, S, W, E))
        self.rightframe = tk.Frame(self.mainframe)
        self.rightframe.grid(column=1, row=0, sticky=(N, E, S, W))

        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.rowconfigure(0, weight=1)

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self.leftframe, textvariable=self.entry_var, state='readonly', width=50)
        self.entry.grid(column=0, row=0, padx=10, pady=10, sticky=(W, E))

        browse_button = tk.Button(self.leftframe, text="Browse", command=self.browse_file)
        browse_button.grid(column=1, row=0, padx=10, pady=10, sticky=(W))

        self.table_frame = tk.Frame(self.leftframe)
        self.table_frame.grid(column=0, row=1, columnspan=2, padx=10, pady=30, sticky=(N, S, W, E))

        self.placeholder_frame = tk.Frame(self.table_frame, bg="lightgrey")
        self.placeholder_frame.grid(column=0, row=0, padx=10, pady=10, sticky=(N, W, E, S))
        placeholder_label = tk.Label(self.placeholder_frame, text="No CSV file selected", bg="lightgrey")
        placeholder_label.grid(column=0, row=0, sticky=(N, W, E, S))

        # Parameters section
        self.params_frame = tk.LabelFrame(self.rightframe, text="Parameters", padx=10, pady=10, font=("TkDefaultFont", 10, "bold"))
        self.params_frame.grid(column=0, row=0, padx=10, pady=10, sticky=(W, E))

        tk.Label(self.params_frame, text="Core Name*:").grid(column=0, row=0, sticky=W)
        self.core_name_entry = tk.Entry(self.params_frame, width=20)
        self.core_name_entry.grid(column=1, row=0, padx=5, pady=5)

        tk.Label(self.params_frame, text="Accumulation Mean (default=20):").grid(column=0, row=1, sticky=W)
        self.acc_mean_entry = tk.Entry(self.params_frame, width=20)
        self.acc_mean_entry.grid(column=1, row=1, padx=5, pady=5)

        tk.Label(self.params_frame, text="Accumulation Shape (default=1.5):").grid(column=0, row=2, sticky=W)
        self.acc_shape_entry = tk.Entry(self.params_frame, width=20)
        self.acc_shape_entry.grid(column=1, row=2, padx=5, pady=5)

        tk.Label(self.params_frame, text="Memory Strength (default=10):").grid(column=0, row=3, sticky=W)
        self.mem_strength_entry = tk.Entry(self.params_frame, width=20)
        self.mem_strength_entry.grid(column=1, row=3, padx=5, pady=5)

        tk.Label(self.params_frame, text="Memory Mean (default=0.5):").grid(column=0, row=4, sticky=W)
        self.mem_mean_entry = tk.Entry(self.params_frame, width=20)
        self.mem_mean_entry.grid(column=1, row=4, padx=5, pady=5)

        # Subframe for buttons
        self.button_frame = tk.Frame(self.params_frame)
        self.button_frame.grid(column=0, row=5, columnspan=2, pady=10, sticky=(E, W))

        button_run = Button(self.button_frame, text="Run Model", command=self.run_model)
        button_run.grid(column=0, row=0, padx=10, sticky=E)
        button_inspect = Button(self.button_frame, text="Inspect Run", command=self.inspect_run)
        button_inspect.grid(column=1, row=0, padx=10, sticky=E)

        self.params_frame.columnconfigure(0, weight=1)

        # Postrun Analysis section
        self.postrun_frame = tk.LabelFrame(self.rightframe, text="Predict Age", padx=10, pady=10, font=("TkDefaultFont", 10, "bold"))
        self.postrun_frame.grid(column=0, row=1, padx=10, pady=10, sticky=(W, E))

        tk.Label(self.postrun_frame, text="Enter depth (cm):").grid(column=0, row=0, sticky=W)
        self.predict_age_entry = tk.Entry(self.postrun_frame, width=20, validate="key", validatecommand=(self.parent.register(self.validate_numeric), '%P'))
        self.predict_age_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(W, E))
        button_predict = Button(self.postrun_frame, text="Predict", command=self.predict_age)
        button_predict.grid(column=2, row=0, padx=5, pady=5, sticky=E)

        self.postrun_frame.columnconfigure(1, weight=1)

        # Timespan between two depths section
        self.timespan_frame = tk.LabelFrame(self.rightframe, text="Timespan Between Two Depths", padx=10, pady=10, font=("TkDefaultFont", 10, "bold"))
        self.timespan_frame.grid(column=0, row=2, padx=10, pady=10, sticky=(W, E))

        tk.Label(self.timespan_frame, text="Enter depths (cm):").grid(column=0, row=0, sticky=W)
        self.depth1_entry = tk.Entry(self.timespan_frame, width=10, validate="key", validatecommand=(self.parent.register(self.validate_numeric), '%P'))
        self.depth1_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(W, E))
        tk.Label(self.timespan_frame, text="-").grid(column=2, row=0, sticky=W)
        self.depth2_entry = tk.Entry(self.timespan_frame, width=10, validate="key", validatecommand=(self.parent.register(self.validate_numeric), '%P'))
        self.depth2_entry.grid(column=3, row=0, padx=5, pady=5, sticky=(W, E))
        button_timespan = Button(self.timespan_frame, text="Predict", command=self.predict_timespan)
        button_timespan.grid(column=4, row=0, padx=5, pady=5, sticky=E)

        self.timespan_frame.columnconfigure(1, weight=1)

        # Accumulation rate section
        self.acc_rate_frame = tk.LabelFrame(self.rightframe, text="Accumulation Rate", padx=10, pady=10, font=("TkDefaultFont", 10, "bold"))
        self.acc_rate_frame.grid(column=0, row=3, padx=10, pady=10, sticky=(W, E))

        tk.Label(self.acc_rate_frame, text="Depth (cm):").grid(column=0, row=0, sticky=W)
        self.acc_rate_entry = tk.Entry(self.acc_rate_frame, width=20, validate="key", validatecommand=(self.parent.register(self.validate_numeric), '%P'))
        self.acc_rate_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(W, E))
        button_acc_rate = Button(self.acc_rate_frame, text="Predict", command=self.predict_acc_rate)
        button_acc_rate.grid(column=2, row=0, padx=5, pady=5, sticky=E)
        self.acc_rate_frame.columnconfigure(1, weight=1)

        self.chart_frame = tk.Frame(self.rightframe)
        self.chart_frame.grid(column=0, row=4, padx=10, pady=10, sticky=(W, E))

        self.leftframe.rowconfigure(1, weight=1)
        self.leftframe.columnconfigure(0, weight=1)

    def validate_numeric(self, value_if_allowed):
        if value_if_allowed.isdigit() or value_if_allowed == "":
            return True
        else:
            return False

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.entry_var.set(file_path)
            self.display_csv_content(file_path)
        else:
            self.show_placeholder()

    def display_csv_content(self, file_path):
        df = pd.read_csv(file_path)
        self.table = Table(self.table_frame, dataframe=df, showtoolbar=False, showstatusbar=False, editable=False)
        self.table.show()
        self.placeholder_frame.grid_forget()

    def show_placeholder(self):
        self.placeholder_frame.grid(column=0, row=0, sticky=(N, W, E, S))

    def run_model(self):
        if not self.core_name_entry.get().strip():
            tk.messagebox.showerror("Input Error", "Core Name is required.")
            return
        if not self.entry_var.get().strip():
            tk.messagebox.showerror("Input Error", "File path is required.")
            return
        try:
            acc_mean = float(self.acc_mean_entry.get())
        except ValueError:
            acc_mean = 20

        try:
            acc_shape = float(self.acc_shape_entry.get())
        except ValueError:
            acc_shape = 1.5

        try:
            mem_strength = float(self.mem_strength_entry.get())
        except ValueError:
            mem_strength = 10

        try:
            mem_mean = float(self.mem_mean_entry.get())
        except ValueError:
            mem_mean = 0.5

        file_path = self.entry_var.get().strip()
        core_name = self.core_name_entry.get().strip()

        def run_bacon_model():
            self.bacon_model = Bacon(file_path, core_name, acc_mean=acc_mean, acc_shape=acc_shape, mem_strength=mem_strength, mem_mean=mem_mean)
            self.parent.after(0, on_model_run_complete)

        def on_model_run_complete():
            progress.stop()
            progress_window.destroy()
            tk.messagebox.showinfo("Success", "Model run completed.")

        # Create a popup for the progress bar
        progress_window = tk.Toplevel(self.parent)
        progress_window.title("Running Model")
        progress_window.geometry("300x100")
        progress_window.transient(self.parent)  # Set to be on top of the main window
        progress_window.grab_set()  # Prevent interaction with the main window
        progress_window.focus_set()  # Set focus on the popup

        tk.Label(progress_window, text="Model is running, please wait...").grid(column=0, row=0, padx=10, pady=10)
        progress = ttk.Progressbar(progress_window, orient=tk.HORIZONTAL, length=200, mode='indeterminate')
        progress.grid(column=0, row=1, padx=10, pady=10)
        progress.start()

        # Run the model in a separate thread
        thread = threading.Thread(target=run_bacon_model)
        thread.start()

    def predict_age(self):
        if self.bacon_model is None:
            tk.messagebox.showerror("Error", "Model has not been run yet.")
            return
        try:
            depth = float(self.predict_age_entry.get())
            self.bacon_model.predict_age(depth)
        except ValueError:
            tk.messagebox.showerror("Input Error", "Please enter a valid number for depth.")

    def predict_timespan(self):
        if self.bacon_model is None:
            tk.messagebox.showerror("Error", "Model has not been run yet.")
            return
        try:
            depth1 = float(self.depth1_entry.get())
            depth2 = float(self.depth2_entry.get())
            self.bacon_model.predict_timespan(depth1, depth2)
        except ValueError:
            tk.messagebox.showerror("Input Error", "Please enter valid numbers for depths.")

    def predict_acc_rate(self):
        if self.bacon_model is None:
            tk.messagebox.showerror("Error", "Model has not been run yet.")
            return
        try:
            depth = float(self.acc_rate_entry.get())
            self.bacon_model.predict_acc_rate(depth)
        except ValueError:
            tk.messagebox.showerror("Input Error", "Please enter a valid number for depth.")

    def inspect_run(self):
        if not self.core_name_entry.get().strip():
            tk.messagebox.showerror("Input Error", "Core Name is required.")
            return
        if self.bacon_model is None:
            tk.messagebox.showerror("Error", "Model has not been run yet.")
            return
        self.bacon_model.inspect_run()