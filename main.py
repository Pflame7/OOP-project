import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pyglet

pyglet.font.add_file('Orbitron-Medium.ttf')

from Database import create_database
from Login import LoginWindow
from CosmicApp import CosmicApp

def launch_main_app(root, user_role, mechanic_name=None):
    root.deiconify()
    CosmicApp(root, user_role=user_role, mechanic_name=mechanic_name)

def main():
    create_database()
    root = ttk.Window(themename="cyborg")
    root.withdraw()

    # Show login as a Toplevel
    login_win = tk.Toplevel(root)
    LoginWindow(
        login_win,
        on_login=lambda user_role, mechanic_name=None: (
            login_win.destroy(),
            launch_main_app(root, user_role, mechanic_name)
        )
    )

    root.mainloop()

if __name__ == "__main__":
    main()