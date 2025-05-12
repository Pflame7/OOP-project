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
        self.root.state('zoomed')  # Start maximized
        self.style = ttk.Style(theme='darkly')
        self._configure_styles()
        self.conn = sqlite3.connect('cosmic_garage.db')
        self.create_tables()
        self.create_widgets()
        self.animate_header()

    def _configure_styles(self):
        # Base font configuration
        self.style.configure('.', font=('Orbitron', 16))
        self.style.configure('Header.TLabel', font=('Orbitron', 28, 'bold'))
        self.style.configure('TButton', font=('Orbitron', 18))
        self.style.configure('Treeview.Heading', font=('Orbitron', 18, 'bold'))
        self.style.configure('Treeview', font=('Orbitron', 16), rowheight=35)
        self.style.configure('TEntry', font=('Orbitron', 16))

    def create_widgets(self):
        # Main container with responsive layout
        self.bg_image = ImageTk.PhotoImage(Image.open('space_bg.jpg').resize(
            (self.root.winfo_screenwidth(), self.root.winfo_screenheight())))
        bg_label = ttk.Label(self.root, image=self.bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Header with responsive padding
        self.header = ttk.Label(self.root, text="🚀 COSMIC VEHICLE WORKSHOP 🪐",
                                style='Header.TLabel')
        self.header.pack(pady=(30, 20))

        # Responsive notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create tabs
        self._create_customer_tab()
        self._create_repairs_tab()
        self._create_inventory_tab()

        # Configure grid weights for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _create_customer_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="New Customers")

        form_frame = ttk.Frame(tab)
        form_frame.pack(pady=30, padx=30, fill=tk.BOTH, expand=True)

        entries = [
            ('Name:', 'customer_name'),
            ('Car Model:', 'car_model'),
            ('VIN:', 'vin'),
            ('Issue:', 'issue')
        ]

        self.entries = {}
        for label, key in entries:
            frame = ttk.Frame(form_frame)
            frame.pack(pady=15, fill=tk.X)
            ttk.Label(frame, text=label, style='TLabel', width=15).pack(side=tk.LEFT, padx=10)
            entry = ttk.Entry(frame, width=30)
            entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=10)
            self.entries[key] = entry

        add_btn = ttk.Button(form_frame, text="Add Customer",
                             style='TButton', command=self.add_customer)
        add_btn.pack(pady=30)

    def _create_repairs_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Active Repairs")

        # Expanded Treeview columns
        self.repairs_tree = ttk.Treeview(tab, columns=(
            'Status', 'Start Date', 'Issue', 'Mechanic', 'Priority', 'Hours'
        ), show='headings')

        columns = [
            ('#0', 'Vehicle', 300),
            ('Status', 'Status', 120),
            ('Start Date', 'Start Date', 180),
            ('Issue', 'Issue', 400),
            ('Mechanic', 'Mechanic', 150),
            ('Priority', 'Priority', 100),
            ('Hours', 'Est. Hours', 100)
        ]

        for col_id, heading, width in columns:
            if col_id == '#0':
                self.repairs_tree.heading(col_id, text=heading, anchor=tk.W)
                self.repairs_tree.column(col_id, width=width, minwidth=width-50)
            else:
                self.repairs_tree.heading(col_id, text=heading, anchor=tk.W)
                self.repairs_tree.column(col_id, width=width, minwidth=width-50)

        self.repairs_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=20)

        controls = [
            ('Mark Repaired', self.mark_repaired),
            ('Mark Pending', self.mark_pending),
            ('Edit Repair', self.edit_repair),
            ('Add Notes', self.add_repair_notes)
        ]

        for text, cmd in controls:
            ttk.Button(btn_frame, text=text, command=cmd, style='TButton').pack(side=tk.LEFT, padx=10)

    def _create_inventory_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Stellar Inventory")

        self.inventory_tree = ttk.Treeview(tab, columns=('Quantity', 'Last Ordered'), show='headings')
        self.inventory_tree.heading('#0', text='Part')
        self.inventory_tree.heading('Quantity', text='Quantity')
        self.inventory_tree.heading('Last Ordered', text='Last Ordered')
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Button(tab, text="Quantum Order Parts", style='TButton', command=self.order_parts).pack(pady=10)
        self.update_inventory_display()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Repairs table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='repairs'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(repairs)")
            cols = [c[1] for c in cursor.fetchall()]
            if 'priority' not in cols:
                cursor.execute("ALTER TABLE repairs ADD COLUMN priority TEXT DEFAULT 'Medium'")
        else:
            cursor.execute('''CREATE TABLE repairs (
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
                                notes TEXT
                              )''')
        # Customers
        cursor.execute('''CREATE TABLE IF NOT EXISTS customers
                          (id INTEGER PRIMARY KEY,
                           name TEXT,
                           car_model TEXT,
                           vin TEXT UNIQUE,
                           issue TEXT,
                           date_added TEXT)''')
        # Inventory
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventory
                          (id INTEGER PRIMARY KEY,
                           part_name TEXT UNIQUE,
                           quantity INTEGER,
                           last_ordered TEXT)''')
        cursor.execute('SELECT COUNT(*) FROM inventory')
        if cursor.fetchone()[0] == 0:
            initial = [('Spark Plugs', 15), ('Brake Pads', 10), ('Oil Filter', 20), ('Timing Belt', 8)]
            cursor.executemany('INSERT INTO inventory (part_name, quantity) VALUES (?,?)', initial)
        self.conn.commit()

    # Animations
    def animate_header(self):
        current_color = self.header.cget('foreground')
        new_color = '#ff00ff' if current_color == '#00f3ff' else '#00f3ff'
        self.header.config(foreground=new_color)
        self.root.after(1000, self.animate_header)

    def animate_success(self):
        original_bg = self.style.colors.get('bg')
        for i in range(5):
            self.root.after(100 * i, lambda i=i: self.header.config(
                background='#00ff00' if i % 2 else original_bg))

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
            ("Customer:",        r[2]),
            ("Vehicle:",         r[1]),
            ("VIN:",             r[4]),
            ("Issue:",           r[5]),
            ("Assigned Mechanic:",r[7]),
            ("Priority:",        r[8]),
            ("Estimated Hours:", r[9]),
            ("Estimated Cost:",  r[10]),
            ("Start Date:",      r[11]),
            ("End Date:",        r[12] or "Ongoing"),
            ("Status:",          r[6])
        ]
        for i,(lbl,val) in enumerate(fields):
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
            ('Priority:',          'priority',           'combo', ['Low','Medium','High'], rd[8]),
            ('Estimated Hours:',   'hours',              'entry', rd[9])
        ]
        entries = {}
        for i,(lbl,key,t,*rest) in enumerate(fields):
            ttk.Label(win, text=lbl).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            if t=='entry':
                e = ttk.Entry(win); e.insert(0, rest[0]); e.grid(row=i, column=1, padx=10, pady=5)
                entries[key]=e
            else:
                c = ttk.Combobox(win, values=rest[0]); c.set(rest[1]); c.grid(row=i, column=1, padx=10, pady=5)
                entries[key]=c
        def save():
            cur.execute('''UPDATE repairs SET
                           assigned_mechanic=?, priority=?, estimated_hours=?
                           WHERE vehicle=?''', (
                entries['assigned_mechanic'].get(),
                entries['priority'].get(),
                float(entries['hours'].get() or 0),
                vehicle
            ))
            self.conn.commit(); self.update_repairs_display(); win.destroy()
        ttk.Button(win, text="Save Changes", command=save).grid(row=len(fields), columnspan=2, pady=10)

    def add_repair_notes(self):
        sel = self.repairs_tree.selection()
        if not sel: return
        vehicle = self.repairs_tree.item(sel[0])['text']
        cur = self.conn.cursor()
        cur.execute('SELECT issue FROM repairs WHERE vehicle=?', (vehicle,))
        text = cur.fetchone()[0]
        win = tk.Toplevel(self.root); win.title("Repair Notes")
        ttk.Label(win, text="Detailed Repair Notes:").pack(pady=10)
        ta = tk.Text(win, width=60, height=15, font=('Orbitron',14)); ta.insert('1.0', text); ta.pack(padx=20,pady=10)
        def save():
            cur.execute('UPDATE repairs SET issue=? WHERE vehicle=?', (ta.get('1.0',tk.END).strip(), vehicle))
            self.conn.commit(); self.update_repairs_display(); win.destroy()
        ttk.Button(win, text="Save Notes", command=save).pack(pady=10)

    def update_repairs_display(self):
        self.repairs_tree.delete(*self.repairs_tree.get_children())
        cur = self.conn.cursor()
        cur.execute('''SELECT vehicle, status, start_date, issue, assigned_mechanic, priority, estimated_hours FROM repairs''')
        for row in cur.fetchall():
            try:
                dt = datetime.datetime.fromisoformat(row[2]); sd = dt.strftime('%Y-%m-%d %H:%M')
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
            cur.execute('UPDATE repairs SET status=?, end_date=? WHERE vehicle=?', ('Repaired', datetime.datetime.now().isoformat(), veh))
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
                cur.execute('UPDATE inventory SET quantity=?, last_ordered=? WHERE part_name=?', (qty+20, datetime.datetime.now().isoformat(), part))
        self.conn.commit()
        if ordered:
            messagebox.showinfo("Quantum Order", f"Parts warping through subspace:', '.join(ordered)")
            self.update_inventory_display()
        else:
            messagebox.showinfo("Inventory Stable", "All systems nominal - stock levels OK")

if __name__ == "__main__":
    root = ttk.Window()
    root.minsize(1000, 700)
    app = CosmicMechanicsApp(root)
    root.mainloop()
