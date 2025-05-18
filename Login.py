import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sys
import os

# Terran color palette
TERRAN_BG = "#1b263b"
TERRAN_ACCENT = "#415a77"
TERRAN_HIGHLIGHT = "#00b4d8"
TERRAN_TEXT = "#e0e1dd"

class LoginWindow:
    TITLEBAR_MARGIN = 24  # Adjust this for more/less space below the title bar

    def __init__(self, master, on_login=None, terran_style=True):
        self.master = master
        self.on_login = on_login
        self.terran_style = terran_style
        self.master.geometry("620x520")
        self.style = ttk.Style(theme='cyborg')
        if terran_style:
            self.master.configure(bg=TERRAN_BG)
        self._add_custom_titlebar("Garage Login")
        self._create_widgets()

    def _add_custom_titlebar(self, title="Garage Login"):
        self.master.overrideredirect(True)
        titlebar = tk.Frame(self.master, bg=TERRAN_ACCENT, relief="raised", bd=0, highlightthickness=0)
        titlebar.pack(fill=tk.X, side=tk.TOP)
        title_label = tk.Label(titlebar, text=title, bg=TERRAN_ACCENT, fg=TERRAN_TEXT, font=("Orbitron", 14, "bold"))
        title_label.pack(side=tk.LEFT, padx=10, pady=2)
        exit_btn = tk.Button(
            titlebar, text="✕", bg=TERRAN_ACCENT, fg=TERRAN_TEXT, borderwidth=0, font=("Arial", 14, "bold"),
            activebackground="#b22222", activeforeground="#fff",
            command=self._full_exit
        )
        exit_btn.pack(side=tk.RIGHT, padx=(0, 2), pady=2)
        min_btn = tk.Button(
            titlebar, text="—", bg=TERRAN_ACCENT, fg=TERRAN_TEXT, borderwidth=0, font=("Arial", 14, "bold"),
            activebackground=TERRAN_BG, activeforeground=TERRAN_HIGHLIGHT,
            command=lambda: self.master.iconify()
        )
        min_btn.pack(side=tk.RIGHT, padx=(0, 2), pady=2)
        def start_move(event):
            self.master._drag_start_x = event.x_root
            self.master._drag_start_y = event.y_root
            self.master._win_x = self.master.winfo_x()
            self.master._win_y = self.master.winfo_y()
        def do_move(event):
            if hasattr(self.master, '_drag_start_x'):
                dx = event.x_root - self.master._drag_start_x
                dy = event.y_root - self.master._drag_start_y
                new_x = self.master._win_x + dx
                new_y = self.master._win_y + dy
                self.master.geometry(f"+{new_x}+{new_y}")
        titlebar.bind("<ButtonPress-1>", start_move)
        titlebar.bind("<B1-Motion>", do_move)
        # Margin below the title bar
        if self.TITLEBAR_MARGIN > 0:
            spacer = tk.Frame(self.master, height=self.TITLEBAR_MARGIN, bg=TERRAN_BG)
            spacer.pack(fill=tk.X)

    def _full_exit(self):
        try:
            self.master.destroy()
        except Exception:
            pass
        try:
            self.master.quit()
        except Exception:
            pass
        os._exit(0)  # Guaranteed exit

    def _create_widgets(self):
        # Spacer between titlebar and login frame
        spacer = tk.Frame(self.master, height=36, bg=TERRAN_BG)  # Match background
        spacer.pack(fill=tk.X)

        login_frame = ttk.LabelFrame(
            self.master,
            padding=12,  # Increased padding for larger appearance
            borderwidth=3,
            relief="groove"
        )
        login_frame.pack(pady=(0, 10), padx=10)  # More vertical space and horizontal margin

        self.style.configure("TLabelframe", background=TERRAN_ACCENT, foreground=TERRAN_TEXT,
                             bordercolor=TERRAN_HIGHLIGHT)
        self.style.configure("TLabelframe.Label", font=('Orbitron', 18, 'bold'), background=TERRAN_ACCENT,
                             foreground=TERRAN_TEXT)

        self.user_type = ttk.Combobox(
            login_frame, values=['Admin', 'Mechanic'], state='readonly', font=('Orbitron', 12)
        )
        self.user_type.grid(row=0, column=0, columnspan=2, pady=6, padx=10, sticky='ew')
        self.user_type.set('Admin')

        ttk.Label(login_frame, text="Username:", font=('Orbitron', 12), background=TERRAN_ACCENT,
                  foreground=TERRAN_TEXT).grid(row=1, column=0, padx=5, pady=6, sticky='e')
        self.username = ttk.Entry(login_frame, font=('Orbitron', 12), width=22)
        self.username.grid(row=1, column=1, padx=5, pady=6, sticky='w')

        ttk.Label(login_frame, text="Password:", font=('Orbitron', 12), background=TERRAN_ACCENT,
                  foreground=TERRAN_TEXT).grid(row=2, column=0, padx=5, pady=6, sticky='e')
        self.password = ttk.Entry(login_frame, show="*", font=('Orbitron', 12), width=22)
        self.password.grid(row=2, column=1, padx=5, pady=6, sticky='w')

        login_btn = ttk.Button(
            login_frame, text="Login", command=self.authenticate,
            width=20
        )
        login_btn.grid(row=3, column=0, columnspan=2, pady=14, sticky='ew')

        register_btn = ttk.Button(
            login_frame, text="Register New Mechanic", command=self.open_register,
            width=20
        )
        register_btn.grid(row=4, column=0, columnspan=2, pady=6)

    def authenticate(self):
        user_type = self.user_type.get()
        username = self.username.get()
        password = self.password.get()

        if not username or not password:
            messagebox.showerror("Login Failed", "Please enter username and password")
            return

        try:
            with sqlite3.connect('cosmic_garage.db') as conn:
                cursor = conn.cursor()
                if user_type == 'Admin':
                    cursor.execute('SELECT * FROM users WHERE username=? AND password=? AND role="admin"', (username, password))
                    user = cursor.fetchone()
                    if user:
                        self.master.destroy()
                        if self.on_login:
                            self.on_login(user_role='admin')
                    else:
                        messagebox.showerror("Login Failed", "Invalid admin credentials")
                elif user_type == 'Mechanic':
                    cursor.execute('SELECT * FROM users WHERE username=? AND password=? AND role="mechanic"', (username, password))
                    user = cursor.fetchone()
                    if user:
                        self.master.destroy()
                        if self.on_login:
                            self.on_login(user_role='mechanic', mechanic_name=user[4])
                    else:
                        messagebox.showerror("Login Failed", "Invalid mechanic credentials")
                else:
                    messagebox.showerror("Login Failed", "Please select a user type")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred with the database: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def open_register(self):
        register_win = tk.Toplevel(self.master)
        register_win.title("Mechanic Registration")
        register_win.geometry("340x260")
        register_win.transient(self.master)
        register_win.grab_set()
        register_win.focus_set()
        if self.terran_style:
            register_win.configure(bg=TERRAN_BG)

        reg_frame = ttk.LabelFrame(
            register_win,
            text="Mechanic Registration",
            padding=10,
            borderwidth=3,
            relief="groove"
        )
        reg_frame.pack(pady=10, padx=20, fill='x')

        self.style.configure("TLabelframe", background=TERRAN_ACCENT, foreground=TERRAN_TEXT, bordercolor=TERRAN_HIGHLIGHT)
        self.style.configure("TLabelframe.Label", font=('Orbitron', 14, 'bold'), background=TERRAN_ACCENT, foreground=TERRAN_TEXT)

        entries = [
            ('Full Name:', 'full_name'),
            ('Username:', 'username'),
            ('Password:', 'password'),
            ('Confirm Password:', 'confirm_password')
        ]

        self.register_entries = {}
        for i, (label, key) in enumerate(entries):
            ttk.Label(reg_frame, text=label, width=15, background=TERRAN_ACCENT, foreground=TERRAN_TEXT).grid(row=i, column=0, sticky='e', padx=5, pady=5)
            entry = ttk.Entry(reg_frame, show="*" if "password" in key else "")
            entry.grid(row=i, column=1, sticky='w', padx=5, pady=5)
            self.register_entries[key] = entry

        ttk.Button(register_win, text="Submit Registration", command=lambda: self.submit_registration(register_win)).pack(pady=10)

    def submit_registration(self, register_win):
        data = {
            'full_name': self.register_entries['full_name'].get().strip(),
            'username': self.register_entries['username'].get().strip(),
            'password': self.register_entries['password'].get(),
            'confirm_password': self.register_entries['confirm_password'].get()
        }

        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required")
            return

        if data['password'] != data['confirm_password']:
            messagebox.showerror("Error", "Passwords do not match")
            return

        try:
            with sqlite3.connect('cosmic_garage.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    username TEXT UNIQUE NOT NULL,
                                    password TEXT NOT NULL,
                                    role TEXT NOT NULL,
                                    full_name TEXT
                                )''')
                conn.commit()
                cursor.execute('''INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)''',
                               (data['username'], data['password'], 'mechanic', data['full_name']))
                conn.commit()
                messagebox.showinfo("Success", "Registration successful!\nYou can now login as a mechanic")
                register_win.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred with the database: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
