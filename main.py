import customtkinter as ctk
from tkinter import simpledialog, messagebox
import obsws_python as obs
import os
import requests
from urllib.parse import urlparse



OBS_HOST = "localhost"
OBS_PORT = 4455
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STOCK_IMAGE_DIRECTORY = os.path.join(BASE_DIR, "StockIcons")
FRAME_IMAGE_DIRECTORY = os.path.join(BASE_DIR, "Char_PNGs")
CONFIG_FILE_PATH = os.path.join(BASE_DIR, "config.txt")
STARTGG_API_URL = "https://api.start.gg/gql/alpha"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def read_config():
    config = {}
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as f:
            for line in f:
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip()
    return config

def save_config(config):
    try:
        with open(CONFIG_FILE_PATH, "w") as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
        print("Config file updated successfully.")
    except Exception as e:
        print(f"Failed to save config file: {e}")
        messagebox.showerror("Error", "Failed to save the config file.")

def get_or_prompt_config_value(config, key, prompt_message):
    value = config.get(key)
    if not value:
        root = ctk.CTk()
        root.withdraw()
        value = simpledialog.askstring("Configuration", prompt_message)
        if value:
            config[key] = value
            save_config(config)
    return value


def fetch_startgg_data(query, variables=None):
    headers = {
        "Authorization": f"Bearer {STARTGG_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": query,
        "variables": variables or {}
    }

    try:
        response = requests.post(STARTGG_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        return None
    
def get_event_entrants(event_id, page=1, per_page=20):
    query = """
    query EventEntrants($eventId: ID!, $page: Int!, $perPage: Int!) {
      event(id: $eventId) {
        id
        name
        entrants(query: { page: $page, perPage: $perPage }) {
          nodes {
            id
            participants {
              id
              gamerTag
            }
          }
        }
      }
    }
    """
    variables = {
        "eventId": event_id,
        "page": page,
        "perPage": per_page
    }

    data = fetch_startgg_data(query, variables)
    if data:
        entrants = data["data"]["event"]["entrants"]["nodes"]
        return [{"id": node["id"], "gamerTags": [p["gamerTag"] for p in node["participants"]]} for node in entrants]
    return None

def get_gamer_tags(event_id, page=1, per_page=20):
    entrants = get_event_entrants(event_id, page, per_page)
    if entrants:
        gamer_tags = [gamer_tag for entrant in entrants for gamer_tag in entrant["gamerTags"]]
        return sorted(gamer_tags)
    return []

def get_event_id(Slug):
    Slug_Formatted = extract_path_from_url(Slug)
    query = """
    query getEventId($slug: String) {
        event(slug: $slug) {
            id
            name
        }
    }
    """
    variables = {
        "slug": Slug_Formatted
    }

    data = fetch_startgg_data(query, variables)
    print(Slug_Formatted)
    if data:
        eventId = data["data"]["event"]["id"]
        return eventId
    return None
    

def extract_path_from_url(url):
    parsed_url = urlparse(url) 
    full_path = parsed_url.path
    relevant_path = "/".join(full_path.split("/")[:5])
    return relevant_path[1:]

def get_startgg_api_key():
    config = read_config()
    return get_or_prompt_config_value(config, "STARTGG_API_KEY", "Enter your Start.gg API Key:")

def save_startgg_api_key(api_key):
    try:
        config_content = []
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "r") as f:
                config_content = f.readlines()
        with open(CONFIG_FILE_PATH, "w") as f:
            key_found = False
            for line in config_content:
                if line.startswith("STARTGG_API_KEY="):
                    f.write(f"STARTGG_API_KEY={api_key}\n")
                    key_found = True
                else:
                    f.write(line)
            if not key_found:
                f.write(f"STARTGG_API_KEY={api_key}\n")
        print("Start.gg API key saved to config.txt.")
    except Exception as e:
        print(f"Failed to save Start.gg API key: {e}")
        messagebox.showerror("Error", "Failed to save Start.gg API key.")

def prompt_for_startgg_api_key():
    root = ctk.CTk()
    root.withdraw()
    api_key = simpledialog.askstring("Start.gg API Key", "Enter your Start.gg API Key:")
    if api_key:
        save_startgg_api_key(api_key)
    return api_key or ""

