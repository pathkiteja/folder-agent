import tkinter as tk
from tkinter import simpledialog, messagebox
import os
import subprocess
import shutil  # for shutil.which()

def select_extensions_dialog(root, extension_list):
    top = tk.Toplevel(root)
    top.title("Select Extensions")

    var_dict = {}
    for ext in extension_list:
        var = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(top, text=ext, variable=var)
        chk.pack(anchor=tk.W, padx=10, pady=2)
        var_dict[ext] = var

    chosen_exts = []

    def on_ok():
        for ext, v in var_dict.items():
            if v.get():
                chosen_exts.append(ext)
        top.destroy()

    tk.Button(top, text="OK", command=on_ok).pack(pady=5)
    top.grab_set()
    root.wait_window(top)
    return chosen_exts

def input_filenames_dialog(root, chosen_exts):
    if not chosen_exts:
        return []
    top = tk.Toplevel(root)
    top.title("File Names")

    entries = {}
    for ext in chosen_exts:
        frame = tk.Frame(top)
        frame.pack(anchor=tk.W, padx=10, pady=2)

        lbl = tk.Label(frame, text=f"Filename for {ext}:")
        lbl.pack(side=tk.LEFT)

        ent = tk.Entry(frame, width=20)
        ent.pack(side=tk.LEFT, padx=5)
        entries[ext] = ent

    filenames = []

    def on_ok():
        for ext, ent in entries.items():
            base_name = ent.get().strip()
            if base_name:
                filenames.append(base_name + ext)
        top.destroy()

    tk.Button(top, text="OK", command=on_ok).pack(pady=5)
    top.grab_set()
    root.wait_window(top)

    return filenames

def open_in_vscode(folder_path):
    """
    Attempt to open the given folder in VS Code.
    1) First try "code"
    2) If not found, fall back to a hard-coded path (update for your system!)
    """
    # 1) Try "code" on PATH
    if shutil.which("code"):
        # "code" is found on the PATH
        try:
            subprocess.Popen(["code", folder_path])
            return
        except Exception as e:
            # If some other error occurs, we'll try fallback
            print("Error using 'code' from PATH:", e)

    # 2) Fallback path (you must update this to your actual code.exe location)
    fallback_path = r"C:\Users\Teja\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"
    if os.path.isfile(fallback_path):
        try:
            subprocess.Popen([fallback_path, folder_path])
            return
        except Exception as e:
            print("Error using fallback path:", e)

    # 3) If all else fails, show error
    messagebox.showerror(
        "Error",
        "Could not open VS Code.\n\n"
        "1) Ensure 'code' is on your PATH, or\n"
        f"2) Update the fallback_path to match your code.exe location."
    )

def create_project():
    base_path = r"C:\programming\Test"

    folder_name = simpledialog.askstring("Folder Name", "Enter the new folder name:")
    if not folder_name:
        return

    extension_list = [".py", ".html", ".css", ".js", ".md", ".txt", 
                      ".json", ".xml", ".yml", ".csv"]
    chosen_exts = select_extensions_dialog(root, extension_list)

    selected_files = input_filenames_dialog(root, chosen_exts)

    if not selected_files:
        summary_text = (
            f"Folder path: {base_path}\n"
            f"Folder name: {folder_name}\n"
            "No files selected."
        )
    else:
        summary_text = (
            f"Folder path: {base_path}\n"
            f"Folder name: {folder_name}\n"
            "Files to be created:\n" +
            "\n".join(["  - " + f for f in selected_files])
        )

    confirm = messagebox.askyesno("Summary", summary_text + "\n\nCreate now?")
    if not confirm:
        return

    final_folder_path = os.path.join(base_path, folder_name)
    os.makedirs(final_folder_path, exist_ok=True)

    for filename in selected_files:
        file_path = os.path.join(final_folder_path, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            pass  # Empty file or add template text if needed

    # Attempt to open in VS Code using our function
    open_in_vscode(final_folder_path)

def main():
    global root
    root = tk.Tk()
    root.title("Local AI Agent")

    create_button = tk.Button(root, text="Create Project", command=create_project)
    create_button.pack(padx=30, pady=30)

    root.mainloop()

if __name__ == "__main__":
    main()
