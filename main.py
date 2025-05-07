import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
import sqlite3
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pyglet
import datetime

# Load custom font
pyglet.font.add_file('Orbitron-Medium.ttf')  # Place font file in same directory


class CosmicMechanicsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stellar Garage Manager")
        self.root.geometry("1400x900")

        # Configure cosmic style
        self.style = ttk.Style(theme='darkly')
        self._configure_styles()

        # Initialize database
        self.conn = sqlite3.connect('cosmic_garage.db')
        self.create_tables()

        # Create main interface
        self.create_widgets()

        # Start animations
        self.animate_header()

    def _configure_styles(self):
        # Custom cosmic theme
        self.style.configure('Cosmic.TButton', font=('Orbitron', 12),
                             bordercolor='#00f3ff', focusthickness=3)
        self.style.configure('Cosmic.TLabel', font=('Orbitron', 14),
                             foreground='#00f3ff')
        self.style.configure('Header.TLabel', font=('Orbitron', 24, 'bold'),
                             foreground='#ff00ff')

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS customers
                        (id INTEGER PRIMARY KEY,
                        name TEXT,
                        car_model TEXT,
                        vin TEXT,
                        issue TEXT,
                        date_added TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS repairs
                        (id INTEGER PRIMARY KEY,
                        vehicle TEXT,
                        status TEXT,
                        start_date TEXT,
                        end_date TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS inventory
                        (id INTEGER PRIMARY KEY,
                        part_name TEXT,
                        quantity INTEGER,
                        last_ordered TEXT)''')
        self.conn.commit()

    def create_widgets(self):
        # Main container with cosmic background
        self.bg_image = ImageTk.PhotoImage(Image.open('space_bg.jpg').resize((1400, 900)))
        bg_label = ttk.Label(self.root, image=self.bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Animated header
        self.header = ttk.Label(self.root, text="🚀 COSMIC VEHICLE WORKSHOP 🪐",
                                style='Header.TLabel')
        self.header.pack(pady=30)

        # Main notebook interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self._create_customer_tab()
        self._create_repairs_tab()
        self._create_inventory_tab()

    def _create_customer_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="New Customers")

        form_frame = ttk.Frame(tab)
        form_frame.pack(pady=20)

        entries = [
            ('Name', 'customer_name'),
            ('Car Model', 'car_model'),
            ('VIN', 'vin'),
            ('Issue', 'issue')
        ]

        self.entries = {}
        for label, key in entries:
            frame = ttk.Frame(form_frame)
            frame.pack(pady=10)
            ttk.Label(frame, text=label, style='Cosmic.TLabel').pack(side=tk.LEFT)
            entry = ttk.Entry(frame, width=30)
            entry.pack(side=tk.RIGHT, padx=10)
            self.entries[key] = entry

        add_btn = ttk.Button(form_frame, text="Add Customer",
                             style='Cosmic.TButton',
                             command=self.add_customer)
        add_btn.pack(pady=20)

    def _create_repairs_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Active Repairs")

        # Repair list with scrollbar
        self.repairs_tree = ttk.Treeview(tab, columns=('Status', 'Start Date'),
                                         show='headings')
        self.repairs_tree.heading('#0', text='Vehicle')
        self.repairs_tree.heading('Status', text='Status')
        self.repairs_tree.heading('Start Date', text='Start Date')
        self.repairs_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Controls
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Mark Repaired", style='Cosmic.TButton',
                   command=self.mark_repaired).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Mark Pending", style='Cosmic.TButton',
                   command=self.mark_pending).pack(side=tk.LEFT, padx=5)

        self.update_repairs_display()

    def _create_inventory_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Stellar Inventory")

        # Inventory list
        self.inventory_tree = ttk.Treeview(tab, columns=('Quantity', 'Last Ordered'),
                                           show='headings')
        self.inventory_tree.heading('#0', text='Part')
        self.inventory_tree.heading('Quantity', text='Quantity')
        self.inventory_tree.heading('Last Ordered', text='Last Ordered')
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Order button
        ttk.Button(tab, text="Quantum Order Parts", style='Cosmic.TButton',
                   command=self.order_parts).pack(pady=10)

        self.update_inventory_display()

    # Database operations
    def add_customer(self):
        data = {k: v.get() for k, v in self.entries.items()}
        if all(data.values()):
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO customers 
                            (name, car_model, vin, issue, date_added)
                            VALUES (?, ?, ?, ?, ?)''',
                           (data['customer_name'], data['car_model'], data['vin'],
                            data['issue'], datetime.datetime.now().isoformat()))

            cursor.execute('''INSERT INTO repairs 
                            (vehicle, status, start_date)
                            VALUES (?, ?, ?)''',
                           (f"{data['car_model']} ({data['vin']})",
                            'Pending', datetime.datetime.now().isoformat()))
            self.conn.commit()
            self.update_repairs_display()
            self.clear_form()
            self.animate_success()
        else:
            messagebox.showwarning("Input Error", "Please fill all fields")

    def update_repairs_display(self):
        self.repairs_tree.delete(*self.repairs_tree.get_children())
        cursor = self.conn.cursor()
        for row in cursor.execute('SELECT vehicle, status, start_date FROM repairs'):
            self.repairs_tree.insert('', 'end', text=row[0],
                                     values=(row[1], row[2]))

    def update_inventory_display(self):
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        cursor = self.conn.cursor()
        for row in cursor.execute('SELECT part_name, quantity, last_ordered FROM inventory'):
            self.inventory_tree.insert('', 'end', text=row[0],
                                       values=(row[1], row[2] or 'Never'))

    # Animations
    def animate_header(self):
        current_color = self.header.cget('foreground')
        new_color = '#ff00ff' if current_color == '#00f3ff' else '#00f3ff'
        self.header.config(foreground=new_color)
        self.root.after(1000, self.animate_header)

    def animate_success(self):
        original_bg = self.style.colors.get('bg')
        for i in range(5):
            self.root.after(100 * i, lambda: self.header.config(
                background='#00ff00' if i % 2 else original_bg))

    # Other methods
    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def mark_repaired(self):
        selected = self.repairs_tree.selection()
        if selected:
            vehicle = self.repairs_tree.item(selected[0])['text']
            cursor = self.conn.cursor()
            cursor.execute('''UPDATE repairs SET status=?, end_date=?
                            WHERE vehicle=?''',
                           ('Repaired', datetime.datetime.now().isoformat(), vehicle))
            self.conn.commit()
            self.update_repairs_display()

    def order_parts(self):
        cursor = self.conn.cursor()
        ordered = []
        for item in cursor.execute('SELECT part_name, quantity FROM inventory'):
            if item[1] < 10:
                ordered.append(item[0])
                cursor.execute('''UPDATE inventory SET quantity=?, last_ordered=?
                                WHERE part_name=?''',
                               (item[1] + 20, datetime.datetime.now().isoformat(), item[0]))
        self.conn.commit()
        if ordered:
            messagebox.showinfo("Quantum Order",
                                f"Parts warping through subspace:\n{', '.join(ordered)}")
            self.update_inventory_display()
        else:
            messagebox.showinfo("Inventory Stable", "All systems nominal - stock levels OK")


if __name__ == "__main__":
    root = ttk.Window()
    app = CosmicMechanicsApp(root)
    root.mainloop()