STARTGG_API_KEY = get_startgg_api_key()

def get_obs_password():
    config = read_config()
    return get_or_prompt_config_value(config, "OBS_PASSWORD", "Enter your OBS WebSocket password:")

OBS_PASSWORD = get_obs_password()

def save_obs_password(password):
    try:
        with open(CONFIG_FILE_PATH, "w") as f:
            f.write(f"OBS_PASSWORD={password}\n")
        print("OBS password saved to config.txt.")
    except Exception as e:
        print(f"Failed to save OBS password: {e}")
        messagebox.showerror("Error", "Failed to save OBS password.")

def prompt_for_password():
    root = ctk.CTk()
    root.withdraw()
    password = simpledialog.askstring("OBS Password", "Enter your OBS WebSocket password:", show='*')
    if password:
        save_obs_password(password)
    return password or ""

def connect_to_obs(password):
    try:
        client = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=password)
        print("Connected to OBS.")
        return client
    except Exception as e:
        print(f"Failed to connect to OBS: {e}")
        messagebox.showerror("Error", "Failed to connect to OBS. Check your settings.")
        return None

def update_obs_text(client, source, text):
    try:
        print(f"Updating text source '{source}' with text: '{text}'")
        client.set_input_settings(source, {"text": text}, overlay=True)
        print(f"Successfully updated text source: {source}")
    except Exception as e:
        print(f"Failed to update OBS text source '{source}': {e}")
        messagebox.showerror("Error", f"Failed to update OBS text source '{source}': {e}")


def update_obs_image(client, source, image_name):
    try:
        if switch_var.get() == "Stock Icons":
            image_path = os.path.join(STOCK_IMAGE_DIRECTORY, f"{image_name}.png")
        elif switch_var.get() == "Character Frames":
            image_path = os.path.join(FRAME_IMAGE_DIRECTORY, f"{image_name}.png")
        if os.path.exists(image_path):
            print(f"Updating image source '{source}' with image: '{image_path}'")
            client.set_input_settings(source, {"file": image_path}, overlay=True)
            print(f"Successfully updated image source: {source}")
        else:
            print(f"Image not found for source '{source}': {image_path}")
            messagebox.showerror("Error", f"Image not found: {image_path}")
    except Exception as e:
        print(f"Failed to update OBS image source '{source}': {e}")
        messagebox.showerror("Error", f"Failed to update OBS image source '{source}': {e}")

def on_update():
    password = get_obs_password()
    client = connect_to_obs(password)
    if not client:
        return

    player1_name = player1_name_var.get()
    player1_char = player1_char_var.get()
    update_obs_text(client, "Player1Name", player1_name)
    update_obs_image(client, "Player1Image", player1_char)

    player2_name = player2_name_var.get()
    player2_char = player2_char_var.get()
    update_obs_text(client, "Player2Name", player2_name)
    update_obs_image(client, "Player2Image", player2_char)

    set_count = f"{set_count_1_var.get()} - {set_count_2_var.get()}"
    update_obs_text(client, "SetCount", set_count)

character_options = [os.path.splitext(f)[0] for f in os.listdir(STOCK_IMAGE_DIRECTORY) if f.endswith(".png")]
name_options = []

def update_url_and_names():
    """Fetch gamer tags based on the event URL and update dropdowns."""
    event_url = event_url_var.get()
    if not event_url:
        messagebox.showerror("Error", "Event URL is empty. Please provide a valid URL.")
        return

    event_id = get_event_id(event_url)
    if not event_id:
        messagebox.showerror("Error", "Failed to fetch event ID. Check the URL and try again.")
        return

    gamer_tags = get_gamer_tags(event_id)
    if not gamer_tags:
        messagebox.showerror("Error", "Failed to fetch gamer tags. Try again later.")
        return

    player1_name_dropdown.configure(values=gamer_tags)
    player2_name_dropdown.configure(values=gamer_tags)
    messagebox.showinfo("Success", "Gamer tags updated successfully!")

def switch_event():
    print("switch toggled, current value:", switch_var.get())
    switch.configure(text=switch_var.get())

root = ctk.CTk()
root.title("OBS Set Manager")
root.geometry("650x300")
root.resizable(False, False)

root.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")
root.grid_rowconfigure(1, weight=1) 

