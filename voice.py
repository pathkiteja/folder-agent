import tkinter as tk
import threading
import speech_recognition as sr
import os
import subprocess
import shutil
import time

############################################################
# CONFIGURATION
############################################################

BASE_PATH = r"C:\programming\Test"  # Where new folders will be created
FALLBACK_VSCODE_PATH = r"C:\Users\Teja\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"

# A list of valid extensions we'll accept (add/remove if needed)
VALID_EXTENSIONS = [".py", ".html", ".css", ".js", ".md", ".txt", ".json", ".xml", ".yml", ".csv"]

############################################################
# SPEECH + HELPER FUNCTIONS
############################################################

def listen_for_speech(timeout=5):
    """
    Listen to the microphone for up to `timeout` seconds.
    Return recognized text in lowercase, or None if not understood.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # Log to UI that we are listening
        log_to_ui("Listening... (up to {}s)".format(timeout))
        audio = r.listen(source, phrase_time_limit=timeout)
    try:
        text = r.recognize_google(audio)
        text = text.lower().strip()
        log_to_ui(f"> You said: {text}")
        return text
    except sr.UnknownValueError:
        log_to_ui("> Sorry, I didn't catch that.")
        return None
    except sr.RequestError as e:
        log_to_ui(f"> Speech Recognition error: {e}")
        return None

def open_in_vscode(folder_path):
    """
    Attempt to open the folder in VS Code:
    1) Try 'code' from PATH
    2) Fallback to FALLBACK_VSCODE_PATH
    """
    if shutil.which("code"):
        # 'code' is on PATH
        try:
            subprocess.Popen(["code", folder_path])
            return
        except Exception as e:
            log_to_ui(f"Error using 'code' from PATH: {e}")

    if os.path.isfile(FALLBACK_VSCODE_PATH):
        try:
            subprocess.Popen([FALLBACK_VSCODE_PATH, folder_path])
            return
        except Exception as e:
            log_to_ui(f"Error using fallback path: {e}")

    log_to_ui("Could not open VS Code. Update PATH or FALLBACK_VSCODE_PATH.")

############################################################
# TKINTER UI
############################################################

root = tk.Tk()
root.title("Voice-Driven Folder Creator")

# A simple Text widget to show logs/instructions
log_widget = tk.Text(root, width=70, height=20)
log_widget.pack(padx=10, pady=10)

def log_to_ui(message):
    """
    Print a message to the Tkinter Text widget (and console), 
    then scroll to the end.
    """
    print(message)
    log_widget.insert(tk.END, message + "\n")
    log_widget.see(tk.END)
    root.update_idletasks()

############################################################
# MAIN VOICE FLOW (RUNS IN A SEPARATE THREAD)
############################################################

def voice_flow():
    """
    Fully voice-driven flow:
      1. Ask user to say "folder" (to create a new folder) or "done" to exit.
      2. If folder, ask for folder name, create it, then ask if we want 
         to create extensions. 
      3. If yes, ask how many, then for each extension (format: ".py named main").
      4. Summarize, if user says "done," open in VS Code.
      5. Repeat if user wants more folders (optional).
    """
    log_to_ui("Welcome to the Voice-Driven Folder Creator!")
    log_to_ui(f"Folders will be created under: {BASE_PATH}")
    log_to_ui("Say 'folder' to create a new folder, or 'done' to exit.\n")

    while True:
        spoken = listen_for_speech()
        if not spoken:
            continue
        if "done" in spoken:
            log_to_ui("Okay, finishing up. No folder created. Exiting flow.")
            break

        if "folder" in spoken:
            # Step 1: Ask for folder name
            folder_name = None
            while not folder_name:
                log_to_ui("Please say the folder name now.")
                name_spoken = listen_for_speech()
                if name_spoken:
                    folder_name = name_spoken.replace(" ", "_")  # replace spaces w/ underscores
                    log_to_ui(f"Folder name set to: {folder_name}")

            # Create the folder
            final_folder_path = os.path.join(BASE_PATH, folder_name)
            os.makedirs(final_folder_path, exist_ok=True)
            log_to_ui(f"Folder created at: {final_folder_path}")

            # Step 2: Ask if we want to create extensions
            log_to_ui("Do you want to create any extensions in this folder? Say 'yes' or 'no'.")
            wants_extensions = False
            while True:
                ans = listen_for_speech()
                if not ans:
                    continue
                if "yes" in ans:
                    wants_extensions = True
                    break
                elif "no" in ans:
                    break
                else:
                    log_to_ui("Please say 'yes' or 'no'.")

            file_list = []
            if wants_extensions:
                # Step 3: how many?
                log_to_ui("How many extensions do you want to create? (say a number)")
                num_ext = 0
                while True:
                    num_spoken = listen_for_speech()
                    if not num_spoken:
                        continue
                    # try to parse integer
                    try:
                        num_ext = int(num_spoken)
                        if num_ext <= 0:
                            log_to_ui("Number must be > 0. Try again.")
                            continue
                        break
                    except ValueError:
                        log_to_ui("Could not parse a valid number. Try again.")

                # Now ask for each extension
                for i in range(num_ext):
                    while True:
                        log_to_ui(f"Extension #{i+1}: Say something like '.py named main'")
                        ext_spoken = listen_for_speech()
                        if not ext_spoken:
                            continue
                        # We expect format: ".py named main"
                        # parse it
                        if "named" in ext_spoken:
                            parts = ext_spoken.split("named")
                            ext_part = parts[0].strip()
                            name_part = parts[1].strip()
                            # Ensure ext_part is a valid extension
                            if (ext_part.startswith(".")) and (ext_part in VALID_EXTENSIONS):
                                filename = name_part + ext_part
                                file_list.append(filename)
                                log_to_ui(f"Added file: {filename}")
                                break
                            else:
                                log_to_ui("Extension not recognized or invalid. Please try again (e.g. '.py named main').")
                        else:
                            log_to_ui("Please include the word 'named'. E.g. '.py named main'.")

                # Create the files
                for f in file_list:
                    file_path = os.path.join(final_folder_path, f)
                    with open(file_path, "w", encoding="utf-8") as fp:
                        pass
                log_to_ui("Extensions created.")

            # Step 4: Summarize and ask if "done"
            log_to_ui("Summary of your folder and files:")
            log_to_ui(f"Folder: {folder_name}")
            if file_list:
                log_to_ui("Files:")
                for f in file_list:
                    log_to_ui(f" - {f}")
            else:
                log_to_ui("No files created.")

            log_to_ui("Say 'done' to open in VS Code, or say 'continue' to create another folder.")
            while True:
                final_ans = listen_for_speech()
                if not final_ans:
                    continue
                if "done" in final_ans:
                    open_in_vscode(final_folder_path)
                    log_to_ui("Done! Exiting flow.")
                    return
                elif "continue" in final_ans:
                    log_to_ui("Ok, let's create another folder. Say 'folder' or 'done' to exit.")
                    break
                else:
                    log_to_ui("Please say 'done' or 'continue'.")

        else:
            log_to_ui("Please say 'folder' to create a new folder or 'done' to exit.")

############################################################
# STARTUP
############################################################

def start_voice_thread():
    """
    Start the voice_flow in a background thread so we don't block the Tkinter mainloop.
    """
    t = threading.Thread(target=voice_flow, daemon=True)
    t.start()

# As soon as the UI appears, we begin the voice flow
root.after(1000, start_voice_thread)

# Run the Tkinter event loop
root.mainloop()
