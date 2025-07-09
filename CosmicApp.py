import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import datetime

# Brighter Terran color palette
TERRAN_TEXT2 = 	"#FFFFFF"
TERRAN_BG = "#22304a"
TERRAN_ACCENT = "#4a6fa5"
TERRAN_HIGHLIGHT = "#00cfff"
TERRAN_TEXT = "#222"  # Use dark text for contrast
CALENDAR_CELL_GRAY = "#e0e0e0"
CALENDAR_CELL_TODAY = "#b0b0b0"
CALENDAR_CELL_DONE = "#a8ffb0"
CALENDAR_CELL_LATE = "#ffe066"
CALENDAR_CELL_TASK = "#5ecfff"
CALENDAR_CELL_SERVICE = "#ffd580"

def add_custom_titlebar(window, title="Terran Garage Manager", exit_callback=None):
    window.overrideredirect(True)
    titlebar = tk.Frame(window, bg=TERRAN_ACCENT, relief="raised", bd=0, highlightthickness=0)
    titlebar.pack(fill=tk.X, side=tk.TOP)
    title_label = tk.Label(titlebar, text=title, bg=TERRAN_ACCENT, fg=TERRAN_TEXT, font=("Orbitron", 14, "bold"))
    title_label.pack(side=tk.LEFT, padx=10, pady=2)
    exit_btn = tk.Button(
        titlebar, text="✕", bg=TERRAN_ACCENT, fg=TERRAN_TEXT, borderwidth=0, font=("Arial", 14, "bold"),
        activebackground="#b22222", activeforeground="#fff",
        command=exit_callback if exit_callback else window.quit
    )
    exit_btn.pack(side=tk.RIGHT, padx=(0, 2), pady=2)
    min_btn = tk.Button(
        titlebar, text="—", bg=TERRAN_ACCENT, fg=TERRAN_TEXT, borderwidth=0, font=("Arial", 14, "bold"),
        activebackground=TERRAN_BG, activeforeground=TERRAN_HIGHLIGHT,
        command=lambda: window.iconify()
    )
    min_btn.pack(side=tk.RIGHT, padx=(0, 2), pady=2)
    def start_move(event):
        window._drag_start_x = event.x_root
        window._drag_start_y = event.y_root
        window._win_x = window.winfo_x()
        window._win_y = window.winfo_y()
    def do_move(event):
        dx = event.x_root - window._drag_start_x
        dy = event.y_root - window._drag_start_y
        new_x = window._win_x + dx
        new_y = window._win_y + dy
        window.geometry(f"+{new_x}+{new_y}")
    titlebar.bind("<ButtonPress-1>", start_move)
    titlebar.bind("<B1-Motion>", do_move)
    spacer = tk.Frame(window, height=16, bg=TERRAN_BG)
    spacer.pack(fill=tk.X)