title_label = ctk.CTkLabel(root, text="Current Stream Set", font=("Arial", 18, "bold"))
title_label.grid(row=0, column=0, columnspan=3, pady=10)

frame_width = 180
frame_height = 130

player1_frame = ctk.CTkFrame(root, width=frame_width, height=frame_height)
player1_frame.grid(row=1, column=0, padx=25, pady=10, sticky="nsew")
player1_frame.grid_propagate(False)

player1_label = ctk.CTkLabel(player1_frame, text="Player 1")
player1_label.grid(row=0, column=0, pady=5, sticky="ew")

player1_name_var = ctk.StringVar()
player1_name_dropdown = ctk.CTkComboBox(player1_frame, variable=player1_name_var, values=name_options)
player1_name_dropdown.grid(row=1, column=0, pady=5, padx=10, sticky="ew")

player1_char_label = ctk.CTkLabel(player1_frame, text="Char:")
player1_char_label.grid(row=2, column=0, pady=5, sticky="ew")

player1_char_var = ctk.StringVar()
player1_char_dropdown = ctk.CTkComboBox(player1_frame, variable=player1_char_var, values=character_options)
player1_char_dropdown.grid(row=3, column=0, pady=5, padx=10, sticky="ew")

set_count_frame = ctk.CTkFrame(root, width=frame_width, height=frame_height)
set_count_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
set_count_frame.grid_propagate(False)
set_count_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="count")

set_count_label = ctk.CTkLabel(set_count_frame, text="Set Count", font=("Arial", 14, "bold"))
set_count_label.grid(row=0, column=0, columnspan=3, pady=5)

set_count_1_var = ctk.StringVar(value="0")
set_count_1_entry = ctk.CTkEntry(set_count_frame, textvariable=set_count_1_var, width=40, justify="center")
set_count_1_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

set_count_dash = ctk.CTkLabel(set_count_frame, text="-")
set_count_dash.grid(row=1, column=1, pady=5)

set_count_2_var = ctk.StringVar(value="0")
set_count_2_entry = ctk.CTkEntry(set_count_frame, textvariable=set_count_2_var, width=40, justify="center")
set_count_2_entry.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

update_button = ctk.CTkButton(set_count_frame, text="Update OBS", command=on_update)
update_button.grid(row=2, column=0, columnspan=3, pady=10)

switch_var = ctk.StringVar(value="Character Frames")
switch = ctk.CTkSwitch(set_count_frame, text=switch_var.get(), command=switch_event, variable=switch_var, onvalue="Character Frames", offvalue="Stock Icons")
switch.grid(row=3, column=0, columnspan=3, pady=10)

player2_frame = ctk.CTkFrame(root, width=frame_width, height=frame_height)
player2_frame.grid(row=1, column=2, padx=30, pady=10, sticky="nsew")
player2_frame.grid_propagate(False)

player2_label = ctk.CTkLabel(player2_frame, text="Player 2")
player2_label.grid(row=0, column=0, pady=5, sticky="ew")

player2_name_var = ctk.StringVar()
player2_name_dropdown = ctk.CTkComboBox(player2_frame, variable=player2_name_var, values=name_options)
player2_name_dropdown.grid(row=1, column=0, pady=5, padx=10, sticky="ew")

player2_char_label = ctk.CTkLabel(player2_frame, text="Char:")
player2_char_label.grid(row=2, column=0, pady=5, sticky="ew")

player2_char_var = ctk.StringVar()
player2_char_dropdown = ctk.CTkComboBox(player2_frame, variable=player2_char_var, values=character_options)
player2_char_dropdown.grid(row=3, column=0, pady=5, padx=10, sticky="ew")

event_url_label = ctk.CTkLabel(root, text="Event URL:", font=("Arial", 12), anchor="e")
event_url_label.grid(row=2, column=0, columnspan=1, pady=10, sticky="w", padx=10)

event_url_var = ctk.StringVar()
event_url_entry = ctk.CTkEntry(root, textvariable=event_url_var, width=500)
event_url_entry.grid(row=2, column=1, columnspan=1, pady=10, sticky="ew")

url_button = ctk.CTkButton(root, text="Update URL", command=update_url_and_names)
url_button.grid(row=2, column=2, columnspan=1, pady=10, padx=10, sticky="ew")

root.mainloop()
