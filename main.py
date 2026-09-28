import os
import sqlite3
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ===================== SETTINGS =====================

BG = "#08111F"
NAV = "#0B1728"
CARD = "#101C2D"
FORM = "#F7F3EA"
WHITE = "#FFFFFF"
DARK = "#162033"
GREY = "#9AA8BA"
ORANGE = "#F59E0B"

CATEGORIES = [
    "Electrical", "Furniture", "Plumbing", "IT",
    "Internet", "Cleaning", "AC/Cooling", "Other"
]

PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Pending", "In Progress", "Resolved"]

BASE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(BASE, "data"), exist_ok=True)
DB = os.path.join(BASE, "data", "campus.db")


# ===================== DATABASE =====================

def con():
    return sqlite3.connect(DB)


def setup():
    c = con()

    c.execute("""
    CREATE TABLE IF NOT EXISTS complaints(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT UNIQUE,
        student_name TEXT NOT NULL,
        department TEXT,
        building TEXT,
        room_no TEXT,
        category TEXT,
        problem TEXT NOT NULL,
        priority TEXT,
        status TEXT,
        date TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS maintenance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT,
        staff_name TEXT,
        repair_date TEXT,
        cost REAL,
        remarks TEXT
    )
    """)

    c.commit()
    c.close()


def new_id():
    c = con()
    r = c.execute(
        "SELECT id FROM complaints ORDER BY id DESC LIMIT 1"
    ).fetchone()
    c.close()
    return f"CMP{(r[0] + 1) if r else 1:03d}"


def complaints():
    c = con()
    d = pd.read_sql_query(
        "SELECT * FROM complaints ORDER BY id DESC", c
    )
    c.close()
    return d


def maintenance():
    c = con()
    d = pd.read_sql_query(
        "SELECT * FROM maintenance", c
    )
    c.close()
    return d


def find(cid):
    c = con()
    r = c.execute("""
        SELECT complaint_id,student_name,department,building,
        room_no,category,problem,priority,status,date
        FROM complaints
        WHERE UPPER(complaint_id)=UPPER(?)
    """, (cid.strip(),)).fetchone()
    c.close()
    return r


# ===================== APPLICATION =====================