class CosmicApp:
    def __init__(self, root, user_role, mechanic_name=None, terran_style=True):
        add_custom_titlebar(root, "Garage Manager", exit_callback=root.quit)
        self.root = root
        self.user_role = user_role
        self.mechanic_name = mechanic_name
        self.terran_style = terran_style
        self.current_theme = "dark" if self.terran_style else "light"
        self.root.title("Garage Manager")
        self.root.state('zoomed')
        self.style = ttk.Style(theme='cyborg')
        self.conn = sqlite3.connect('cosmic_garage.db')

        if terran_style:
            self.root.configure(bg=TERRAN_BG)

        self._configure_styles()
        self.cal_year = 2025  # Default to year 2025
        self.cal_month = 1
        self.create_widgets()
        self.animate_header()

    def _configure_styles(self):
        self.style.configure('.', font=('Orbitron', 14))
        self.style.configure('Header.TLabel', font=('Orbitron', 28, 'bold'), background=TERRAN_ACCENT, foreground=TERRAN_TEXT)
        self.style.configure('TButton', font=('Orbitron', 14))
        self.style.configure('Treeview.Heading', font=('Orbitron', 16, 'bold'))
        self.style.configure('Treeview', font=('Orbitron', 14), rowheight=35)
        self.style.configure('TEntry', font=('Orbitron', 14))

    def apply_bg_recursive(self, widget, bg):
        try:
            widget.configure(bg=bg)
        except:
            pass
        for child in widget.winfo_children():
            self.apply_bg_recursive(child, bg)

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.terran_style = False
            self.root.configure(bg="white")
            self.style.theme_use('flatly')
            self.apply_bg_recursive(self.root, "white")
            self.theme_btn.config(text="🌙")
        else:
            self.current_theme = "dark"
            self.terran_style = True
            self.root.configure(bg=TERRAN_BG)
            self.style.theme_use('cyborg')
            self.apply_bg_recursive(self.root, TERRAN_BG)
            self.theme_btn.config(text="☀️")

        self._configure_styles()

    def _configure_styles(self):
        self.style.configure('.', font=('Orbitron', 14))
        self.style.configure('TButton', font=('Orbitron', 14))
        self.style.configure('Treeview.Heading', font=('Orbitron', 16, 'bold'))
        self.style.configure('Treeview', font=('Orbitron', 14), rowheight=35)
        self.style.configure('TEntry', font=('Orbitron', 14))

        if self.current_theme == "dark":
            self.style.configure('Header.TLabel',
                                 font=('Orbitron', 28, 'bold'),
                                 background=TERRAN_ACCENT,
                                 foreground=TERRAN_TEXT2)

            self.style.configure('TLabel',
                                 background=TERRAN_BG,
                                 foreground=TERRAN_TEXT2)

            self.style.configure('TLabelframe',
                                 background=TERRAN_BG,
                                 foreground=TERRAN_TEXT2,
                                 bordercolor=TERRAN_HIGHLIGHT)

            self.style.configure('TLabelframe.Label',
                                 background=TERRAN_BG,
                                 foreground=TERRAN_TEXT2)

        else:  # светла тема
            self.style.configure('Header.TLabel',
                                 font=('Orbitron', 28, 'bold'),
                                 background="#f0f0f0",
                                 foreground="#222")

            self.style.configure('TLabel',
                                 background="white",
                                 foreground="#222")

            self.style.configure('TLabelframe',
                                 background="white",
                                 foreground="#222",
                                 bordercolor="gray")

            self.style.configure('TLabelframe.Label',
                                 background="white",
                                 foreground="#222")

    def create_widgets(self):
        self.header = ttk.Label(
            self.root,
            text="🔧 VEHICLE WORKSHOP ⚙️",
            style='Header.TLabel'
        )
        self.header.pack(pady=(30, 10), fill='x')
        self.theme_btn = ttk.Button(
            self.root,
            text="🌙",  # или "Toggle Theme"
            command=self.toggle_theme
        )
        self.theme_btn.pack(pady=(0, 10))

        if self.user_role == 'mechanic' and self.mechanic_name:
            ttk.Label(
                self.root,
                text=f"Welcome, {self.mechanic_name}!",
                font=('Orbitron', 18, 'bold'),
                background=TERRAN_BG,
                foreground=TERRAN_HIGHLIGHT
            ).pack(pady=(0, 10))

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

        form_frame = ttk.LabelFrame(tab, text="Add New Customer", padding=20)
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
            ttk.Label(frame, text=label, width=15, background=TERRAN_BG, foreground=TERRAN_TEXT2).pack(side=tk.LEFT, padx=10)
            entry = ttk.Entry(frame, width=30)
            entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=10)
            self.customer_entries[key] = entry

        ttk.Button(form_frame, text="Add Customer", command=self.add_customer).pack(pady=20)

    # ================== REPAIRS TAB ==================
    def _create_repairs_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Repairs")

        self.repairs_tree = ttk.Treeview(tab, columns=(
            'Vehicle', 'Status', 'Start Date', 'Issue', 'Mechanic', 'Priority', 'Hours'
        ), show='headings')

        columns = [
            ('Vehicle', 'Vehicle', 300),
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
        ttk.Button(btn_frame, text="Add Schedule", command=self.open_add_schedule_dialog).pack(side=tk.LEFT, padx=5)

    def open_add_schedule_dialog(self):
        self.add_schedule(mechanic=self.selected_mechanic.get())

    def add_schedule(self, mechanic, tab=None):
        win = tk.Toplevel(self.root)
        win.title("Add Schedule")
        if self.terran_style:
            win.configure(bg=TERRAN_BG)
        else:
            win.configure(bg="white")

        tk.Label(win, text="Task:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        task_entry = tk.Entry(win)
        task_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(win, text="Start (YYYY-MM-DD HH:MM):").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        start_entry = tk.Entry(win)
        start_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(win, text="End (YYYY-MM-DD HH:MM):").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        end_entry = tk.Entry(win)
        end_entry.grid(row=2, column=1, padx=10, pady=5)

        def save():
            task = task_entry.get().strip()
            start = start_entry.get().strip()
            end = end_entry.get().strip()
            if not (task and start and end):
                tk.messagebox.showerror("Error", "All fields are required.")
                return
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    '''INSERT INTO schedules (mechanic, start_time, end_time, task, status)
                       VALUES (?, ?, ?, ?, ?)''',
                    (mechanic, start, end, task, 'pending')
                )
                self.conn.commit()
                if tab:
                    self.update_monthly_calendar_display(tab=tab)
                else:
                    self.update_monthly_calendar_display()
                win.destroy()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to add schedule: {e}")

        tk.Button(win, text="Save", command=save).grid(row=3, columnspan=2, pady=10)

    def _create_my_schedule_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="My Schedule")

        nav_frame = ttk.Frame(tab)
        nav_frame.pack(anchor='center', pady=(10,5))
        ttk.Button(nav_frame, text="<<", command=lambda: self.change_month(-1, tab)).pack(side=tk.LEFT, padx=5)
        self.my_month_label = ttk.Label(nav_frame, text="")
        self.my_month_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text=">>", command=lambda: self.change_month(1, tab)).pack(side=tk.LEFT, padx=5)

        self.my_calendar_frame = ttk.Frame(tab)
        self.my_calendar_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        self.update_monthly_calendar_display(tab=tab)

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Schedule", command=lambda: self.add_schedule(mechanic=self.mechanic_name, tab=tab)).pack(side=tk.LEFT, padx=5)

    def change_month(self, delta, tab=None):
        if tab and hasattr(self, 'my_month_label'):
            self.cal_month += delta
            if self.cal_month < 1:
                self.cal_month = 12
                self.cal_year -= 1
            elif self.cal_month > 12:
                self.cal_month = 1
                self.cal_year += 1
            self.update_monthly_calendar_display(tab=tab)
        else:
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
        from datetime import datetime
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
            mechanic = self.selected_mechanic.get() if hasattr(self,
                                                               'selected_mechanic') and self.selected_mechanic.get() else None
            if not mechanic:
                return

        # Draw day headers
        for col, day in enumerate(days):
            tk.Label(cal_frame, text=day, anchor='center', width=18, font=('Orbitron', 12, 'bold'),
                     bg=TERRAN_ACCENT, fg=TERRAN_HIGHLIGHT, bd=0).grid(row=0, column=col, padx=2, pady=2)

        cursor = self.conn.cursor()
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-31"
        # Fetch schedules
        cursor.execute('''SELECT id, mechanic, start_time, end_time, task, status FROM schedules
                           WHERE mechanic=? AND date(start_time) BETWEEN ? AND ?''', (mechanic, start_date, end_date))
        schedules = cursor.fetchall()
        # Fetch ALL repairs (services) for this mechanic and month, regardless of status
        cursor.execute('''SELECT id, assigned_mechanic, start_date, end_date, issue, status FROM repairs
                          WHERE assigned_mechanic=? AND date(start_date) BETWEEN ? AND ?''',
                       (mechanic, start_date, end_date))
        repairs = cursor.fetchall()

        sched_map = {}
        now = datetime.now()
        # Add schedules
        for sid, mech, st, et, task, status in schedules:
            try:
                day = datetime.strptime(st, "%Y-%m-%d %H:%M").day
            except Exception:
                continue
            sched_map.setdefault(day, []).append(('schedule', sid, st, et, task, status))
        # Add repairs (services)
        for rid, mech, st, et, issue, status in repairs:
            try:
                # Try several formats for start_date
                if 'T' in st:
                    day = datetime.strptime(st, "%Y-%m-%dT%H:%M:%S.%f").day
                elif len(st) > 10:
                    day = datetime.strptime(st, "%Y-%m-%d %H:%M:%S").day
                else:
                    day = datetime.strptime(st, "%Y-%m-%d").day
            except Exception:
                continue
            sched_map.setdefault(day, []).append(('repair', rid, st, et, issue, status))

        today = now.day if now.year == year and now.month == month else None
        for row, week in enumerate(month_days, start=1):
            for col, day in enumerate(week):
                cell_bg = CALENDAR_CELL_GRAY
                bordercolor = TERRAN_ACCENT
                if day == today:
                    cell_bg = CALENDAR_CELL_TODAY
                    bordercolor = "#fff"
                cell = tk.Frame(cal_frame, bg=cell_bg, highlightbackground=bordercolor, highlightthickness=2, bd=0)
                cell.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
                cell.grid_propagate(False)
                cell.config(width=140, height=90)
                if day != 0:
                    day_lbl = tk.Label(cell, text=str(day), anchor='ne', font=('Orbitron', 11, 'bold'),
                                       bg=cell_bg, fg="#222")
                    day_lbl.pack(anchor='ne', padx=2, pady=2)
                    if day in sched_map:
                        for entry in sched_map[day]:
                            entry_type, eid, st, et, desc, status = entry
                            late = False
                            try:
                                if et:
                                    end_dt = datetime.strptime(et, "%Y-%m-%d %H:%M")
                                    if end_dt < now:
                                        late = True
                            except Exception:
                                pass
                            # Color code for status
                            if status == 'done' and late:
                                bg = CALENDAR_CELL_DONE
                                fg = '#222'
                            elif status == 'done':
                                bg = "#4CAF50"
                                fg = '#fff'
                            elif late:
                                bg = CALENDAR_CELL_LATE
                                fg = '#222'
                            else:
                                bg = CALENDAR_CELL_TASK if entry_type == 'schedule' else CALENDAR_CELL_SERVICE
                                fg = '#222'
                            label_prefix = "Service:" if entry_type == 'repair' else "Task:"
                            sched_lbl = tk.Label(cell, text=f"{label_prefix} {desc}\n{st[-5:] if len(st) >= 5 else st}",
                                                 font=('Orbitron', 9),
                                                 bg=bg, fg=fg, bd=1, relief="ridge", wraplength=120, justify="center")
                            sched_lbl.pack(fill=tk.X, padx=1, pady=1)
                            # Only show buttons for schedules, not repairs
                            if entry_type == 'schedule':
                                btns = tk.Frame(cell, bg=cell_bg)
                                btns.pack(anchor='w', pady=1)
                                if status != 'done':
                                    tk.Button(btns, text="✓", width=2, font=("Arial", 10, "bold"),
                                              bg="#b0b0b0", fg="#222",
                                              command=lambda s=eid, t=tab: self.mark_schedule_done(s, t)).pack(
                                        side=tk.LEFT, padx=1)
                                else:
                                    tk.Button(btns, text="Done", width=4, state='disabled', bg="#4CAF50",
                                              fg="#fff").pack(side=tk.LEFT, padx=1)
                                tk.Button(btns, text="✎", width=2, bg="#e0e0e0", fg="#222",
                                          command=lambda s=eid, t=tab: self.edit_schedule(s, t)).pack(side=tk.LEFT,
                                                                                                      padx=1)
                                tk.Button(btns, text="🗑", width=2, bg="#e0e0e0", fg="#222",
                                          command=lambda s=eid, t=tab: self.delete_schedule_by_id(s, t)).pack(
                                    side=tk.LEFT, padx=1)
                else:
                    tk.Label(cell, text="", width=12, bg=cell_bg).pack()

        for i in range(7):
            cal_frame.grid_columnconfigure(i, weight=1)
        for i in range(len(month_days) + 1):
            cal_frame.grid_rowconfigure(i, weight=1)

    def mark_schedule_done(self, schedule_id, tab=None):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE schedules SET status=? WHERE id=?', ('done', schedule_id))
        self.conn.commit()
        if tab:
            self.update_monthly_calendar_display(tab=tab)
        else:
            self.update_monthly_calendar_display()

    # ================== MECHANICS MANAGEMENT ==================
    def _create_mechanics_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Mechanics")

        self.mechanics_tree = ttk.Treeview(tab, columns=('Full Name', 'Username', 'Role'), show='headings')
        self.mechanics_tree.heading('Full Name', text='Full Name')
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

        self.inventory_tree = ttk.Treeview(
            tab,
            columns=('Part Name', 'Quantity', 'Price', 'Supplier', 'Last Ordered'),
            show='headings'
        )
        self.inventory_tree.heading('Part Name', text='Part Name')
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

    def update_inventory_display(self):
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        cur = self.conn.cursor()
        for part, qty, price, supplier, lo in cur.execute(
                'SELECT part_name, quantity, price, supplier, last_ordered FROM inventory'):
            self.inventory_tree.insert('', 'end', values=(part, qty, price, supplier, lo or 'Never'))

    def add_part_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add New Part")
        if self.terran_style:
            win.configure(bg=TERRAN_BG)
        else:
            win.configure(bg="white")

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
            self.repairs_tree.insert('', 'end', values=row)

    def update_mechanics_display(self):
        self.mechanics_tree.delete(*self.mechanics_tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute('SELECT full_name, username, role FROM users WHERE role="mechanic"')
        for row in cursor.fetchall():
            self.mechanics_tree.insert('', 'end', values=(row[0], row[1], row[2]))

    def add_mechanic(self):
        win = tk.Toplevel(self.root)
        win.title("Add Mechanic")
        if self.terran_style:
            win.configure(bg=TERRAN_BG)
        else:
            win.configure(bg="white")

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
            username = item['values'][1]  # Username is the second column
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM users WHERE username=?', (username,))
            self.conn.commit()
            self.update_mechanics_display()

    def show_repair_details(self, event=None):
        sel = self.repairs_tree.selection()
        if not sel: return
        vehicle = self.repairs_tree.item(sel[0])['values'][0]
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM repairs WHERE vehicle=?', (vehicle,))
        r = cur.fetchone()
        win = tk.Toplevel(self.root)
        win.title("Repair Details")
        if self.terran_style:
            win.configure(bg=TERRAN_BG)
        else:
            win.configure(bg="white")
        # Corrected indices based on your schema:
        # 0: id, 1: vehicle, 2: customer_name, 3: car_model, 4: vin, 5: issue, 6: status,
        # 7: start_date, 8: assigned_mechanic, 9: priority, 10: estimated_hours, 11: estimated_cost, 12: end_date
        fields = [
            ("Customer:", r[2]),
            ("Vehicle:", r[1]),
            ("Car Model:", r[3]),
            ("VIN:", r[4]),
            ("Issue:", r[5]),
            ("Assigned Mechanic:", r[8]),
            ("Priority:", r[9]),
            ("Estimated Hours:", r[10]),
            ("Estimated Cost:", r[11]),
            ("Start Date:", r[7]),
            ("End Date:", r[12] or "Ongoing"),
            ("Status:", r[6])
        ]
        for i, (lbl, val) in enumerate(fields):
            ttk.Label(win, text=lbl).grid(row=i, column=0, sticky='e', padx=5, pady=2)
            ttk.Label(win, text=val).grid(row=i, column=1, sticky='w', padx=5, pady=2)

    def edit_repair(self):
        sel = self.repairs_tree.selection()
        if not sel: return
        vehicle = self.repairs_tree.item(sel[0])['values'][0]
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM repairs WHERE vehicle=?', (vehicle,))
        rd = cur.fetchone()
        win = tk.Toplevel(self.root)
        win.title("Edit Repair Details")
        if self.terran_style:
            win.configure(bg=TERRAN_BG)
        else:
            win.configure(bg="white")
        # Corrected indices based on your schema:
        # 8: assigned_mechanic, 9: priority, 10: estimated_hours
        fields = [
            ('Assigned Mechanic:', 'assigned_mechanic', 'entry', rd[8]),
            ('Priority:', 'priority', 'combo', ['Low', 'Medium', 'High'], rd[9]),
            ('Estimated Hours:', 'hours', 'entry', rd[10])
        ]
        entries = {}
        for i, (lbl, key, t, *rest) in enumerate(fields):
            ttk.Label(win, text=lbl).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            if t == 'entry':
                e = ttk.Entry(win)
                e.insert(0, rest[0])
                e.grid(row=i, column=1, padx=10, pady=5)
                entries[key] = e
            else:
                c = ttk.Combobox(win, values=rest[0])
                c.set(rest[1])
                c.grid(row=i, column=1, padx=10, pady=5)
                entries[key] = c

        def save():
            # Validate hours as a float
            try:
                hours_val = float(entries['hours'].get())
            except ValueError:
                messagebox.showerror("Error", "Estimated Hours must be a number.")
                return
            cur.execute('''UPDATE repairs SET
                            assigned_mechanic=?, priority=?, estimated_hours=?
                            WHERE vehicle=?''', (
                entries['assigned_mechanic'].get(),
                entries['priority'].get(),
                hours_val,
                vehicle
            ))
            self.conn.commit()
            self.update_repairs_display()
            win.destroy()

        ttk.Button(win, text="Save Changes", command=save).grid(row=len(fields), columnspan=2, pady=10)

        def save():
            # Validate hours as a float
            try:
                hours_val = float(entries['hours'].get())
            except ValueError:
                messagebox.showerror("Error", "Estimated Hours must be a number.")
                return
            cur.execute('''UPDATE repairs SET
                           assigned_mechanic=?, priority=?, estimated_hours=?
                           WHERE vehicle=?''', (
                entries['assigned_mechanic'].get(),
                entries['priority'].get(),
                hours_val,
                vehicle
            ))
            self.conn.commit()
            self.update_repairs_display()
            win.destroy()

        ttk.Button(win, text="Save Changes", command=save).grid(row=len(fields), columnspan=2, pady=10)

    def add_repair_notes(self):
        sel = self.repairs_tree.selection()
        if not sel: return
        vehicle = self.repairs_tree.item(sel[0])['values'][0]
        cur = self.conn.cursor()
        cur.execute('SELECT issue FROM repairs WHERE vehicle=?', (vehicle,))
        text = cur.fetchone()[0]
        win = tk.Toplevel(self.root);
        win.title("Repair Notes")
        if self.terran_style:
            win.configure(bg=TERRAN_BG)
        else:
            win.configure(bg="white")
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

    def mark_repaired(self):
        sel = self.repairs_tree.selection()
        if sel:
            veh = self.repairs_tree.item(sel[0])['values'][0]
            cur = self.conn.cursor()
            cur.execute('UPDATE repairs SET status=?, end_date=? WHERE vehicle=?',
                        ('Repaired', datetime.datetime.now().isoformat(), veh))
            self.conn.commit()
            self.update_repairs_display()

    def mark_pending(self):
        sel = self.repairs_tree.selection()
        if sel:
            veh = self.repairs_tree.item(sel[0])['values'][0]
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
