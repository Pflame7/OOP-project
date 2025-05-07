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

        # Create tabs with improved spacing
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

        # Repair list with improved column widths
        self.repairs_tree = ttk.Treeview(tab, columns=('Status', 'Start Date'),
                                         show='headings')
        self.repairs_tree.heading('#0', text='Vehicle', anchor=tk.W)
        self.repairs_tree.column('#0', width=400, minwidth=300)
        self.repairs_tree.heading('Status', text='Status', anchor=tk.W)
        self.repairs_tree.column('Status', width=200, minwidth=150)
        self.repairs_tree.heading('Start Date', text='Start Date', anchor=tk.W)
        self.repairs_tree.column('Start Date', width=300, minwidth=250)
        self.repairs_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Button container with responsive layout
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Mark Repaired", command=self.mark_repaired) \
            .pack(side=tk.LEFT, padx=20, ipadx=20, ipady=10)
        ttk.Button(btn_frame, text="Mark Pending", command=self.mark_pending) \
            .pack(side=tk.LEFT, padx=20, ipadx=20, ipady=10)

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
    def create_tables(self):
        """Create or upgrade database tables"""
        cursor = self.conn.cursor()

        # Create customers table
        cursor.execute('''CREATE TABLE IF NOT EXISTS customers
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT,
                         car_model TEXT,
                         vin TEXT UNIQUE,
                         issue TEXT,
                         date_added TEXT)''')

        # Create repairs table with new schema
        cursor.execute('''CREATE TABLE IF NOT EXISTS repairs
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         vehicle TEXT,
                         status TEXT,
                         start_date TEXT,
                         end_date TEXT,
                         issue TEXT,
                         assigned_mechanic TEXT,
                         priority TEXT,
                         estimated_hours REAL)''')

        # Create inventory table
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventory
                        (part_name TEXT PRIMARY KEY,
                         quantity INTEGER,
                         last_ordered TEXT)''')

        # Add any missing columns to repairs table
        cursor.execute('PRAGMA table_info(repairs)')
        existing_columns = [col[1] for col in cursor.fetchall()]
        required_columns = ['issue', 'assigned_mechanic', 'priority', 'estimated_hours']

        for col in required_columns:
            if col not in existing_columns:
                cursor.execute(f'ALTER TABLE repairs ADD COLUMN {col} TEXT')

        self.conn.commit()
    def _create_repairs_tab(self):
        """Create repairs tab with expanded columns and controls"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Active Repairs")

        # Expanded Treeview columns
        self.repairs_tree = ttk.Treeview(tab, columns=(
            'Status', 'Start Date', 'Issue', 'Mechanic', 'Priority', 'Hours'
        ), show='headings')

        # Configure columns
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
                self.repairs_tree.column(col_id, width=width, minwidth=width - 50)
            else:
                self.repairs_tree.heading(col_id, text=heading, anchor=tk.W)
                self.repairs_tree.column(col_id, width=width, minwidth=width - 50)

        self.repairs_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # New button container
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=20)

        controls = [
            ('Mark Repaired', self.mark_repaired),
            ('Mark Pending', self.mark_pending),
            ('Edit Repair', self.edit_repair),
            ('Add Notes', self.add_repair_notes)
        ]

        for text, cmd in controls:
            ttk.Button(btn_frame, text=text, command=cmd,
                       style='TButton').pack(side=tk.LEFT, padx=10)

    def update_repairs_display(self):
        """Update repairs list with formatted dates and enhanced info"""
        self.repairs_tree.delete(*self.repairs_tree.get_children())
        cursor = self.conn.cursor()
        query = '''SELECT vehicle, status, start_date, issue,
                            assigned_mechanic, priority, estimated_hours
                     FROM repairs'''

        for row in cursor.execute(query):
            # Format start date
            try:
                dt = datetime.datetime.fromisoformat(row[2])
                formatted_date = dt.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = row[2]

            self.repairs_tree.insert('', 'end', text=row[0],
                                     values=(row[1], formatted_date, row[3], row[4], row[5], row[6]))

    def edit_repair(self):
        """Edit repair details dialog"""
        selected = self.repairs_tree.selection()
        if not selected:
            return

        vehicle = self.repairs_tree.item(selected[0])['text']
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM repairs WHERE vehicle=?''', (vehicle,))
        repair_data = cursor.fetchone()

        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Repair Details")

        # Form fields
        fields = [
            ('Assigned Mechanic:', 'assigned_mechanic', 'entry', repair_data[6]),
            ('Priority:', 'priority', 'combo', ['Low', 'Medium', 'High'], repair_data[7]),
            ('Estimated Hours:', 'hours', 'entry', repair_data[8])
        ]

        entries = {}
        for i, (label, key, type_, *rest) in enumerate(fields):
            ttk.Label(edit_win, text=label).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            if type_ == 'entry':
                entry = ttk.Entry(edit_win)
                entry.insert(0, rest[0] if rest[0] else "")
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries[key] = entry
            elif type_ == 'combo':
                combo = ttk.Combobox(edit_win, values=rest[0])
                combo.set(rest[1] if rest[1] else "Medium")
                combo.grid(row=i, column=1, padx=10, pady=5)
                entries[key] = combo

        # Save handler
        def save_changes():
            updates = (
                entries['assigned_mechanic'].get(),
                entries['priority'].get(),
                float(entries['hours'].get() or 0),
                vehicle
            )
            cursor.execute('''UPDATE repairs SET
                              assigned_mechanic=?,
                              priority=?,
                              estimated_hours=?
                            WHERE vehicle=?''', updates)
            self.conn.commit()
            self.update_repairs_display()
            edit_win.destroy()

        ttk.Button(edit_win, text="Save Changes", command=save_changes) \
            .grid(row=len(fields), columnspan=2, pady=10)

    def add_repair_notes(self):
        """Add detailed notes to repair"""
        selected = self.repairs_tree.selection()
        if not selected:
            return

        vehicle = self.repairs_tree.item(selected[0])['text']
        cursor = self.conn.cursor()
        cursor.execute('SELECT issue FROM repairs WHERE vehicle=?', (vehicle,))
        current_issue = cursor.fetchone()[0]

        note_win = tk.Toplevel(self.root)
        note_win.title("Repair Notes")

        ttk.Label(note_win, text="Detailed Repair Notes:").pack(pady=10)
        text_area = tk.Text(note_win, width=60, height=15,
                            font=('Orbitron', 14))
        text_area.insert('1.0', current_issue)
        text_area.pack(padx=20, pady=10)

        def save_notes():
            cursor.execute('''UPDATE repairs SET issue=?
                             WHERE vehicle=?''',
                           (text_area.get('1.0', tk.END).strip(), vehicle))
            self.conn.commit()
            self.update_repairs_display()
            note_win.destroy()

        ttk.Button(note_win, text="Save Notes", command=save_notes) \
            .pack(pady=10)

    def add_customer(self):
        data = {k: v.get() for k, v in self.entries.items()}
        if all(data.values()):
            cursor = self.conn.cursor()
            try:
                # Insert customer
                cursor.execute('''INSERT INTO customers 
                                (name, car_model, vin, issue, date_added)
                                VALUES (?, ?, ?, ?, ?)''',
                               (data['customer_name'], data['car_model'],
                                data['vin'], data['issue'],
                                datetime.datetime.now().isoformat()))

                # Insert repair with proper columns
                cursor.execute('''INSERT INTO repairs 
                                (vehicle, status, start_date, issue)
                                VALUES (?, ?, ?, ?)''',
                               (f"{data['car_model']} ({data['vin']})",
                                'Pending',
                                datetime.datetime.now().isoformat(),
                                data['issue']))
                self.conn.commit()
                self.update_repairs_display()
                self.clear_form()
                self.animate_success()
            except sqlite3.Error as e:
                self.conn.rollback()
                messagebox.showerror("Database Error", f"Error: {str(e)}")
        else:
            messagebox.showwarning("Input Error", "All fields required")
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

    def mark_pending(self):
        selected = self.repairs_tree.selection()
        if selected:
            vehicle = self.repairs_tree.item(selected[0])['text']
            cursor = self.conn.cursor()
            cursor.execute('''UPDATE repairs SET status=? WHERE vehicle=?''',
                           ('Pending', vehicle))
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
    root.minsize(1000, 700)  # Set minimum window size
    app = CosmicMechanicsApp(root)
    root.mainloop()