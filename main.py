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

        # Create a larger calendar-like grid for the month
        calendar_frame = ttk.Frame(tab)
        calendar_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        # Create header row for days
        for col, day in enumerate(days):
            ttk.Label(calendar_frame, text=day, anchor='center', width=20).grid(row=0, column=col, padx=10, pady=10)

        # Generate the current month's calendar
        import calendar
        year, month = datetime.datetime.now().year, datetime.datetime.now().month
        month_days = calendar.monthcalendar(year, month)

        for row, week in enumerate(month_days, start=1):
            for col, day in enumerate(week):
                cell = ttk.Frame(calendar_frame, relief='ridge', borderwidth=2, width=150, height=100)
                cell.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
                if day != 0:
                    ttk.Label(cell, text=str(day), anchor='ne', font=('Orbitron', 12)).pack(anchor='ne', padx=5, pady=5)

        # Populate the calendar with existing schedules
        self.update_monthly_calendar_display(calendar_frame, days, month_days, year, month)

        # Correctly initialize the schedule tree
        self.schedule_tree = ttk.Treeview(tab, columns=('Mechanic', 'Start Time', 'End Time', 'Task'), show='headings')
        self.schedule_tree.heading('Mechanic', text='Mechanic')
        self.schedule_tree.heading('Start Time', text='Start Time')
        self.schedule_tree.heading('End Time', text='End Time')
        self.schedule_tree.heading('Task', text='Task')
        self.schedule_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Add buttons for schedule management
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Schedule", command=self.add_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Schedule", command=self.delete_schedule).pack(side=tk.LEFT, padx=5)

        # Update schedule display method
        self.update_schedule_display()

    def update_monthly_calendar_display(self, calendar_frame, days, month_days, year, month):
        cursor = self.conn.cursor()
        cursor.execute('SELECT mechanic, start_time, end_time, task FROM schedules')
        schedules = cursor.fetchall()

        for schedule in schedules:
            mechanic, start_time, end_time, task = schedule
            start_date = datetime.datetime.strptime(start_time.split(' ')[0], '%Y-%m-%d')
            day = start_date.day

            for row, week in enumerate(month_days, start=1):
                if day in week:
                    col = week.index(day)
                    cell = calendar_frame.grid_slaves(row=row, column=col)[0]
                    label = ttk.Label(cell, text=f"{mechanic}\n{task}", anchor='center', background='lightblue')
                    label.pack(expand=True, fill=tk.BOTH)

    def _create_my_schedule_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="My Schedule")

        self.my_schedule_tree = ttk.Treeview(tab, columns=('Start', 'End', 'Task'), show='headings')
        for col in ['Start', 'End', 'Task']:
            self.my_schedule_tree.heading(col, text=col)
            self.my_schedule_tree.column(col, width=250)
        self.my_schedule_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.update_my_schedule()

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

        self.inventory_tree = ttk.Treeview(tab, columns=('Quantity', 'Last Ordered', 'Price', 'Supplier'),
                                           show='headings')
        self.inventory_tree.heading('#0', text='Part')
        self.inventory_tree.heading('Quantity', text='Quantity')
        self.inventory_tree.heading('Last Ordered', text='Last Ordered')
        self.inventory_tree.heading('Price', text='Price')
        self.inventory_tree.heading('Supplier', text='Supplier')
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Button(tab, text="Order Parts", command=self.order_parts).pack(pady=10)
        ttk.Button(tab, text="Ship Parts", command=self.ship_parts).pack(pady=10)
        self.update_inventory_display()

        # Add essential mechanic parts if not already present
        self.add_essential_parts()

    def add_essential_parts(self):
        essential_parts = [
            ('Spark Plugs', 15, 5.99),
            ('Brake Pads', 10, 25.50),
            ('Oil Filter', 20, 7.99),
            ('Timing Belt', 8, 45.00),
            ('Air Filter', 12, 12.50),
            ('Fuel Pump', 5, 89.99),
            ('Alternator', 7, 150.00),
            ('Battery', 10, 120.00),
            ('Radiator', 6, 200.00),
            ('Clutch Kit', 4, 250.00),
            ('Shock Absorbers', 8, 75.00),
            ('Headlights', 10, 30.00),
            ('Wiper Blades', 15, 15.00),
            ('Engine Oil', 25, 40.00),
            ('Transmission Fluid', 20, 35.00),
            ('Brake Rotors', 10, 60.00),
            ('Wheel Bearings', 8, 50.00),
            ('Control Arms', 6, 80.00),
            ('Ball Joints', 10, 20.00),
            ('Tie Rod Ends', 12, 25.00),
            ('Drive Belts', 15, 18.00),
            ('Water Pump', 5, 70.00),
            ('Thermostat', 10, 15.00),
            ('Ignition Coils', 8, 45.00),
            ('Starter Motor', 5, 130.00),
            ('Exhaust Muffler', 6, 90.00),
            ('Catalytic Converter', 4, 300.00),
            ('Oxygen Sensor', 10, 50.00),
            ('Fuel Injectors', 8, 100.00),
            ('Turbocharger', 3, 500.00),
            ('Timing Chain', 7, 85.00),
            ('Camshaft', 4, 250.00),
            ('Crankshaft', 3, 400.00),
            ('Piston Rings', 10, 35.00),
            ('Valve Cover Gasket', 12, 20.00),
            ('Cylinder Head', 2, 600.00),
            ('EGR Valve', 5, 120.00),
            ('Mass Airflow Sensor', 6, 150.00),
            ('Throttle Body', 4, 200.00)
        ]

        cursor = self.conn.cursor()
        for part, quantity, price in essential_parts:
            cursor.execute('''INSERT OR IGNORE INTO inventory (part_name, quantity, last_ordered) VALUES (?, ?, ?)''',
                           (part, quantity, None))
            cursor.execute('''ALTER TABLE inventory ADD COLUMN price REAL''')
            cursor.execute('''UPDATE inventory SET price = ? WHERE part_name = ?''', (price, part))
        self.conn.commit()
        self.update_inventory_display()

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
        for part, qty, lo in cur.execute('SELECT part_name, quantity, last_ordered FROM inventory'):
            self.inventory_tree.insert('', 'end', text=part, values=(qty, lo or 'Never'))

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
        cur = self.conn.cursor()
        ordered = []
        for part, qty in cur.execute('SELECT part_name, quantity FROM inventory'):
            if qty < 10:
                ordered.append(part)
                cur.execute('UPDATE inventory SET quantity=?, last_ordered=? WHERE part_name=?',
                            (qty + 20, datetime.datetime.now().isoformat(), part))
        self.conn.commit()
        if ordered:
            messagebox.showinfo("Quantum Order", f"Parts warping through subspace:', '.join(ordered)")
            self.update_inventory_display()
        else:
            messagebox.showinfo("Inventory Stable", "All systems nominal - stock levels OK")

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