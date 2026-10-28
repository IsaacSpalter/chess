import tkinter as tk
from tkinter import filedialog
import os

# Hide the main tkinter window that pops up automatically
# root = tk.Tk()
# root.withdraw()

# Open the file dialog and get the selected file path
file_path = filedialog.askopenfilename(
    initialdir="/",  # Optional: specify initial directory
    title="Select a file", # Optional: set dialog title
    filetypes=(("Text files", "*.txt"), ("All files", "*.*")) # Optional: filter file types
)

# Print the selected file path
if file_path:
    print("Selected file:", file_path)
    # You can now use the file_path variable to open the file, e.g.:
    # with open(file_path, 'r') as f:
    #     content = f.read()
else:
    print("No file selected.")
