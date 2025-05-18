import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pyglet
import datetime

# Load custom font
pyglet.font.add_file('Orbitron-Medium.ttf')


# ================== DATABASE SETUP ==================
def create_database():
    conn = sqlite3.connect('cosmic_garage.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT,
                        full_name TEXT)''')

    # Customers table
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        car_model TEXT,
                        vin TEXT UNIQUE,
                        issue TEXT,
                        date_added TEXT)''')

    # Repairs table
    cursor.execute('''CREATE TABLE IF NOT EXISTS repairs (
                        id INTEGER PRIMARY KEY,
                        vehicle TEXT,
                        customer_name TEXT,
                        car_model TEXT,
                        vin TEXT UNIQUE,
                        issue TEXT,
                        status TEXT,
                        assigned_mechanic TEXT,
                        priority TEXT DEFAULT 'Medium',
                        estimated_hours REAL,
                        cost REAL,
                        start_date TEXT,
                        end_date TEXT,
                        notes TEXT)''')

    # Inventory table
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY,
                        part_name TEXT UNIQUE,
                        quantity INTEGER,
                        last_ordered TEXT)''')

    # Schedules table
    cursor.execute('''CREATE TABLE IF NOT EXISTS schedules (
                        id INTEGER PRIMARY KEY,
                        mechanic TEXT,
                        start_time TEXT,
                        end_time TEXT,
                        task TEXT,
                        repair_id INTEGER,
                        FOREIGN KEY(repair_id) REFERENCES repairs(id))''')

    # Create default admin if not exists
    cursor.execute('SELECT * FROM users WHERE username="admin"')
    if not cursor.fetchone():
        cursor.execute('''INSERT INTO users (username, password, role, full_name)
                          VALUES (?, ?, ?, ?)''',
                       ('admin', 'admin123', 'admin', 'Administrator'))

    # Create initial inventory if empty
    cursor.execute('SELECT COUNT(*) FROM inventory')
    if cursor.fetchone()[0] == 0:
        initial = [('Spark Plugs', 15), ('Brake Pads', 10),
                   ('Oil Filter', 20), ('Timing Belt', 8)]
        cursor.executemany('INSERT INTO inventory (part_name, quantity) VALUES (?,?)', initial)

    conn.commit()
    conn.close()


create_database()


# ================== LOGIN WINDOW ==================
class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Stellar Garage Login")
        self.master.geometry("400x300")
        self.style = ttk.Style(theme='darkly')

        self._create_widgets()

    def _create_widgets(self):
        self.bg_image = ImageTk.PhotoImage(Image.open('space_bg.jpg').resize((400, 300)))
        bg_label = ttk.Label(self.master, image=self.bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        login_frame = ttk.Frame(self.master)
        login_frame.place(relx=0.5, rely=0.5, anchor='center')

        ttk.Label(login_frame, text="Stellar Garage Login", font=('Orbitron', 16)).grid(row=0, column=0, columnspan=2,
                                                                                        pady=10)

        self.user_type = ttk.Combobox(login_frame, values=['Admin', 'Mechanic'], state='readonly')
        self.user_type.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky='ew')
        self.user_type.set('Admin')

        ttk.Label(login_frame, text="Username:").grid(row=2, column=0, padx=5, pady=5)
        self.username = ttk.Entry(login_frame)
        self.username.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(login_frame, text="Password:").grid(row=3, column=0, padx=5, pady=5)
        self.password = ttk.Entry(login_frame, show="*")
        self.password.grid(row=3, column=1, padx=5, pady=5)

        self.mechanic_selector = ttk.Combobox(login_frame, state='disabled')
        self.mechanic_selector.grid(row=4, column=0, columnspan=2, pady=5, padx=10, sticky='ew')

        login_btn = ttk.Button(login_frame, text="Login", command=self.authenticate)
        login_btn.grid(row=5, column=0, columnspan=2, pady=10, sticky='ew')

        # Add Register button
        register_btn = ttk.Button(login_frame, text="Register New Mechanic",
                                  command=self.open_register, width=20)
        register_btn.grid(row=6, column=0, columnspan=2, pady=10)

        self.user_type.bind('<<ComboboxSelected>>', self.update_login_fields)

    def update_login_fields(self, event):
        if self.user_type.get() == 'Mechanic':
            conn = sqlite3.connect('cosmic_garage.db')
            cursor = conn.cursor()
            cursor.execute('SELECT full_name FROM users WHERE role="mechanic"')
            mechanics = [row[0] for row in cursor.fetchall()]
            self.mechanic_selector['values'] = mechanics
            self.mechanic_selector['state'] = 'readonly'
            self.username['state'] = 'disabled'
            self.password['state'] = 'disabled'
            conn.close()
        else:
            self.mechanic_selector['state'] = 'disabled'
            self.username['state'] = 'normal'
            self.password['state'] = 'normal'

    def authenticate(self):
        user_type = self.user_type.get()
        username = self.username.get()
        password = self.password.get()
        mechanic = self.mechanic_selector.get()

        conn = sqlite3.connect('cosmic_garage.db')
        cursor = conn.cursor()

        try:
            if user_type == 'Admin':
                cursor.execute('SELECT * FROM users WHERE username=? AND password=? AND role="admin"',
                               (username, password))
                user = cursor.fetchone()
                if user:
                    self.master.destroy()
                    root = ttk.Window()
                    CosmicApp(root, user_role='admin')
                    root.mainloop()
                else:
                    messagebox.showerror("Login Failed", "Invalid admin credentials")
            elif user_type == 'Mechanic' and mechanic:
                cursor.execute('SELECT * FROM users WHERE full_name=? AND role="mechanic"', (mechanic,))
                user = cursor.fetchone()
                if user:
                    self.master.destroy()
                    root = ttk.Window()
                    CosmicApp(root, user_role='mechanic', mechanic_name=mechanic)
                    root.mainloop()
                else:
                    messagebox.showerror("Login Failed", "Mechanic not found")
            else:
                messagebox.showerror("Login Failed", "Please fill all fields")
        finally:
            conn.close()

    def open_register(self):
        register_win = tk.Toplevel(self.master)
        register_win.title("Mechanic Registration")
        register_win.geometry("300x250")

        ttk.Label(register_win, text="Mechanic Registration", font=('Orbitron', 12)).pack(pady=10)

        form_frame = ttk.Frame(register_win)
        form_frame.pack(pady=10, padx=20)

        entries = [
            ('Full Name:', 'full_name'),
            ('Username:', 'username'),
            ('Password:', 'password'),
            ('Confirm Password:', 'confirm_password')
        ]

        self.register_entries = {}
        for label, key in entries:
            frame = ttk.Frame(form_frame)
            frame.pack(pady=5, fill=tk.X)
            ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT)
            entry = ttk.Entry(frame, show="*" if "password" in key else "")
            entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
            self.register_entries[key] = entry

        ttk.Button(register_win, text="Submit Registration",
                   command=self.submit_registration).pack(pady=10)

    def submit_registration(self):
        data = {
            'full_name': self.register_entries['full_name'].get(),
            'username': self.register_entries['username'].get(),
            'password': self.register_entries['password'].get(),
            'confirm_password': self.register_entries['confirm_password'].get()
        }

        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required")
            return

        if data['password'] != data['confirm_password']:
            messagebox.showerror("Error", "Passwords do not match")
            return

        conn = sqlite3.connect('cosmic_garage.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''INSERT INTO users 
                            (username, password, role, full_name)
                            VALUES (?, ?, ?, ?)''',
                           (data['username'], data['password'],
                            'mechanic', data['full_name']))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful!\nYou can now login as a mechanic")

            # Refresh mechanics list
            if self.user_type.get() == 'Mechanic':
                self.update_login_fields(None)

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        finally:
            conn.close()


