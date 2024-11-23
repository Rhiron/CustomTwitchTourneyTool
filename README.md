OBS Tourney Stream Helper
==========================

This tool allows you to manage player names, character images, and set counts for your tournaments with OBS. The tool connects to OBS via WebSocket and dynamically updates your scene.

Requirements:
-------------
1. OBS Studio with the OBS WebSocket plugin installed.
2. OBS WebSocket plugin enabled and configured (default port: 4455).
3. Character images stored in the `StockIcons` folder.

Setup Instructions:
-------------------
1. Run `main.exe`.
2. If prompted, enter your OBS WebSocket password. The password is saved securely in a `config.txt` file for future use.
    2.1. You can find the password in OBS Studio Tools > WebSocket Server Setting > Show Connect Info > Server Password (Copy this value)
3. Use the GUI to:
   - Enter player names.
   - Select character images from the dropdown (images must be in the `StockIcons` folder).
   - Update the set count.
4. Click "Update OBS" to apply changes to your OBS scene.

Notes:
------
- Images must be `.png` files and placed in the `StockIcons` folder.
- The `config.txt` file is created in the same directory as `main.exe` to store your OBS WebSocket password securely.
- If you encounter issues connecting to OBS, ensure the OBS WebSocket plugin is installed and the password is correct.

Support:
--------
For questions or feedback, please contact [rileyhiron@gmail.com].

