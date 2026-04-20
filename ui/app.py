import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from database.database import WarehouseDB
import datetime

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

BG      = "#0f172a
CARD_BG = "#1e293b"
SIDEBAR = "#111827"
HEADER  = "#1e3a8a"
ORANGE  = "#f97316"
GREEN   = "#14b8a6"
RED     = "#ef4444"
YELLOW  = "#eab308"
BLUE    = "#3b82f6"
PURPLE  = "#8b5cf6"


def _style_tree():
    s = ttk.Style()
    try:
        s.theme_use("clam")
    except Exception:
        pass
    s.configure("W.Treeview", background=CARD_BG, fieldbackground=CARD_BG,
                foreground="white", rowheight=30, font=("Arial", 11))
    s.configure("W.Treeview.Heading", background=HEADER,
                foreground="white", font=("Arial", 11, "bold"))
    s.map("W.Treeview", background=[("selected", BLUE)])


def _tree(parent, columns, widths):
    _style_tree()
    t = ttk.Treeview(parent, columns=columns, show="headings", style="W.Treeview")
    for col, w in zip(columns, widths):
        t.heading(col, text=col)
        t.column(col, width=w)
    t.tag_configure("low",  background="#450a0a", foreground="#fca5a5")
    t.tag_configure("zero", background="#7f1d1d", foreground="white")
    return t


def _lbl(parent, text, size=13, bold=False, color="white", **kw):
    font = ("Arial", size, "bold") if bold else ("Arial", size)
    return ctk.CTkLabel(parent, text=text, font=font, text_color=color, **kw)


def _btn(parent, text, cmd, color=BLUE, hover=None, width=140, **kw):
    return ctk.CTkButton(parent, text=text, command=cmd,
                         fg_color=color, hover_color=hover or color,
                         width=width, **kw)


class WMSApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.geometry("1200x750")
        self.title("Warehouse Management System")
        self.resizable(True, True)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.db           = WarehouseDB()
        self.current_user = None
        self.role         = None
        self.main         = None
        self._tick_id     = None

        self.show_login()

    # ════════════ CLOCK ════════════
    def _do_tick(self):
        try:
            now = datetime.datetime.now().strftime("%d-%m-%Y   %H:%M:%S")
            self.time_lbl.configure(text=f"  {now}  ")
            self._tick_id = self.after(1000, self._do_tick)
        except Exception:
            self._tick_id = None

    def cancel_tick(self):
        if self._tick_id is not None:
            try:
                self.after_cancel(self._tick_id)
            except Exception:
                pass
            self._tick_id = None

    # ════════════ LOGIN ════════════
    def show_login(self):
        self.cancel_tick()
        self.clear_all()
        self.update_idletasks()

        bg = ctk.CTkFrame(self, fg_color=BG)
        bg.place(relx=0, rely=0, relwidth=1, relheight=1)

        card = ctk.CTkFrame(bg, width=420, height=510,
                            fg_color=CARD_BG, corner_radius=16)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        _lbl(card, "Welcome to", 14, color="#94a3b8").pack(pady=(40, 0))
        _lbl(card, "Warehouse Management\nSystem", 22, True,
             color=ORANGE).pack(pady=(4, 4))
        _lbl(card, "Sign in to your account", 12,
             color="#64748b").pack(pady=(0, 24))

        self.u_entry = ctk.CTkEntry(card, placeholder_text="Username",
                                    width=300, height=40)
        self.u_entry.pack(pady=6)
        self.p_entry = ctk.CTkEntry(card, placeholder_text="Password",
                                    show="*", width=300, height=40)
        self.p_entry.pack(pady=6)
        self.p_entry.bind("<Return>", lambda _: self._do_login())

        self.login_err = _lbl(card, "", 11, color=RED)
        self.login_err.pack(pady=(4, 0))

        _btn(card, "Sign In", self._do_login, ORANGE, "#ea580c",
             width=300, height=42, font=("Arial", 14, "bold")).pack(pady=14)

        _lbl(card, "Don't have an account?", 12, color="#64748b").pack()
        ctk.CTkButton(card, text="Sign Up", width=300, height=38,
                      fg_color="transparent", border_width=1,
                      border_color=ORANGE, text_color=ORANGE,
                      hover_color="#1e1e2e",
                      command=self.show_signup).pack(pady=8)

    def _do_login(self):
        u = self.u_entry.get().strip()
        p = self.p_entry.get().strip()
        if not u or not p:
            self.login_err.configure(text="Enter username and password.")
            return
        res = self.db.check_user(u, p)
        if res:
            self.current_user = u
            self.role = res[0]          # res = (role,)
            self.db.log(u, "LOGIN", f"Role: {self.role}")
            self.load_main_ui()
        else:
            self.login_err.configure(text="Invalid username or password.")

    # ════════════ SIGNUP ════════════
    def show_signup(self):
        self.cancel_tick()
        self.clear_all()
        self.update_idletasks()

        bg = ctk.CTkFrame(self, fg_color=BG)
        bg.place(relx=0, rely=0, relwidth=1, relheight=1)

        card = ctk.CTkFrame(bg, width=420, height=460,
                            fg_color=CARD_BG, corner_radius=16)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        _lbl(card, "Create Account", 22, True, color=ORANGE).pack(pady=(40, 4))
        _lbl(card, "Registered as Employee", 12,
             color="#64748b").pack(pady=(0, 24))

        self.su_user = ctk.CTkEntry(card, placeholder_text="Username",
                                    width=300, height=40)
        self.su_user.pack(pady=6)
        self.su_pass = ctk.CTkEntry(card, placeholder_text="Password",
                                    show="*", width=300, height=40)
        self.su_pass.pack(pady=6)

        self.su_err = _lbl(card, "", 11, color=RED)
        self.su_err.pack(pady=(4, 0))

        def register():
            u = self.su_user.get().strip()
            p = self.su_pass.get().strip()
            if not u or not p:
                self.su_err.configure(text="Both fields required."); return
            if self.db.add_user(u, p):
                self.db.log(u, "SIGNUP", "New employee account created")
                messagebox.showinfo("Success", f"Account '{u}' created!")
                self.show_login()
            else:
                self.su_err.configure(text="Username already exists.")

        _btn(card, "Register", register, ORANGE, "#ea580c",
             width=300, height=42, font=("Arial", 14, "bold")).pack(pady=14)
        ctk.CTkButton(card, text="Back to Sign In", width=300, height=38,
                      fg_color="transparent", border_width=1,
                      border_color="#475569", text_color="#94a3b8",
                      hover_color="#1e1e2e",
                      command=self.show_login).pack()

    # ════════════ MAIN SHELL ════════════
    def load_main_ui(self):
        self.cancel_tick()
        self.clear_all()
        self.update_idletasks()

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # ── HEADER ──
        hdr = ctk.CTkFrame(self, height=56, fg_color=HEADER, corner_radius=0)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        hdr.grid_propagate(False)
        hdr.columnconfigure(1, weight=1)

        _lbl(hdr, "  Warehouse Management System", 15, True
             ).grid(row=0, column=0, padx=20, pady=10, sticky="w")

        rc = ORANGE if self.role == "admin" else GREEN
        _lbl(hdr, f"  {self.current_user}   [{self.role.upper()}]",
             12, color=rc).grid(row=0, column=1, padx=20, sticky="e")

        self.time_lbl = _lbl(hdr, "", 12)
        self.time_lbl.grid(row=0, column=2, padx=20, sticky="e")
        self._do_tick()

        # ── SIDEBAR — uses pack() only, never grid() ──
        sb = ctk.CTkFrame(self, width=210, fg_color=SIDEBAR, corner_radius=0)
        sb.grid(row=1, column=0, sticky="nsew")
        sb.grid_propagate(False)

        # Role badge
        badge_bg  = "#7c2d12" if self.role == "admin" else "#064e3b"
        badge_txt = "  Administrator" if self.role == "admin" else "  Employee"
        badge_clr = ORANGE if self.role == "admin" else GREEN

        badge = ctk.CTkFrame(sb, fg_color=badge_bg, height=36, corner_radius=0)
        badge.pack(fill="x", side="top")
        badge.pack_propagate(False)
        _lbl(badge, badge_txt, 11, True, color=badge_clr
             ).place(relx=0.5, rely=0.5, anchor="center")

        _lbl(sb, "  MENU", 10, color="#475569").pack(
            anchor="w", pady=(18, 6), padx=10, side="top")

        # All nav items
        nav = [
            ("  Dashboard",    self.show_dashboard),
            ("  Inventory",    self.show_inventory),
        ]
        if self.role == "admin":
            nav += [
                ("  Add Product",   self.show_add_product),
                ("  Suppliers",     self.show_suppliers),
                ("  Sales",         self.show_sales),
                ("  Manage Users",  self.show_users),
                ("  Activity Logs", self.show_logs),
            ]

        for label, cmd in nav:
            ctk.CTkButton(
                sb, text=label, anchor="w",
                fg_color="transparent", hover_color="#1f2937",
                text_color="white", font=("Arial", 13),
                height=38, command=cmd
            ).pack(fill="x", padx=10, pady=2, side="top")

        # Logout pinned to bottom
        ctk.CTkButton(
            sb, text="  Logout",
            fg_color="#7f1d1d", hover_color="#991b1b",
            text_color="white", font=("Arial", 13),
            height=38, command=self.show_login
        ).pack(fill="x", padx=10, pady=14, side="bottom")

        # ── MAIN AREA ──
        self.main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.main.grid(row=1, column=1, sticky="nsew")

        self.show_dashboard()

    # ════════════ DASHBOARD ════════════
    def show_dashboard(self):
        self.clear_main()

        _lbl(self.main, "Dashboard", 26, True, ORANGE
             ).pack(anchor="w", padx=30, pady=(24, 2))
        _lbl(self.main, "Warehouse overview", 13, color="#64748b"
             ).pack(anchor="w", padx=30, pady=(0, 16))

        products, suppliers, categories, sales = self.db.get_counts()

        cf = tk.Frame(self.main, bg=BG)
        cf.pack(anchor="w", padx=30)

        for col, (icon, lbl, val, color) in enumerate([
            ("📦", "Products",   str(products),   BLUE),
            ("🏭", "Suppliers",  str(suppliers),  ORANGE),
            ("🗂",  "Categories", str(categories), GREEN),
            ("💰", "Sales Rs",   str(sales),      YELLOW),
        ]):
            c = ctk.CTkFrame(cf, width=200, height=110,
                             fg_color=color, corner_radius=12)
            c.grid(row=0, column=col, padx=8, pady=6)
            c.grid_propagate(False)
            ctk.CTkLabel(c, text=icon, font=("Arial", 20)
                         ).place(relx=0.15, rely=0.3, anchor="center")
            ctk.CTkLabel(c, text=lbl, font=("Arial", 11), text_color="white"
                         ).place(relx=0.58, rely=0.3, anchor="center")
            ctk.CTkLabel(c, text=val, font=("Arial", 26, "bold"), text_color="white"
                         ).place(relx=0.5, rely=0.72, anchor="center")

        if HAS_MPL:
            self._draw_charts()
        else:
            _lbl(self.main, "Run:  pip install matplotlib  to enable charts",
                 12, color="#64748b").pack(pady=20)

    def _draw_charts(self):
        chart_frame = tk.Frame(self.main, bg=BG)
        chart_frame.pack(fill="both", expand=True, padx=24, pady=20)

        cat_data     = self.db.get_category_stock()
        monthly_data = self.db.get_monthly_sales()
        daily_data   = self.db.get_daily_sales()

        fig = Figure(figsize=(11, 4.2), facecolor="#1e293b")
        fig.subplots_adjust(wspace=0.35, left=0.07, right=0.97,
                            top=0.88, bottom=0.18)

        axes = [fig.add_subplot(1, 3, i+1) for i in range(3)]
        for ax in axes:
            ax.set_facecolor("#0f172a")
            ax.tick_params(colors="white", labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor("#334155")
            ax.title.set_color("white")
            ax.title.set_fontsize(20)

        if cat_data:
            cats, qtys = zip(*cat_data)
            colors = [BLUE, ORANGE, GREEN, YELLOW, PURPLE,
                      RED, "#ec4899", "#06b6d4"][:len(cats)]
            axes[0].bar(cats, qtys, color=colors, edgecolor="#1e293b")
            axes[0].set_title("Category-wise Stock")
            axes[0].set_xticklabels(cats, rotation=25, ha="right")
        else:
            axes[0].text(0.5, 0.5, "No data", color="gray",
                         ha="center", va="center", transform=axes[0].transAxes)
            axes[0].set_title("Category-wise Stock")

        if monthly_data:
            months, amounts = zip(*monthly_data)
            axes[1].plot(months, amounts, color=ORANGE, marker="o",
                         linewidth=2, markersize=5)
            axes[1].fill_between(months, amounts, color=ORANGE, alpha=0.15)
            axes[1].set_title("Monthly Sales (Rs)")
            axes[1].set_xticklabels(months, rotation=25, ha="right")
        else:
            axes[1].text(0.5, 0.5, "No data", color="gray",
                         ha="center", va="center", transform=axes[1].transAxes)
            axes[1].set_title("Monthly Sales (Rs)")

        if daily_data:
            days, damts = zip(*daily_data)
            short = [d[5:] for d in days]
            axes[2].bar(short, damts, color=GREEN, edgecolor="#1e293b")
            axes[2].set_title("Daily Sales Rs (14d)")
            axes[2].set_xticklabels(short, rotation=45, ha="right")
        else:
            axes[2].text(0.5, 0.5, "No data", color="gray",
                         ha="center", va="center", transform=axes[2].transAxes)
            axes[2].set_title("Daily Sales Rs (14d)")

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ════════════ INVENTORY ════════════
    def show_inventory(self):
        self.clear_main()

        _lbl(self.main, "Inventory", 26, True, ORANGE
             ).pack(anchor="w", padx=30, pady=(24, 4))

        sf = tk.Frame(self.main, bg=BG)
        sf.pack(fill="x", padx=30, pady=(0, 8))

        sv = tk.StringVar()
        ctk.CTkEntry(sf, placeholder_text="  Search SKU or Name...",
                     textvariable=sv, width=320, height=34
                     ).pack(side="left")
        _lbl(sf, "   Red=0 stock   Pink=low(<10)",
             11, color="#94a3b8").pack(side="right")

        cols   = ("SKU", "Name", "Category", "Qty", "Location", "Supplier")
        widths = [100, 180, 130, 60, 130, 120]

        holder = tk.Frame(self.main, bg=BG)
        holder.pack(fill="both", expand=True, padx=30, pady=(0, 4))

        tree = _tree(holder, cols, widths)
        sb2  = ttk.Scrollbar(holder, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb2.set)
        tree.pack(side="left", fill="both", expand=True)
        sb2.pack(side="left", fill="y")

        def reload_data():
            """Always fetch fresh from DB."""
            return self.db.get_inventory()

        def load(data):
            tree.delete(*tree.get_children())
            for r in data:
                qty = r[3]
                tag = "zero" if qty == 0 else ("low" if qty < 10 else "")
                tree.insert("", tk.END, values=r, tags=(tag,))

        all_data = reload_data()
        load(all_data)

        def on_search(*_):
            q = sv.get().lower()
            if q:
                load([r for r in all_data
                      if q in str(r[0]).lower() or q in str(r[1]).lower()])
            else:
                load(all_data)

        sv.trace_add("write", on_search)

        # Admin buttons below table
        if self.role == "admin":
            bf = tk.Frame(self.main, bg=BG)
            bf.pack(anchor="w", padx=30, pady=8)

            def edit_selected():
                sel = tree.selection()
                if not sel:
                    messagebox.showwarning("Select", "Select a product first.")
                    return
                sku = str(tree.item(sel[0])["values"][0])
                self._edit_product_dialog(sku, self.show_inventory)

            def delete_selected():
                sel = tree.selection()
                if not sel:
                    messagebox.showwarning("Select", "Select a product first.")
                    return
                sku  = str(tree.item(sel[0])["values"][0])
                name = str(tree.item(sel[0])["values"][1])
                if messagebox.askyesno("Delete", f"Delete '{name}' (SKU: {sku})?"):
                    self.db.delete_product(sku)
                    self.db.log(self.current_user, "DELETE PRODUCT",
                                f"SKU:{sku} Name:{name}")
                    self.show_inventory()   # full refresh

            _btn(bf, "  Edit Selected",   edit_selected,
                 HEADER, "#1e40af", 160).pack(side="left", padx=(0, 10))
            _btn(bf, "  Delete Selected", delete_selected,
                 "#7f1d1d", "#991b1b", 160).pack(side="left")

    def _edit_product_dialog(self, sku, on_done):
        prod = self.db.get_product(sku)
        if not prod:
            messagebox.showerror("Error", f"Product '{sku}' not found.")
            return
        # prod = (sku, name, category, quantity, location, supplier_id)

        win = ctk.CTkToplevel(self)
        win.title(f"Edit Product — {sku}")
        win.geometry("480x500")
        win.grab_set()
        win.focus()

        _lbl(win, f"Edit: {sku}", 18, True, ORANGE).pack(pady=(20, 14))

        suppliers = self.db.get_suppliers()
        sup_map   = {s[1]: s[0] for s in suppliers}   # name -> id
        sup_rev   = {s[0]: s[1] for s in suppliers}   # id -> name
        sup_names = ["-- None --"] + [s[1] for s in suppliers]
        cur_sup   = sup_rev.get(prod[5], "-- None --")

        fields = {}
        for label, val in [("Name",     prod[1]),
                            ("Category", prod[2]),
                            ("Quantity", prod[3]),
                            ("Location", prod[4])]:
            _lbl(win, label, 12, color="#94a3b8").pack(
                anchor="w", padx=30, pady=(8, 0))
            e = ctk.CTkEntry(win, width=400, height=34)
            e.insert(0, str(val))
            e.pack(padx=30)
            fields[label] = e

        _lbl(win, "Supplier", 12, color="#94a3b8").pack(
            anchor="w", padx=30, pady=(8, 0))
        sup_var = tk.StringVar(value=cur_sup)
        ctk.CTkOptionMenu(win, values=sup_names,
                          variable=sup_var, width=400).pack(padx=30)

        err = _lbl(win, "", 11, color=RED)
        err.pack(pady=(8, 0))

        def save():
            try:
                name = fields["Name"].get().strip()
                cat  = fields["Category"].get().strip()
                qty  = int(fields["Quantity"].get().strip())
                loc  = fields["Location"].get().strip()
                sid  = sup_map.get(sup_var.get())   # None if no supplier
                if not name or not cat:
                    err.configure(text="Name and Category are required.")
                    return
                self.db.update_product(sku, name, cat, qty, loc, sid)
                self.db.log(self.current_user, "EDIT PRODUCT",
                            f"SKU:{sku} name={name} qty={qty}")
                win.destroy()
                on_done()   # refresh inventory page
            except ValueError:
                err.configure(text="Quantity must be a whole number.")

        _btn(win, "  Save Changes", save, ORANGE, "#ea580c",
             width=400, height=40,
             font=("Arial", 13, "bold")).pack(padx=30, pady=18)

    # ════════════ ADD PRODUCT ════════════
    def show_add_product(self):
        self.clear_main()

        _lbl(self.main, "Add Product", 26, True, ORANGE
             ).pack(anchor="w", padx=30, pady=(24, 20))

        form = ctk.CTkFrame(self.main, fg_color=CARD_BG, corner_radius=12)
        form.pack(padx=30, anchor="nw", ipadx=20, ipady=10)

        suppliers = self.db.get_suppliers()
        sup_map   = {s[1]: s[0] for s in suppliers}
        sup_names = ["-- None --"] + [s[1] for s in suppliers]

        fields = {}
        for label in ["SKU", "Name", "Category", "Quantity", "Location"]:
            _lbl(form, label, 12, color="#94a3b8").pack(
                anchor="w", padx=24, pady=(12, 0))
            e = ctk.CTkEntry(form, width=420, height=34)
            e.pack(padx=24)
            fields[label] = e

        _lbl(form, "Supplier", 12, color="#94a3b8").pack(
            anchor="w", padx=24, pady=(12, 0))
        sup_var = tk.StringVar(value=sup_names[0])
        ctk.CTkOptionMenu(form, values=sup_names,
                          variable=sup_var, width=420).pack(padx=24)

        err = _lbl(form, "", 11, color=RED)
        err.pack(pady=(8, 0))

        def submit():
            try:
                sku  = fields["SKU"].get().strip()
                name = fields["Name"].get().strip()
                cat  = fields["Category"].get().strip()
                qty  = int(fields["Quantity"].get().strip())
                loc  = fields["Location"].get().strip()
                sid  = sup_map.get(sup_var.get())
                if not sku or not name or not cat:
                    err.configure(text="SKU, Name and Category are required.")
                    return
                if self.db.add_product(sku, name, cat, qty, loc, sid):
                    self.db.log(self.current_user, "ADD PRODUCT",
                                f"SKU:{sku} Name:{name} Qty:{qty}")
                    messagebox.showinfo("Added", f"Product '{name}' added!")
                    self.show_inventory()   # go to inventory so user sees new row
                else:
                    err.configure(text=f"SKU '{sku}' already exists.")
            except ValueError:
                err.configure(text="Quantity must be a whole number.")

        _btn(form, "  Add Product", submit, ORANGE, "#ea580c",
             width=420, height=42,
             font=("Arial", 13, "bold")).pack(padx=24, pady=20)

    # ════════════ SUPPLIERS ════════════
    def show_suppliers(self):
        self.clear_main()

        _lbl(self.main, "Supplier Management", 26, True, ORANGE
             ).pack(anchor="w", padx=30, pady=(24, 16))

        af = ctk.CTkFrame(self.main, fg_color=CARD_BG, corner_radius=12)
        af.pack(fill="x", padx=30, pady=(0, 16), ipadx=10, ipady=10)

        _lbl(af, "Add New Supplier", 14, True).pack(
            anchor="w", padx=20, pady=(10, 8))

        row = tk.Frame(af, bg=CARD_BG)
        row.pack(fill="x", padx=20, pady=(0, 8))

        sn = ctk.CTkEntry(row, placeholder_text="Supplier Name *", width=200, height=34)
        sc = ctk.CTkEntry(row, placeholder_text="Contact",          width=160, height=34)
        se = ctk.CTkEntry(row, placeholder_text="Email",            width=200, height=34)
        sn.pack(side="left", padx=(0, 8))
        sc.pack(side="left", padx=(0, 8))
        se.pack(side="left", padx=(0, 8))

        sup_err = _lbl(af, "", 11, color=RED)
        sup_err.pack()

        cols   = ("ID", "Name", "Contact", "Email")
        widths = [50, 250, 180, 220]
        holder = tk.Frame(self.main, bg=BG)
        holder.pack(fill="both", expand=True, padx=30)

        tree = _tree(holder, cols, widths)
        tree.pack(fill="both", expand=True)

        def refresh():
            tree.delete(*tree.get_children())
            for s in self.db.get_suppliers():
                tree.insert("", tk.END, values=s)

        refresh()

        def add_sup():
            n = sn.get().strip()
            if not n:
                sup_err.configure(text="Supplier name is required."); return
            if self.db.add_supplier(n, sc.get().strip(), se.get().strip()):
                self.db.log(self.current_user, "ADD SUPPLIER", f"Name:{n}")
                for e in (sn, sc, se): e.delete(0, tk.END)
                sup_err.configure(text="")
                refresh()
            else:
                sup_err.configure(text="Supplier already exists.")

        def del_sup():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a supplier."); return
            sid  = tree.item(sel[0])["values"][0]
            name = tree.item(sel[0])["values"][1]
            if messagebox.askyesno("Delete", f"Delete supplier '{name}'?"):
                self.db.delete_supplier(sid)
                self.db.log(self.current_user, "DELETE SUPPLIER", f"Name:{name}")
                refresh()

        btn_row = tk.Frame(af, bg=CARD_BG)
        btn_row.pack(anchor="w", padx=20, pady=(4, 8))
        _btn(btn_row, "  Add Supplier", add_sup, GREEN, "#0d9488", 160
             ).pack(side="left", padx=(0, 10))

        bf = tk.Frame(self.main, bg=BG)
        bf.pack(anchor="w", padx=30, pady=8)
        _btn(bf, "  Delete Selected", del_sup, "#7f1d1d", "#991b1b", 160
             ).pack(side="left")

    # ════════════ SALES ════════════
    def show_sales(self):
        self.clear_main()

        _lbl(self.main, "Sales", 26, True, ORANGE
             ).pack(anchor="w", padx=30, pady=(24, 16))

        af = ctk.CTkFrame(self.main, fg_color=CARD_BG, corner_radius=12)
        af.pack(fill="x", padx=30, pady=(0, 16), ipadx=10, ipady=10)

        _lbl(af, "Record New Sale", 14, True).pack(
            anchor="w", padx=20, pady=(10, 8))

        row = tk.Frame(af, bg=CARD_BG)
        row.pack(fill="x", padx=20)

        sk_e = ctk.CTkEntry(row, placeholder_text="SKU *",      width=130, height=34)
        qt_e = ctk.CTkEntry(row, placeholder_text="Qty *",      width=80,  height=34)
        am_e = ctk.CTkEntry(row, placeholder_text="Amount *",   width=120, height=34)
        dt_e = ctk.CTkEntry(row, placeholder_text="YYYY-MM-DD", width=150, height=34)
        dt_e.insert(0, datetime.date.today().isoformat())
        for w in (sk_e, qt_e, am_e, dt_e):
            w.pack(side="left", padx=(0, 8))

        sale_err = _lbl(af, "", 11, color=RED)
        sale_err.pack()

        cols   = ("ID", "SKU", "Product", "Qty", "Amount", "Date")
        widths = [50, 100, 200, 60, 110, 130]
        holder = tk.Frame(self.main, bg=BG)
        holder.pack(fill="both", expand=True, padx=30)

        tree = _tree(holder, cols, widths)
        sb2  = ttk.Scrollbar(holder, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb2.set)
        tree.pack(side="left", fill="both", expand=True)
        sb2.pack(side="left", fill="y")

        def refresh():
            tree.delete(*tree.get_children())
            for s in self.db.get_sales():
                tree.insert("", tk.END, values=s)

        refresh()

        def add_sale():
            try:
                sku = sk_e.get().strip()
                qty = int(qt_e.get().strip())
                amt = float(am_e.get().strip())
                dt  = dt_e.get().strip()
                if not sku:
                    sale_err.configure(text="SKU is required."); return
                self.db.add_sale(sku, qty, amt, dt)
                self.db.log(self.current_user, "ADD SALE",
                            f"SKU:{sku} Qty:{qty} Amt:{amt}")
                for e in (sk_e, qt_e, am_e): e.delete(0, tk.END)
                sale_err.configure(text="")
                refresh()
            except ValueError:
                sale_err.configure(text="Qty = whole number, Amount = decimal.")

        btn_row = tk.Frame(af, bg=CARD_BG)
        btn_row.pack(anchor="w", padx=20, pady=(8, 8))
        _btn(btn_row, "  Record Sale", add_sale, GREEN, "#0d9488", 160
             ).pack(side="left")

    # ════════════ MANAGE USERS ════════════
    def show_users(self):
        self.clear_main()

        _lbl(self.main, "Manage Users", 26, True, ORANGE
             ).pack(anchor="w", padx=30, pady=(24, 4))
        _lbl(self.main,
             "Only the 'admin' account is protected. Promoted admins can be deleted.",
             11, color="#64748b").pack(anchor="w", padx=30, pady=(0, 12))

        cols   = ("Username", "Role")
        widths = [320, 200]
        holder = tk.Frame(self.main, bg=BG)
        holder.pack(fill="both", expand=True, padx=30)

        tree = _tree(holder, cols, widths)
        tree.pack(fill="both", expand=True)

        def refresh():
            tree.delete(*tree.get_children())
            for u in self.db.get_users():
                tree.insert("", tk.END, values=u)

        refresh()

        bf = tk.Frame(self.main, bg=BG)
        bf.pack(anchor="w", padx=30, pady=12)

        def delete_user():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a user."); return
            uname = str(tree.item(sel[0])["values"][0])
            if uname == "admin":
                messagebox.showerror("Protected",
                    "The default 'admin' account cannot be deleted."); return
            if uname == self.current_user:
                messagebox.showerror("Error", "You cannot delete yourself."); return
            if messagebox.askyesno("Confirm", f"Delete user '{uname}'?"):
                self.db.delete_user(uname)
                self.db.log(self.current_user, "DELETE USER", uname)
                refresh()

        def toggle_role():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a user."); return
            uname    = str(tree.item(sel[0])["values"][0])
            cur_role = str(tree.item(sel[0])["values"][1])
            new_role = "user" if cur_role == "admin" else "admin"
            action   = "Demote to Employee" if cur_role == "admin" else "Promote to Admin"
            if messagebox.askyesno("Confirm", f"{action}: '{uname}'?"):
                self.db.set_role(uname, new_role)
                self.db.log(self.current_user, f"SET ROLE {new_role.upper()}", uname)
                refresh()

        _btn(bf, "  Delete User",    delete_user, "#7f1d1d", "#991b1b", 150
             ).pack(side="left", padx=(0, 12))
        _btn(bf, "  Toggle Role", toggle_role,  HEADER,   "#1e40af", 160
             ).pack(side="left")


    # ════════════ HELPERS ════════════
    def clear_main(self):
        if self.main:
            try:
                for w in self.main.winfo_children():
                    w.destroy()
            except Exception:
                pass

    def clear_all(self):
        try:
            for w in self.winfo_children():
                w.destroy()
        except Exception:
            pass

# ───────────── Application Entry Point ─────────────
if __name__ == "__main__":
    print("Starting Warehouse Management System...")
    app = WMSApp()
    app.mainloop()