# ================== MAIN APPLICATION ==================
class CosmicApp:
    def __init__(self, root, user_role, mechanic_name=None):
        self.root = root
        self.user_role = user_role
        self.mechanic_name = mechanic_name
        self.root.title("Stellar Garage Manager")
        self.root.state('zoomed')
        self.style = ttk.Style(theme='darkly')
        self.conn = sqlite3.connect('cosmic_garage.db')

        self._configure_styles()
        self.cal_year = datetime.datetime.now().year
        self.cal_month = datetime.datetime.now().month
        self.create_widgets()
        self.animate_header()

    def _configure_styles(self):
        self.style.configure('.', font=('Orbitron', 14))
        self.style.configure('Header.TLabel', font=('Orbitron', 28, 'bold'))
        self.style.configure('TButton', font=('Orbitron', 14))
        self.style.configure('Treeview.Heading', font=('Orbitron', 16, 'bold'))
        self.style.configure('Treeview', font=('Orbitron', 14), rowheight=35)
        self.style.configure('TEntry', font=('Orbitron', 14))

    def create_widgets(self):
        self.bg_image = ImageTk.PhotoImage(Image.open('space_bg.jpg').resize(
            (self.root.winfo_screenwidth(), self.root.winfo_screenheight())))
        bg_label = ttk.Label(self.root, image=self.bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.header = ttk.Label(self.root, text="🚀 COSMIC VEHICLE WORKSHOP 🪐", style='Header.TLabel')
        self.header.pack(pady=(30, 20))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self._create_customer_tab()
        self._create_repairs_tab()
        self._create_inventory_tab()

        if self.user_role == 'admin':
            self._create_mechanics_tab()
            self._create_schedule_tab()
        elif self.user_role == 'mechanic':
            self._create_my_schedule_tab()

    # ================== CUSTOMER TAB ==================
    def _create_customer_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Customers")

        form_frame = ttk.Frame(tab)
        form_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)

        entries = [
            ('Name:', 'customer_name'),
            ('Car Model:', 'car_model'),
            ('VIN:', 'vin'),
            ('Issue:', 'issue')
        ]

        self.customer_entries = {}
        for label, key in entries:
            frame = ttk.Frame(form_frame)
            frame.pack(pady=10, fill=tk.X)
            ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT, padx=10)
            entry = ttk.Entry(frame, width=30)
            entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=10)
            self.customer_entries[key] = entry

        ttk.Button(form_frame, text="Add Customer", command=self.add_customer).pack(pady=20)

    # ================== REPAIRS TAB ==================
    def _create_repairs_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Repairs")

        self.repairs_tree = ttk.Treeview(tab, columns=(
            'Status', 'Start Date', 'Issue', 'Mechanic', 'Priority', 'Hours'
        ), show='headings')

        columns = [
            ('#0', 'Vehicle', 300),
            ('Status', 'Status', 120),
            ('Start Date', 'Start Date', 150),
            ('Issue', 'Issue', 400),
            ('Mechanic', 'Mechanic', 150),
            ('Priority', 'Priority', 100),
            ('Hours', 'Est. Hours', 100)
        ]

        for col_id, heading, width in columns:
            self.repairs_tree.heading(col_id, text=heading, anchor=tk.W)
            self.repairs_tree.column(col_id, width=width, minwidth=width - 50)

        self.repairs_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.repairs_tree.bind('<<TreeviewSelect>>', self.show_repair_details)

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)

        controls = [
            ('Mark Repaired', self.mark_repaired),
            ('Mark Pending', self.mark_pending),
            ('Edit Repair', self.edit_repair),
            ('Add Notes', self.add_repair_notes)
        ]

        for text, cmd in controls:
            ttk.Button(btn_frame, text=text, command=cmd).pack(side=tk.LEFT, padx=5)

        self.update_repairs_display()

    # ================== SCHEDULE MANAGEMENT ==================
    def _create_schedule_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Schedules")

        # Mechanic selector for admin
        self.selected_mechanic = tk.StringVar()
        cursor = self.conn.cursor()
        cursor.execute('SELECT full_name FROM users WHERE role="mechanic"')
        mechanics = [row[0] for row in cursor.fetchall()]
        self.selected_mechanic.set(mechanics[0] if mechanics else "")
        sel_frame = ttk.Frame(tab)
        sel_frame.pack(anchor='w', padx=20, pady=(10,0))
        ttk.Label(sel_frame, text="Mechanic:").pack(side=tk.LEFT)
        self.mechanic_combo = ttk.Combobox(sel_frame, values=mechanics, textvariable=self.selected_mechanic, state='readonly', width=25)
        self.mechanic_combo.pack(side=tk.LEFT, padx=10)
        self.mechanic_combo.bind('<<ComboboxSelected>>', lambda e: self.update_monthly_calendar_display())

        # Month/year navigation
        nav_frame = ttk.Frame(tab)
        nav_frame.pack(anchor='center', pady=(0,5))
        ttk.Button(nav_frame, text="<<", command=lambda: self.change_month(-1)).pack(side=tk.LEFT, padx=5)
        self.month_label = ttk.Label(nav_frame, text="")
        self.month_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text=">>", command=lambda: self.change_month(1)).pack(side=tk.LEFT, padx=5)

        # Calendar frame
        self.calendar_frame = ttk.Frame(tab)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        self.update_monthly_calendar_display()

        # Add schedule button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        # Pass selected mechanic to add_schedule
        ttk.Button(btn_frame, text="Add Schedule", command=self.open_add_schedule_dialog).pack(side=tk.LEFT, padx=5)

    def open_add_schedule_dialog(self):
        # Open add schedule dialog with selected mechanic
        self.add_schedule(mechanic=self.selected_mechanic.get())

    def _create_my_schedule_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="My Schedule")

        # Month/year navigation
        self.cal_year = datetime.datetime.now().year
        self.cal_month = datetime.datetime.now().month
        nav_frame = ttk.Frame(tab)
        nav_frame.pack(anchor='center', pady=(10,5))
        ttk.Button(nav_frame, text="<<", command=lambda: self.change_month(-1, tab)).pack(side=tk.LEFT, padx=5)
        self.my_month_label = ttk.Label(nav_frame, text="")
        self.my_month_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text=">>", command=lambda: self.change_month(1, tab)).pack(side=tk.LEFT, padx=5)

        # Calendar frame
        self.my_calendar_frame = ttk.Frame(tab)
        self.my_calendar_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        self.update_monthly_calendar_display(tab=tab)

        # Add schedule button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Schedule", command=lambda: self.add_schedule(mechanic=self.mechanic_name, tab=tab)).pack(side=tk.LEFT, padx=5)

    def change_month(self, delta, tab=None):
        if tab and hasattr(self, 'my_month_label'):
            # Mechanic view
            self.cal_month += delta
            if self.cal_month < 1:
                self.cal_month = 12
                self.cal_year -= 1
            elif self.cal_month > 12:
                self.cal_month = 1
                self.cal_year += 1
            self.update_monthly_calendar_display(tab=tab)
        else:
            # Admin view
            self.cal_month += delta
            if self.cal_month < 1:
                self.cal_month = 12
                self.cal_year -= 1
            elif self.cal_month > 12:
                self.cal_month = 1
                self.cal_year += 1
            self.update_monthly_calendar_display()

    def update_monthly_calendar_display(self, tab=None):
        import calendar
        year, month = self.cal_year, self.cal_month
        month_days = calendar.monthcalendar(year, month)
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        if tab and hasattr(self, 'my_calendar_frame'):
            cal_frame = self.my_calendar_frame
            for widget in cal_frame.winfo_children():
                widget.destroy()
            self.my_month_label.config(text=f"{calendar.month_name[month]} {year}")
            mechanic = self.mechanic_name
        else:
            cal_frame = self.calendar_frame
            for widget in cal_frame.winfo_children():
                widget.destroy()
            self.month_label.config(text=f"{calendar.month_name[month]} {year}")
            mechanic = self.selected_mechanic.get() if hasattr(self, 'selected_mechanic') and self.selected_mechanic.get() else None
            if not mechanic:
                # No mechanics in system, show empty calendar
                return

        # Header
        for col, day in enumerate(days):
            ttk.Label(cal_frame, text=day, anchor='center', width=18).grid(row=0, column=col, padx=2, pady=2)

        # Fetch schedules for this mechanic and month
        cursor = self.conn.cursor()
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-31"
        cursor.execute('''SELECT id, mechanic, start_time, end_time, task FROM schedules
                          WHERE mechanic=? AND date(start_time) BETWEEN ? AND ?''', (mechanic, start_date, end_date))
        schedules = cursor.fetchall()
        # Map day -> list of schedules
        sched_map = {}
        for sid, mech, st, et, task in schedules:
            try:
                day = int(st.split()[0].split('-')[2])
            except Exception:
                continue
            sched_map.setdefault(day, []).append((sid, st, et, task))

        # Calendar grid
        for row, week in enumerate(month_days, start=1):
            for col, day in enumerate(week):
                cell = ttk.Frame(cal_frame, relief='ridge', borderwidth=2, width=140, height=90)
                cell.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
                cell.grid_propagate(False)
                if day != 0:
                    ttk.Label(cell, text=str(day), anchor='ne', font=('Orbitron', 11)).pack(anchor='ne', padx=2, pady=2)
                    # Show schedules for this day
                    if day in sched_map:
                        for sid, st, et, task in sched_map[day]:
                            sched_lbl = ttk.Label(cell, text=f"{task}\n{st[-5:]}-{et[-5:]}", style='TLabel', background='#1e90ff', foreground='white')
                            sched_lbl.pack(fill=tk.X, padx=1, pady=1)
                            # Add edit/delete buttons for each schedule
                            btns = ttk.Frame(cell)
                            btns.pack(anchor='w', pady=1)
                            ttk.Button(btns, text="✎", width=2, command=lambda s=sid, t=tab: self.edit_schedule(s, t)).pack(side=tk.LEFT)
                            ttk.Button(btns, text="🗑", width=2, command=lambda s=sid, t=tab: self.delete_schedule_by_id(s, t)).pack(side=tk.LEFT)
                else:
                    ttk.Label(cell, text="", width=12).pack()

    def add_schedule(self, mechanic=None, tab=None):
        win = tk.Toplevel(self.root)
        win.title("Add Schedule")
        cursor = self.conn.cursor()
        if self.user_role == 'admin' and not mechanic:
            cursor.execute('SELECT full_name FROM users WHERE role="mechanic"')
            mechanics = [row[0] for row in cursor.fetchall()]
        else:
            mechanics = [mechanic or self.mechanic_name]

        ttk.Label(win, text="Mechanic:").grid(row=0, column=0, padx=5, pady=5)
        mechanic_cb = ttk.Combobox(win, values=mechanics, state='readonly')
        mechanic_cb.grid(row=0, column=1, padx=5, pady=5)
        mechanic_cb.set(mechanics[0] if mechanics else "") # Set default value

        ttk.Label(win, text="Start (YYYY-MM-DD HH:MM):").grid(row=1, column=0, padx=5, pady=5)
        start = ttk.Entry(win)
        start.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(win, text="End (YYYY-MM-DD HH:MM):").grid(row=2, column=0, padx=5, pady=5)
        end = ttk.Entry(win)
        end.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(win, text="Task:").grid(row=3, column=0, padx=5, pady=5)
        task = ttk.Entry(win)
        task.grid(row=3, column=1, padx=5, pady=5)

        def save():
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO schedules 
                            (mechanic, start_time, end_time, task)
                            VALUES (?, ?, ?, ?)''',
                           (mechanic_cb.get(), start.get(), end.get(), task.get()))
            self.conn.commit()
            win.destroy()
            if tab:
                self.update_monthly_calendar_display(tab=tab)
            else:
                self.update_monthly_calendar_display()

        ttk.Button(win, text="Save", command=save).grid(row=4, columnspan=2, pady=10)

    def edit_schedule(self, schedule_id, tab=None):
        cursor = self.conn.cursor()
        cursor.execute('SELECT mechanic, start_time, end_time, task FROM schedules WHERE id=?', (schedule_id,))
        row = cursor.fetchone()
        if not row:
            return
        win = tk.Toplevel(self.root)
        win.title("Edit Schedule")
        mechanic, start_val, end_val, task_val = row

        ttk.Label(win, text="Start (YYYY-MM-DD HH:MM):").grid(row=0, column=0, padx=5, pady=5)
        start = ttk.Entry(win)
        start.insert(0, start_val)
        start.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(win, text="End (YYYY-MM-DD HH:MM):").grid(row=1, column=0, padx=5, pady=5)
        end = ttk.Entry(win)
        end.insert(0, end_val)
        end.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(win, text="Task:").grid(row=2, column=0, padx=5, pady=5)
        task = ttk.Entry(win)
        task.insert(0, task_val)
        task.grid(row=2, column=1, padx=5, pady=5)

        def save():
            cursor = self.conn.cursor()
            cursor.execute('''UPDATE schedules SET start_time=?, end_time=?, task=? WHERE id=?''',
                           (start.get(), end.get(), task.get(), schedule_id))
            self.conn.commit()
            win.destroy()
            if tab:
                self.update_monthly_calendar_display(tab=tab)
            else:
                self.update_monthly_calendar_display()

        ttk.Button(win, text="Save Changes", command=save).grid(row=3, columnspan=2, pady=10)

    def delete_schedule_by_id(self, schedule_id, tab=None):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM schedules WHERE id=?', (schedule_id,))
        self.conn.commit()
        if tab:
            self.update_monthly_calendar_display(tab=tab)
        else:
            self.update_monthly_calendar_display()

    # ================== MECHANICS MANAGEMENT ==================
    def _create_mechanics_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Mechanics")

        self.mechanics_tree = ttk.Treeview(tab, columns=('Username', 'Role'), show='headings')
        self.mechanics_tree.heading('#0', text='Full Name')
        self.mechanics_tree.heading('Username', text='Username')
        self.mechanics_tree.heading('Role', text='Role')
        self.mechanics_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Mechanic", command=self.add_mechanic).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Mechanic", command=self.remove_mechanic).pack(side=tk.LEFT, padx=5)

        self.update_mechanics_display()

    # ================== INVENTORY TAB ==================
    def _create_inventory_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Inventory")

        self.inventory_tree = ttk.Treeview(tab, columns=('Quantity', 'Price', 'Supplier', 'Last Ordered'),
                                           show='headings')
        self.inventory_tree.heading('#0', text='Part')
        self.inventory_tree.heading('Quantity', text='Quantity')
        self.inventory_tree.heading('Price', text='Price')
        self.inventory_tree.heading('Supplier', text='Supplier')
        self.inventory_tree.heading('Last Ordered', text='Last Ordered')
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Order Parts", command=self.order_parts).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Add Part", command=self.add_part_dialog).pack(side=tk.LEFT, padx=5)
        self.update_inventory_display()

        # Add essential mechanic parts if not already present
        self.add_essential_parts()

    def add_part_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add New Part")

        ttk.Label(win, text="Part Name:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        name_entry = ttk.Entry(win)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(win, text="Quantity:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        qty_entry = ttk.Entry(win)
        qty_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(win, text="Price:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        price_entry = ttk.Entry(win)
        price_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(win, text="Supplier:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        supplier_entry = ttk.Entry(win)
        supplier_entry.grid(row=3, column=1, padx=10, pady=5)

        def add_part():
            name = name_entry.get().strip()
            try:
                qty = int(qty_entry.get())
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Quantity and Price must be numbers.")
                return
            supplier = supplier_entry.get().strip()
            if not name or not supplier:
                messagebox.showerror("Error", "All fields are required.")
                return
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    '''INSERT INTO inventory (part_name, quantity, price, supplier, last_ordered)
                       VALUES (?, ?, ?, ?, ?)''',
                    (name, qty, price, supplier, None)
                )
                self.conn.commit()
                self.update_inventory_display()
                win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Part already exists.")

        ttk.Button(win, text="Add", command=add_part).grid(row=4, columnspan=2, pady=10)

    # ================== CORE FUNCTIONALITY ==================
    def animate_header(self):
        current_color = self.header.cget('foreground')
        new_color = '#ff00ff' if current_color == '#00f3ff' else '#00f3ff'
        self.header.config(foreground=new_color)
        self.root.after(1000, self.animate_header)

    def add_customer(self):
        data = {k: v.get() for k, v in self.customer_entries.items()}
        if all(data.values()):
            try:
                cursor = self.conn.cursor()
                cursor.execute('''INSERT INTO customers 
                                (name, car_model, vin, issue, date_added)
                                VALUES (?, ?, ?, ?, ?)''',
                               (data['customer_name'], data['car_model'],
                                data['vin'], data['issue'],
                                datetime.datetime.now().isoformat()))

                cursor.execute('''INSERT INTO repairs 
                                (vehicle, customer_name, car_model, vin, issue, status, start_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                               (f"{data['car_model']} ({data['vin']})",
                                data['customer_name'], data['car_model'],
                                data['vin'], data['issue'], 'Pending',
                                datetime.datetime.now().isoformat()))

                self.conn.commit()
                self.update_repairs_display()
                messagebox.showinfo("Success", "Customer added successfully!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "VIN already exists in system")
        else:
            messagebox.showwarning("Error", "All fields are required")

    def update_repairs_display(self):
        self.repairs_tree.delete(*self.repairs_tree.get_children())
        cursor = self.conn.cursor()
        query = '''SELECT vehicle, status, start_date, issue, 
                   assigned_mechanic, priority, estimated_hours FROM repairs'''
        if self.user_role == 'mechanic':
            query += f" WHERE assigned_mechanic='{self.mechanic_name}'"
        cursor.execute(query)
        for row in cursor.fetchall():
            self.repairs_tree.insert('', 'end', text=row[0], values=row[1:])

    def update_schedule_display(self):
        self.schedule_tree.delete(*self.schedule_tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute('SELECT mechanic, start_time, end_time, task FROM schedules')
        for row in cursor.fetchall():
            self.schedule_tree.insert('', 'end', values=row)

    def update_my_schedule(self):
        self.my_schedule_tree.delete(*self.my_schedule_tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute('''SELECT start_time, end_time, task 
                          FROM schedules WHERE mechanic=?''',
                       (self.mechanic_name,))
        for row in cursor.fetchall():
            self.my_schedule_tree.insert('', 'end', values=row)

    def add_schedule(self):
        win = tk.Toplevel(self.root)
        win.title("Add Schedule")

        cursor = self.conn.cursor()
        cursor.execute('SELECT full_name FROM users WHERE role="mechanic"')
        mechanics = [row[0] for row in cursor.fetchall()]

        ttk.Label(win, text="Mechanic:").grid(row=0, column=0, padx=5, pady=5)
        mechanic = ttk.Combobox(win, values=mechanics)
        mechanic.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(win, text="Start (YYYY-MM-DD HH:MM):").grid(row=1, column=0, padx=5, pady=5)
        start = ttk.Entry(win)
        start.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(win, text="End (YYYY-MM-DD HH:MM):").grid(row=2, column=0, padx=5, pady=5)
        end = ttk.Entry(win)
        end.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(win, text="Task:").grid(row=3, column=0, padx=5, pady=5)
        task = ttk.Entry(win)
        task.grid(row=3, column=1, padx=5, pady=5)

        def save():
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO schedules 
                            (mechanic, start_time, end_time, task)
                            VALUES (?, ?, ?, ?)''',
                           (mechanic.get(), start.get(), end.get(), task.get()))
            self.conn.commit()
            self.update_schedule_display()
            win.destroy()

        ttk.Button(win, text="Save", command=save).grid(row=4, columnspan=2, pady=10)

    def delete_schedule(self):
        selected = self.schedule_tree.selection()
        if selected:
            item = self.schedule_tree.item(selected[0])
            mechanic, start_time = item['values'][0], item['values'][1]
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM schedules WHERE mechanic=? AND start_time=?', (mechanic, start_time))
            self.conn.commit()
            self.update_schedule_display()

    def update_mechanics_display(self):
        self.mechanics_tree.delete(*self.mechanics_tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute('SELECT full_name, username, role FROM users WHERE role="mechanic"')
        for row in cursor.fetchall():
            self.mechanics_tree.insert('', 'end', text=row[0], values=(row[1], row[2]))

    def add_mechanic(self):
        win = tk.Toplevel(self.root)
        win.title("Add Mechanic")

        ttk.Label(win, text="Full Name:").grid(row=0, column=0, padx=5, pady=5)
        full_name = ttk.Entry(win)
        full_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(win, text="Username:").grid(row=1, column=0, padx=5, pady=5)
        username = ttk.Entry(win)
        username.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(win, text="Password:").grid(row=2, column=0, padx=5, pady=5)
        password = ttk.Entry(win, show="*")
        password.grid(row=2, column=1, padx=5, pady=5)

        def save():
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO users 
                            (full_name, username, password, role)
                            VALUES (?, ?, ?, 'mechanic')''',
                           (full_name.get(), username.get(), password.get()))
            self.conn.commit()
            self.update_mechanics_display()
            win.destroy()

        ttk.Button(win, text="Save", command=save).grid(row=3, columnspan=2, pady=10)

    def remove_mechanic(self):
        selected = self.mechanics_tree.selection()
        if selected:
            item = self.mechanics_tree.item(selected[0])
            username = item['values'][0]
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM users WHERE username=?', (username,))
            self.conn.commit()
            self.update_mechanics_display()

    def show_repair_details(self, event=None):
        sel = self.repairs_tree.selection()
        if not sel: return
        vehicle = self.repairs_tree.item(sel[0])['text']
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM repairs WHERE vehicle=?', (vehicle,))
        r = cur.fetchone()
        win = tk.Toplevel(self.root)
        win.title("Repair Details")
        fields = [
            ("Customer:", r[2]),
            ("Vehicle:", r[1]),
            ("VIN:", r[4]),
            ("Issue:", r[5]),
            ("Assigned Mechanic:", r[7]),
            ("Priority:", r[8]),
            ("Estimated Hours:", r[9]),
            ("Estimated Cost:", r[10]),
            ("Start Date:", r[11]),
            ("End Date:", r[12] or "Ongoing"),
            ("Status:", r[6])
        ]
        for i, (lbl, val) in enumerate(fields):
            ttk.Label(win, text=lbl).grid(row=i, column=0, sticky='e', padx=5, pady=2)
            ttk.Label(win, text=val).grid(row=i, column=1, sticky='w', padx=5, pady=2)

    def edit_repair(self):
        sel = self.repairs_tree.selection()
        if not sel: return
        vehicle = self.repairs_tree.item(sel[0])['text']
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM repairs WHERE vehicle=?', (vehicle,))
        rd = cur.fetchone()
        win = tk.Toplevel(self.root)
        win.title("Edit Repair Details")
        fields = [
            ('Assigned Mechanic:', 'assigned_mechanic', 'entry', rd[7]),
            ('Priority:', 'priority', 'combo', ['Low', 'Medium', 'High'], rd[8]),
            ('Estimated Hours:', 'hours', 'entry', rd[9])
        ]
        entries = {}
        for i, (lbl, key, t, *rest) in enumerate(fields):
            ttk.Label(win, text=lbl).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            if t == 'entry':
                e = ttk.Entry(win);
                e.insert(0, rest[0]);
                e.grid(row=i, column=1, padx=10, pady=5)
                entries[key] = e
            else:
                c = ttk.Combobox(win, values=rest[0]);
                c.set(rest[1]);
                c.grid(row=i, column=1, padx=10, pady=5)
                entries[key] = c

        def save():
            cur.execute('''UPDATE repairs SET
                           assigned_mechanic=?, priority=?, estimated_hours=?
                           WHERE vehicle=?''', (
                entries['assigned_mechanic'].get(),
                entries['priority'].get(),
                float(entries['hours'].get() or 0),
                vehicle
            ))
            self.conn.commit();
            self.update_repairs_display();
            win.destroy()

        ttk.Button(win, text="Save Changes", command=save).grid(row=len(fields), columnspan=2, pady=10)

    def add_repair_notes(self):
        sel = self.repairs_tree.selection()
        if not sel: return
        vehicle = self.repairs_tree.item(sel[0])['text']
        cur = self.conn.cursor()
        cur.execute('SELECT issue FROM repairs WHERE vehicle=?', (vehicle,))
        text = cur.fetchone()[0]
        win = tk.Toplevel(self.root);
        win.title("Repair Notes")
        ttk.Label(win, text="Detailed Repair Notes:").pack(pady=10)
        ta = tk.Text(win, width=60, height=15, font=('Orbitron', 14));
        ta.insert('1.0', text);
        ta.pack(padx=20, pady=10)

        def save():
            cur.execute('UPDATE repairs SET issue=? WHERE vehicle=?', (ta.get('1.0', tk.END).strip(), vehicle))
            self.conn.commit();
            self.update_repairs_display();
            win.destroy()

        ttk.Button(win, text="Save Notes", command=save).pack(pady=10)

    def update_repairs_display(self):
        self.repairs_tree.delete(*self.repairs_tree.get_children())
        cur = self.conn.cursor()
        cur.execute(
            '''SELECT vehicle, status, start_date, issue, assigned_mechanic, priority, estimated_hours FROM repairs''')
        for row in cur.fetchall():
            try:
                dt = datetime.datetime.fromisoformat(row[2]);
                sd = dt.strftime('%Y-%m-%d %H:%M')
            except:
                sd = row[2]
            self.repairs_tree.insert('', 'end', text=row[0], values=(row[1], sd, row[3], row[4], row[5], row[6]))

    def add_customer(self):
        data = {k: v.get() for k, v in self.entries.items()}
        if all(data.values()):
            cur = self.conn.cursor()
            try:
                # Insert into customers
                cur.execute(
                    '''INSERT INTO customers (name, car_model, vin, issue, date_added)
                       VALUES (?, ?, ?, ?, ?)''',
                    (
                        data['customer_name'],
                        data['car_model'],
                        data['vin'],
                        data['issue'],
                        datetime.datetime.now().isoformat()
                    )
                )
                # Insert into repairs
                cur.execute(
                    '''INSERT OR IGNORE INTO repairs (vehicle, customer_name, car_model, vin, issue, status, start_date)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (
                        f"{data['car_model']} ({data['vin']})",
                        data['customer_name'],
                        data['car_model'],
                        data['vin'],
                        data['issue'],
                        'Pending',
                        datetime.datetime.now().isoformat()
                    )
                )
                # If vin exists, update existing record instead
                cur.execute(
                    '''UPDATE repairs SET
                           customer_name=?, car_model=?, issue=?, status=?, start_date=?
                       WHERE vin=?''',
                    (
                        data['customer_name'],
                        data['car_model'],
                        data['issue'],
                        'Pending',
                        datetime.datetime.now().isoformat(),
                        data['vin']
                    )
                )
                self.conn.commit()
                self.update_repairs_display()
                self.clear_form()
                self.animate_success()
            except sqlite3.Error as e:
                self.conn.rollback()
                messagebox.showerror("Database Error", str(e))
        else:
            messagebox.showwarning("Input Error", "All fields required")

    def update_inventory_display(self):
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        cur = self.conn.cursor()
        for part, qty, price, supplier, lo in cur.execute('SELECT part_name, quantity, price, supplier, last_ordered FROM inventory'):
            self.inventory_tree.insert('', 'end', text=part, values=(qty, price, supplier, lo or 'Never'))

    def mark_repaired(self):
        sel = self.repairs_tree.selection()
        if sel:
            veh = self.repairs_tree.item(sel[0])['text']
            cur = self.conn.cursor()
            cur.execute('UPDATE repairs SET status=?, end_date=? WHERE vehicle=?',
                        ('Repaired', datetime.datetime.now().isoformat(), veh))
            self.conn.commit()
            self.update_repairs_display()

    def mark_pending(self):
        sel = self.repairs_tree.selection()
        if sel:
            veh = self.repairs_tree.item(sel[0])['text']
            cur = self.conn.cursor()
            cur.execute('UPDATE repairs SET status=? WHERE vehicle=?', ('Pending', veh))
            self.conn.commit()
            self.update_repairs_display()

    def order_parts(self):
        order_window = tk.Toplevel(self.root)
        order_window.title("Order Parts")

        ttk.Label(order_window, text="Select Part:").grid(row=0, column=0, padx=10, pady=5)
        parts = [row[0] for row in self.conn.cursor().execute('SELECT part_name FROM inventory')]
        part_combo = ttk.Combobox(order_window, values=parts, state='readonly')
        part_combo.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(order_window, text="Quantity to Order:").grid(row=1, column=0, padx=10, pady=5)
        qty_entry = ttk.Entry(order_window)
        qty_entry.grid(row=1, column=1, padx=10, pady=5)

        def confirm_order():
            try:
                part = part_combo.get()
                qty = int(qty_entry.get())
                if qty <= 0:
                    raise ValueError

                cursor = self.conn.cursor()
                cursor.execute('''UPDATE inventory SET quantity = quantity + ?, last_ordered = ? WHERE part_name = ?''',
                               (qty, datetime.datetime.now().isoformat(), part))
                self.conn.commit()
                self.update_inventory_display()
                messagebox.showinfo("Order Confirmation", f"Ordered {qty} units of {part}.")
                order_window.destroy()

            except ValueError:
                messagebox.showerror("Error", "Invalid quantity.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(order_window, text="Confirm Order", command=confirm_order).grid(row=2, columnspan=2, pady=10)

    def __del__(self):
        self.conn.close()

    def ship_parts(self):
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a part to ship.")
            return

        part = self.inventory_tree.item(selected[0])['text']
        quantity = self.inventory_tree.item(selected[0])['values'][0]

        def confirm_ship():
            try:
                ship_qty = int(ship_qty_entry.get())
                if ship_qty <= 0 or ship_qty > quantity:
                    raise ValueError("Invalid quantity")

                cursor = self.conn.cursor()
                cursor.execute('''UPDATE inventory SET quantity = quantity - ? WHERE part_name = ?''',
                               (ship_qty, part))
                self.conn.commit()
                self.update_inventory_display()
                messagebox.showinfo("Success", f"Shipped {ship_qty} units of {part}.")
                ship_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity.")

        ship_window = tk.Toplevel(self.root)
        ship_window.title("Ship Parts")

        ttk.Label(ship_window, text=f"Part: {part}").pack(pady=5)
        ttk.Label(ship_window, text=f"Available Quantity: {quantity}").pack(pady=5)

        ttk.Label(ship_window, text="Quantity to Ship:").pack(pady=5)
        ship_qty_entry = ttk.Entry(ship_window)
        ship_qty_entry.pack(pady=5)

        ttk.Button(ship_window, text="Confirm", command=confirm_ship).pack(pady=10)


if __name__ == "__main__":
    root = ttk.Window()
    LoginWindow(root)
    root.mainloop()