class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("CampusFix - Campus Maintenance System")
        self.geometry("1280x800")
        self.minsize(1050, 700)
        self.configure(bg=BG)

        setup()
        self.nav()
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill="both", expand=True)

        self.dashboard()

    # ================= COMMON =================

    def clear(self):
        for w in self.body.winfo_children():
            w.destroy()

    def button(self, p, text, command, orange=False):
        return tk.Button(
            p,
            text=text,
            command=command,
            bg=ORANGE if orange else CARD,
            fg=DARK if orange else WHITE,
            activebackground="#D97706" if orange else "#1E3048",
            activeforeground=DARK if orange else WHITE,
            relief="flat",
            bd=0,
            padx=16,
            pady=10,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        )

    def nav(self):
        n = tk.Frame(self, bg=NAV, height=72)
        n.pack(fill="x")
        n.pack_propagate(False)

        tk.Label(
            n,
            text="CampusFix",
            bg=NAV,
            fg=WHITE,
            font=("Segoe UI", 20, "bold")
        ).pack(side="left", padx=30)

        for text, command in [
            ("Dashboard", self.dashboard),
            ("Register", self.register),
            ("All Tickets", self.tickets),
            ("Reports", self.reports)
        ]:
            tk.Button(
                n,
                text=text,
                command=command,
                bg=NAV,
                fg="#D5DEE9",
                activebackground="#17263B",
                activeforeground=WHITE,
                relief="flat",
                bd=0,
                padx=15,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2"
            ).pack(side="left", pady=15)

        self.button(
            n,
            "+ Report an Issue",
            self.register,
            True
        ).pack(side="right", padx=25, pady=15)

    def heading(self, title, subtitle):
        tk.Label(
            self.body,
            text=title,
            bg=BG,
            fg=WHITE,
            font=("Segoe UI", 28, "bold")
        ).pack(anchor="w", padx=45, pady=(30, 2))

        tk.Label(
            self.body,
            text=subtitle,
            bg=BG,
            fg=GREY,
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=45, pady=(0, 20))

    def metric(self, p, title, value):
        f = tk.Frame(p, bg=CARD, height=100)
        f.pack(side="left", fill="both", expand=True, padx=4)
        f.pack_propagate(False)

        tk.Label(
            f,
            text=title,
            bg=CARD,
            fg=GREY,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=14, pady=(16, 3))

        tk.Label(
            f,
            text=str(value),
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=14)

    # ================= DASHBOARD =================

    def dashboard(self):
        self.clear()

        tk.Label(
            self.body,
            text="CAMPUS MAINTENANCE",
            bg=BG,
            fg=ORANGE,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=45, pady=(35, 2))

        tk.Label(
            self.body,
            text="Complaint & Tracking System",
            bg=BG,
            fg=WHITE,
            font=("Segoe UI", 30, "bold")
        ).pack(anchor="w", padx=45)

        tk.Label(
            self.body,
            text="Report campus maintenance issues, track their status and analyze repair activity.",
            bg=BG,
            fg=GREY,
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=45, pady=5)

        d = complaints()

        cards = tk.Frame(self.body, bg=BG)
        cards.pack(fill="x", padx=40, pady=35)

        self.metric(cards, "TOTAL COMPLAINTS", len(d))
        self.metric(cards, "PENDING",
                    (d.status == "Pending").sum() if len(d) else 0)
        self.metric(cards, "IN PROGRESS",
                    (d.status == "In Progress").sum() if len(d) else 0)
        self.metric(cards, "RESOLVED",
                    (d.status == "Resolved").sum() if len(d) else 0)

        w = tk.Frame(self.body, bg=CARD)
        w.pack(fill="x", padx=45)

        tk.Label(
            w,
            text="SYSTEM WORKFLOW",
            bg=CARD,
            fg=ORANGE,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=25, pady=(20, 7))

        tk.Label(
            w,
            text="Enter Complaint  →  Save  →  View / Search  →  Update Status  →  Add Repair Details  →  Analyze Data",
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=25, pady=(0, 22))

        a = tk.Frame(self.body, bg=BG)
        a.pack(anchor="w", padx=45, pady=18)

        self.button(
            a, "Register New Complaint",
            self.register, True
        ).pack(side="left", padx=(0, 10))

        self.button(
            a, "View All Tickets",
            self.tickets
        ).pack(side="left")

    # ================= REGISTER =================

    def register(self):
        self.clear()
        self.heading(
            "REGISTER A COMPLAINT",
            "Create a new campus maintenance ticket"
        )

        card = tk.Frame(self.body, bg=FORM)
        card.pack(fill="both", expand=True, padx=50, pady=(0, 30))

        tk.Label(
            card,
            text="NEW TICKET",
            bg=FORM,
            fg=ORANGE,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=30, pady=(25, 10))

        form = tk.Frame(card, bg=FORM)
        form.pack(fill="x", padx=30)

        self.v = {
            "student": tk.StringVar(),
            "department": tk.StringVar(),
            "building": tk.StringVar(),
            "room": tk.StringVar(),
            "category": tk.StringVar(value=CATEGORIES[0]),
            "priority": tk.StringVar(value="Medium")
        }

        fields = [
            ("Student Name", "student", 0, 0),
            ("Department", "department", 0, 1),
            ("Building", "building", 1, 0),
            ("Room No.", "room", 1, 1)
        ]

        for title, key, row, col in fields:
            self.entry(form, title, self.v[key], row, col)

        self.combo(
            form, "Category",
            self.v["category"], CATEGORIES, 2, 0
        )

        self.combo(
            form, "Priority",
            self.v["priority"], PRIORITIES, 2, 1
        )

        tk.Label(
            card,
            text="Problem Description",
            bg=FORM,
            fg=DARK,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=30, pady=(15, 5))

        self.problem = tk.Text(
            card,
            height=6,
            bg="white",
            fg=DARK,
            relief="solid",
            bd=1,
            font=("Segoe UI", 10)
        )
        self.problem.pack(fill="x", padx=30)

        bottom = tk.Frame(card, bg=FORM)
        bottom.pack(fill="x", padx=30, pady=20)

        tk.Label(
            bottom,
            text=f"Date: {date.today()}   •   Initial Status: Pending",
            bg=FORM,
            fg="#687386"
        ).pack(side="left")

        self.button(
            bottom,
            "SAVE / REGISTER COMPLAINT",
            self.save,
            True
        ).pack(side="right")

    def entry(self, p, title, var, row, col):
        f = tk.Frame(p, bg=FORM)
        f.grid(
            row=row,
            column=col,
            sticky="ew",
            padx=(0 if col == 0 else 12,
                  12 if col == 0 else 0),
            pady=6
        )

        p.grid_columnconfigure(col, weight=1)

        tk.Label(
            f,
            text=title,
            bg=FORM,
            fg=DARK,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 4))

        tk.Entry(
            f,
            textvariable=var,
            bg="white",
            fg=DARK,
            relief="solid",
            bd=1
        ).pack(fill="x", ipady=8)

    def combo(self, p, title, var, values, row, col):
        f = tk.Frame(p, bg=FORM)
        f.grid(
            row=row,
            column=col,
            sticky="ew",
            padx=(0 if col == 0 else 12,
                  12 if col == 0 else 0),
            pady=6
        )

        p.grid_columnconfigure(col, weight=1)

        tk.Label(
            f,
            text=title,
            bg=FORM,
            fg=DARK,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 4))

        ttk.Combobox(
            f,
            textvariable=var,
            values=values,
            state="readonly"
        ).pack(fill="x", ipady=5)

    def save(self):
        student = self.v["student"].get().strip()
        problem = self.problem.get("1.0", "end").strip()

        if not student:
            messagebox.showerror(
                "Validation Error",
                "Student Name is required."
            )
            return

        if not problem:
            messagebox.showerror(
                "Validation Error",
                "Problem Description is required."
            )
            return

        cid = new_id()

        c = con()
        c.execute("""
            INSERT INTO complaints
            (complaint_id,student_name,department,building,room_no,
             category,problem,priority,status,date)
            VALUES(?,?,?,?,?,?,?,?,?,?)
        """, (
            cid,
            student,
            self.v["department"].get().strip(),
            self.v["building"].get().strip(),
            self.v["room"].get().strip(),
            self.v["category"].get(),
            problem,
            self.v["priority"].get(),
            "Pending",
            str(date.today())
        ))

        c.commit()
        c.close()

        messagebox.showinfo(
            "Complaint Registered",
            f"Complaint registered successfully.\n\n"
            f"Complaint ID: {cid}\n"
            f"Status: Pending"
        )

        self.tickets()

    # ================= TICKETS =================

    def tickets(self):
        self.clear()

        self.heading(
            "ALL TICKETS",
            "View and manage campus maintenance complaints"
        )

        top = tk.Frame(self.body, bg=BG)
        top.pack(fill="x", padx=40)

        self.search_var = tk.StringVar()

        tk.Entry(
            top,
            textvariable=self.search_var,
            bg="#142238",
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            width=25
        ).pack(side="left", ipady=9, padx=5)

        self.button(
            top, "Search ID",
            self.search
        ).pack(side="left", padx=5)

        self.button(
            top, "Update Status",
            self.status_window,
            True
        ).pack(side="left", padx=5)

        self.button(
            top, "Add Maintenance",
            self.maintenance_window
        ).pack(side="left", padx=5)

        frame = tk.Frame(self.body, bg=CARD)
        frame.pack(fill="both", expand=True, padx=40, pady=20)

        cols = (
            "ID", "Student", "Category",
            "Building", "Priority", "Status", "Date"
        )

        self.tree = ttk.Treeview(
            frame,
            columns=cols,
            show="headings"
        )

        for col, width in zip(
            cols,
            [100, 180, 130, 130, 100, 130, 120]
        ):
            self.tree.heading(col, text=col)
            self.tree.column(
                col,
                width=width,
                anchor="center"
            )

        scroll = ttk.Scrollbar(
            frame,
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scroll.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0),
            pady=10
        )

        scroll.pack(
            side="right",
            fill="y",
            padx=(0, 10),
            pady=10
        )

        for r in complaints().itertuples():
            self.tree.insert(
                "",
                "end",
                values=(
                    r.complaint_id,
                    r.student_name,
                    r.category,
                    r.building,
                    r.priority,
                    r.status,
                    r.date
                )
            )

    # ================= SEARCH =================

    def search(self):
        cid = self.search_var.get().strip()

        if not cid:
            messagebox.showerror(
                "Search",
                "Enter a Complaint ID such as CMP001."
            )
            return

        r = find(cid)

        if not r:
            messagebox.showerror(
                "Complaint Not Found",
                f"No complaint was found for ID: {cid}"
            )
            return

        w = tk.Toplevel(self)
        w.title(f"Complaint {r[0]}")
        w.geometry("620x570")
        w.configure(bg=FORM)

        tk.Label(
            w,
            text=f"COMPLAINT {r[0]}",
            bg=FORM,
            fg=DARK,
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", padx=30, pady=25)

        for title, value in [
            ("Student Name", r[1]),
            ("Department", r[2]),
            ("Building", r[3]),
            ("Room No.", r[4]),
            ("Category", r[5]),
            ("Priority", r[7]),
            ("Status", r[8]),
            ("Date", r[9])
        ]:
            tk.Label(
                w,
                text=f"{title}: {value or '-'}",
                bg=FORM,
                fg=DARK
            ).pack(anchor="w", padx=30, pady=3)

        tk.Label(
            w,
            text="Problem Description",
            bg=FORM,
            fg=DARK,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=30, pady=(15, 4))

        t = tk.Text(w, height=6, bg="white", fg=DARK)
        t.pack(fill="x", padx=30)
        t.insert("1.0", r[6])
        t.configure(state="disabled")

        self.button(
            w, "Close", w.destroy
        ).pack(anchor="e", padx=30, pady=20)

    # ================= STATUS =================

    def status_window(self):
        w = tk.Toplevel(self)
        w.title("Update Complaint Status")
        w.geometry("480x360")
        w.configure(bg=FORM)

        tk.Label(
            w,
            text="UPDATE STATUS",
            bg=FORM,
            fg=DARK,
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", padx=30, pady=25)

        cid = tk.StringVar()
        status = tk.StringVar(value="Pending")

        tk.Label(
            w,
            text="Complaint ID",
            bg=FORM,
            fg=DARK
        ).pack(anchor="w", padx=30)

        tk.Entry(
            w,
            textvariable=cid
        ).pack(fill="x", padx=30, pady=5, ipady=8)

        current = tk.Label(
            w,
            text="Current Status: -",
            bg=FORM,
            fg="#667085"
        )

        current.pack(anchor="w", padx=30, pady=8)

        ttk.Combobox(
            w,
            textvariable=status,
            values=STATUSES,
            state="readonly"
        ).pack(fill="x", padx=30, ipady=5)

        def check():
            r = find(cid.get())

            if not r:
                current.config(
                    text="Current Status: Complaint Not Found"
                )
                return

            current.config(
                text=f"Current Status: {r[8]}"
            )

            status.set(r[8])

        def save():
            if not find(cid.get()):
                messagebox.showerror(
                    "Complaint Not Found",
                    "Complaint ID not found.",
                    parent=w
                )
                return

            c = con()
            c.execute(
                "UPDATE complaints SET status=? WHERE complaint_id=?",
                (status.get(), cid.get().upper())
            )
            c.commit()
            c.close()

            messagebox.showinfo(
                "Status Updated",
                f"{cid.get().upper()} status changed to {status.get()}.",
                parent=w
            )

            w.destroy()
            self.tickets()

        self.button(
            w, "Check Complaint", check
        ).pack(side="left", padx=30, pady=20)

        self.button(
            w, "SAVE STATUS", save, True
        ).pack(side="right", padx=30, pady=20)

    # ================= MAINTENANCE =================

    def maintenance_window(self):
        w = tk.Toplevel(self)
        w.title("Add Repair Details")
        w.geometry("560x600")
        w.configure(bg=FORM)

        tk.Label(
            w,
            text="ADD REPAIR DETAILS",
            bg=FORM,
            fg=DARK,
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", padx=30, pady=25)

        cid = tk.StringVar()
        staff = tk.StringVar()
        repair_date = tk.StringVar(value=str(date.today()))
        cost = tk.StringVar()

        for title, var in [
            ("Complaint ID", cid),
            ("Staff Name", staff),
            ("Repair Date", repair_date),
            ("Repair Cost", cost)
        ]:
            tk.Label(
                w,
                text=title,
                bg=FORM,
                fg=DARK,
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w", padx=30, pady=(4, 3))

            tk.Entry(
                w,
                textvariable=var,
                bg="white",
                fg=DARK
            ).pack(fill="x", padx=30, ipady=8, pady=(0, 8))

        tk.Label(
            w,
            text="Remarks",
            bg=FORM,
            fg=DARK,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=30, pady=(8, 4))

        remarks = tk.Text(w, height=6, bg="white", fg=DARK)
        remarks.pack(fill="x", padx=30)

        def save():
            if not find(cid.get()):
                messagebox.showerror(
                    "Complaint Not Found",
                    "Complaint ID not found.",
                    parent=w
                )
                return

            if not staff.get().strip():
                messagebox.showerror(
                    "Validation Error",
                    "Staff Name is required.",
                    parent=w
                )
                return

            try:
                amount = float(cost.get())

                if amount < 0:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Validation Error",
                    "Repair Cost must be a valid non-negative number.",
                    parent=w
                )
                return

            c = con()

            c.execute("""
                INSERT INTO maintenance
                (complaint_id,staff_name,repair_date,cost,remarks)
                VALUES(?,?,?,?,?)
            """, (
                cid.get().upper(),
                staff.get().strip(),
                repair_date.get().strip(),
                amount,
                remarks.get("1.0", "end").strip()
            ))

            c.commit()
            c.close()

            messagebox.showinfo(
                "Maintenance Saved",
                f"Repair details saved for {cid.get().upper()}.",
                parent=w
            )

            w.destroy()

        self.button(
            w,
            "SAVE REPAIR DETAILS",
            save,
            True
        ).pack(anchor="e", padx=30, pady=25)

    # ================= REPORTS =================

    def reports(self):
        self.clear()

        self.heading(
            "REPORTS & ANALYTICS",
            "Pandas analysis and Matplotlib visualizations of maintenance data"
        )

        d = complaints()
        m = maintenance()

        pending = (
            (d.status == "Pending").sum()
            if len(d) else 0
        )

        progress = (
            (d.status == "In Progress").sum()
            if len(d) else 0
        )

        resolved = (
            (d.status == "Resolved").sum()
            if len(d) else 0
        )

        if len(m):
            costs = pd.to_numeric(
                m["cost"],
                errors="coerce"
            ).fillna(0)

            total_cost = costs.sum()
            average_cost = costs.mean()

        else:
            total_cost = 0
            average_cost = 0

        if len(d):
            common_category = (
                d["category"]
                .fillna("Other")
                .replace("", "Other")
                .value_counts()
                .idxmax()
            )

            buildings = (
                d["building"]
                .replace("", pd.NA)
                .dropna()
            )

            top_building = (
                buildings.value_counts().idxmax()
                if len(buildings) else "-"
            )

        else:
            common_category = "-"
            top_building = "-"

        cards = tk.Frame(self.body, bg=BG)
        cards.pack(fill="x", padx=25)

        values = [
            ("TOTAL COMPLAINTS", len(d)),
            ("PENDING", pending),
            ("IN PROGRESS", progress),
            ("RESOLVED", resolved),
            ("TOTAL MAINT. COST", f"₹{total_cost:,.2f}"),
            ("AVERAGE REPAIR COST", f"₹{average_cost:,.2f}"),
            ("MOST COMMON CATEGORY", common_category),
            ("MOST REPORTED BUILDING", top_building)
        ]

        for title, value in values:
            self.metric(cards, title, value)

        charts = tk.Frame(self.body, bg=BG)
        charts.pack(fill="both", expand=True, padx=30, pady=15)

        self.chart(
            charts, d,
            "Complaints by Category",
            0, 0,
            "bar"
        )

        self.chart(
            charts, d,
            "Complaints by Status",
            0, 1,
            "pie"
        )

        self.chart(
            charts, d,
            "Complaints by Building",
            1, 0,
            "building"
        )

        self.chart(
            charts, d,
            "Monthly Complaints",
            1, 1,
            "month"
        )

        self.cost_chart(
            charts, d, m
        )

    # ================= CHARTS =================

    def chart_frame(self, parent, title, row, col, span=1):
        f = tk.Frame(parent, bg=CARD)

        f.grid(
            row=row,
            column=col,
            columnspan=span,
            sticky="nsew",
            padx=6,
            pady=6
        )

        parent.grid_columnconfigure(
            0, weight=1
        )

        parent.grid_columnconfigure(
            1, weight=1
        )

        parent.grid_rowconfigure(
            row, weight=1
        )

        tk.Label(
            f,
            text=title,
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=12, pady=8)

        return f

    def show_fig(self, frame, fig):
        fig.patch.set_facecolor(CARD)

        canvas = FigureCanvasTkAgg(
            fig,
            master=frame
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    def chart(
        self,
        parent,
        d,
        title,
        row,
        col,
        kind
    ):

        f = self.chart_frame(
            parent,
            title,
            row,
            col
        )

        fig = plt.Figure(
            figsize=(5, 2.4),
            dpi=85
        )

        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD)

        if kind == "bar":

            if len(d):
                x = (
                    d["category"]
                    .fillna("Other")
                    .replace("", "Other")
                    .value_counts()
                )

                ax.bar(
                    x.index.astype(str),
                    x.values
                )

                ax.tick_params(
                    axis="x",
                    rotation=35,
                    labelsize=7,
                    colors="white"
                )

                ax.tick_params(
                    axis="y",
                    colors="white"
                )

            else:
                self.no_data(ax)

        elif kind == "pie":

            x = (
                d["status"]
                .value_counts()
                .reindex(STATUSES, fill_value=0)
                if len(d)
                else pd.Series([0, 0, 0], index=STATUSES)
            )

            if x.sum():
                ax.pie(
                    x.values,
                    labels=x.index,
                    autopct="%1.0f%%",
                    textprops={"color": "white", "fontsize": 8}
                )
            else:
                self.no_data(ax)

        elif kind == "building":

            x = (
                d["building"]
                .replace("", pd.NA)
                .dropna()
                .value_counts()
                if len(d)
                else pd.Series()
            )

            if len(x):
                ax.bar(
                    x.index.astype(str),
                    x.values
                )

                ax.tick_params(
                    axis="x",
                    rotation=35,
                    labelsize=7,
                    colors="white"
                )

                ax.tick_params(
                    axis="y",
                    colors="white"
                )

            else:
                self.no_data(ax)

        elif kind == "month":

            if len(d):

                dt = pd.to_datetime(
                    d["date"],
                    errors="coerce"
                ).dropna()

                if len(dt):

                    x = (
                        dt.dt.to_period("M")
                        .astype(str)
                        .value_counts()
                        .sort_index()
                    )

                    ax.plot(
                        x.index,
                        x.values,
                        marker="o",
                        linewidth=2
                    )

                    ax.tick_params(
                        axis="x",
                        rotation=35,
                        labelsize=7,
                        colors="white"
                    )

                    ax.tick_params(
                        axis="y",
                        colors="white"
                    )

                else:
                    self.no_data(ax)

            else:
                self.no_data(ax)

        for s in ax.spines.values():
            s.set_visible(False)

        fig.tight_layout()
        self.show_fig(f, fig)

    def cost_chart(self, parent, d, m):

        f = self.chart_frame(
            parent,
            "Repair Cost by Category",
            2,
            0,
            2
        )

        fig = plt.Figure(
            figsize=(10, 2.4),
            dpi=85
        )

        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD)

        if len(d) and len(m):

            merged = m.merge(
                d[["complaint_id", "category"]],
                on="complaint_id",
                how="left"
            )

            merged["cost"] = pd.to_numeric(
                merged["cost"],
                errors="coerce"
            ).fillna(0)

            x = merged.groupby(
                merged["category"].fillna("Other")
            )["cost"].sum()

            if len(x):

                ax.bar(
                    x.index.astype(str),
                    x.values
                )

                ax.tick_params(
                    axis="x",
                    rotation=35,
                    labelsize=7,
                    colors="white"
                )

                ax.tick_params(
                    axis="y",
                    colors="white"
                )

            else:
                self.no_data(ax)

        else:
            self.no_data(ax)

        for s in ax.spines.values():
            s.set_visible(False)

        fig.tight_layout()
        self.show_fig(f, fig)

    def no_data(self, ax):
        ax.text(
            0.5,
            0.5,
            "No data available",
            ha="center",
            va="center",
            color="white"
        )

        ax.set_xticks([])
        ax.set_yticks([])


# ===================== START =====================

if __name__ == "__main__":
    App().mainloop()