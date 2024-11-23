import time
import obsws_python as obs
import os

# OBS WebSocket connection details
OBS_HOST = "localhost"  # Default localhost
OBS_PORT = 4455         # Default WebSocket port

# Text source names in OBS
PLAYER_1_SOURCE = "Player1Name"
PLAYER_2_SOURCE = "Player2Name"
PLAYER_1_IMAGE_SOURCE = "Player1Image"
PLAYER_2_IMAGE_SOURCE = "Player2Image"

# Path to the TXT file that commentators will edit
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_FILE_PATH = os.path.join(BASE_DIR, "player_names.txt")
IMAGE_DIRECTORY = os.path.join(BASE_DIR, "StockIcons")
CONFIG_FILE_PATH = os.path.join(BASE_DIR, "config.txt")

def connect_to_obs():
    """Connect to OBS WebSocket."""
    try:
        client = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD)
        print("Connected to OBS.")
        return client
    except Exception as e:
        print(f"Failed to connect to OBS: {e}")
        return None
    
def get_obs_password():
    """Read the OBS password from the config file."""
    try:
        with open(CONFIG_FILE_PATH, "r") as f:
            for line in f:
                if line.startswith("OBS_PASSWORD="):
                    return line.strip().split("=", 1)[1]
        print("OBS_PASSWORD not found in config.txt.")
    except FileNotFoundError:
        print("config.txt not found. Please create it.")
    return ""
OBS_PASSWORD = get_obs_password()
def update_text_sources(client, player1, player2):
    """Update OBS text sources with player names."""
    try:
        client.set_input_settings(PLAYER_1_SOURCE, {"text": player1}, overlay=True)
        client.set_input_settings(PLAYER_2_SOURCE, {"text": player2}, overlay=True)
        print(f"Updated names: Player 1 = {player1}, Player 2 = {player2}")
    except Exception as e:
        print(f"Failed to update text sources: {e}")

def update_image_sources(client, player1_image, player2_image):
    """Update OBS image sources with player images."""
    try:
        player1_path = os.path.join(IMAGE_DIRECTORY, f"{player1_image}.png")
        player2_path = os.path.join(IMAGE_DIRECTORY, f"{player2_image}.png")

        if os.path.exists(player1_path):
            client.set_input_settings(PLAYER_1_IMAGE_SOURCE, {"file": player1_path}, overlay=True)
        else:
            print(f"Image not found for Player 1: {player1_path}")

        if os.path.exists(player2_path):
            client.set_input_settings(PLAYER_2_IMAGE_SOURCE, {"file": player2_path}, overlay=True)
        else:
            print(f"Image not found for Player 2: {player2_path}")

        print(f"Updated images: Player 1 = {player1_image}, Player 2 = {player2_image}")
    except Exception as e:
        print(f"Failed to update image sources: {e}")


def main():
    client = connect_to_obs()
    if not client:
        return

    last_names = ("", "")
    last_images = ("", "")

    try:
        while True:
            try:
                with open(TXT_FILE_PATH, "r") as f:
                    lines = f.read().strip().split("\n")
                    if len(lines) >= 6:
                        player1, player2 = lines[1], lines[4]
                        player1_image, player2_image = lines[2], lines[5]
                        if (player1, player2) != last_names:
                            update_text_sources(client, player1, player2)
                            last_names = (player1, player2)

                        if (player1_image, player2_image) != last_images:
                            update_image_sources(client, player1_image, player2_image)
                            last_images = (player1_image, player2_image)
            except FileNotFoundError:
                print(f"File not found: {TXT_FILE_PATH}. Please create it.")

            time.sleep(1)  # Check for updates every second
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
