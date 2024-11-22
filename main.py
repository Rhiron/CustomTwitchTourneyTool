import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import obsws_python as obs
import os

# OBS WebSocket connection details
OBS_HOST = "localhost"  # Default localhost
OBS_PORT = 4455         # Default WebSocket port
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIRECTORY = os.path.join(BASE_DIR, "StockIcons")
CONFIG_FILE_PATH = os.path.join(BASE_DIR, "config.txt")

# OBS source names
PLAYER_1_SOURCE = "Player1Name"
PLAYER_2_SOURCE = "Player2Name"
PLAYER_1_IMAGE_SOURCE = "Player1Image"
PLAYER_2_IMAGE_SOURCE = "Player2Image"
SET_COUNT_SOURCE = "SetCount"

def get_obs_password():
    """Read OBS password from the config file or prompt the user."""
    try:
        with open(CONFIG_FILE_PATH, "r") as f:
            for line in f:
                if line.startswith("OBS_PASSWORD="):
                    return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        print("config.txt not found.")
        return prompt_for_password()

def save_obs_password(password):
    """Save the OBS password to the config file."""
    try:
        with open(CONFIG_FILE_PATH, "w") as f:
            f.write(f"OBS_PASSWORD={password}\n")
        print("OBS password saved to config.txt.")
    except Exception as e:
        print(f"Failed to save OBS password: {e}")
        messagebox.showerror("Error", "Failed to save OBS password.")

def prompt_for_password():
    """Prompt the user for the OBS password using a GUI."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    password = simpledialog.askstring("OBS Password", "Enter your OBS WebSocket password:", show='*')
    if password:
        save_obs_password(password)
    return password or ""

def connect_to_obs(password):
    """Connect to OBS WebSocket."""
    try:
        client = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=password)
        print("Connected to OBS.")
        return client
    except Exception as e:
        print(f"Failed to connect to OBS: {e}")
        messagebox.showerror("Error", "Failed to connect to OBS. Check your settings.")
        return None

def update_obs_text(client, source, text):
    """Update OBS text source."""
    try:
        client.set_input_settings(source, {"text": text}, overlay=True)
        print(f"Updated {source} to {text}")
    except Exception as e:
        print(f"Failed to update OBS text source: {e}")

def update_obs_image(client, source, image_name):
    """Update OBS image source."""
    try:
        image_path = os.path.join(IMAGE_DIRECTORY, f"{image_name}.png")
        if os.path.exists(image_path):
            client.set_input_settings(source, {"file": image_path}, overlay=True)
            print(f"Updated {source} to {image_name}")
        else:
            print(f"Image not found: {image_path}")
    except Exception as e:
        print(f"Failed to update OBS image source: {e}")

def on_update():
    """Handle update button click."""
    password = get_obs_password()
    client = connect_to_obs(password)
    if not client:
        return

    # Player 1
    player1_name = player1_name_var.get()
    player1_char = player1_char_var.get()
    update_obs_text(client, PLAYER_1_SOURCE, player1_name)
    update_obs_image(client, PLAYER_1_IMAGE_SOURCE, player1_char)

    # Player 2
    player2_name = player2_name_var.get()
    player2_char = player2_char_var.get()
    update_obs_text(client, PLAYER_2_SOURCE, player2_name)
    update_obs_image(client, PLAYER_2_IMAGE_SOURCE, player2_char)

    # Set Count
    set_count = f"{set_count_1_var.get()} - {set_count_2_var.get()}"
    update_obs_text(client, SET_COUNT_SOURCE, set_count)

    messagebox.showinfo("Success", "Updated OBS successfully.")

# Tkinter GUI Setup
root = tk.Tk()
root.title("OBS Stream Manager")
root.geometry("400x400")

# Dropdown options
character_options = [os.path.splitext(f)[0] for f in os.listdir(IMAGE_DIRECTORY) if f.endswith(".png")]

# Player 1
tk.Label(root, text="Player 1").grid(row=0, column=0, pady=5)
player1_name_var = tk.StringVar(value="Player 1")
tk.Entry(root, textvariable=player1_name_var).grid(row=0, column=1)
player1_char_var = tk.StringVar(value=character_options[0] if character_options else "")
tk.Label(root, text="Character").grid(row=0, column=2)
ttk.Combobox(root, textvariable=player1_char_var, values=character_options).grid(row=0, column=3)

# Player 2
tk.Label(root, text="Player 2").grid(row=1, column=0, pady=5)
player2_name_var = tk.StringVar(value="Player 2")
tk.Entry(root, textvariable=player2_name_var).grid(row=1, column=1)
player2_char_var = tk.StringVar(value=character_options[0] if character_options else "")
tk.Label(root, text="Character").grid(row=1, column=2)
ttk.Combobox(root, textvariable=player2_char_var, values=character_options).grid(row=1, column=3)

# Set Count
tk.Label(root, text="Set Count").grid(row=2, column=0, pady=5)
set_count_1_var = tk.StringVar(value="0")
tk.Entry(root, textvariable=set_count_1_var, width=5).grid(row=2, column=1)
tk.Label(root, text="-").grid(row=2, column=2)
set_count_2_var = tk.StringVar(value="0")
tk.Entry(root, textvariable=set_count_2_var, width=5).grid(row=2, column=3)

# Update Button
tk.Button(root, text="Update OBS", command=on_update).grid(row=3, column=0, columnspan=4, pady=20)

root.mainloop()
