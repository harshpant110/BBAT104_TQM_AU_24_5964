import sqlite3
import tkinter as tk
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from tkinter import messagebox, ttk

import customtkinter as ctk

from database import (
    add_menu_item,
    delete_menu_item,
    get_menu_items,
    update_menu_item,
)
from ui.theme import FONTS, SIZES


TREEVIEW_STYLE = "Restaurant.Treeview"
SCROLLBAR_STYLE = "Restaurant.Vertical.TScrollbar"

ALL_CATEGORIES = "All Categories"
STATUS_FILTERS = ("All", "Available", "Unavailable")

MAX_NAME_LENGTH = 80
MAX_CATEGORY_LENGTH = 40
MAX_PRICE = Decimal("100000")


# =============================================================
# Data model
# =============================================================

@dataclass(frozen=True)
class MenuItem:
    id: int
    name: str
    category: str
    price: float
    available: bool

    @classmethod
    def from_row(cls, row):
        item_id, name, category, price, available = row
        return cls(
            id=item_id,
            name=name or "",
            category=category or "",
            price=float(price or 0),
            available=bool(available),
        )


# =============================================================
# Reusable modal dialog base
# =============================================================

class ModalDialog(ctk.CTkToplevel):
    """Centered modal window with safe focus/grab handling."""

    def __init__(self, page, title, width, height):
        parent = page.winfo_toplevel()
        super().__init__(parent)

        self.page = page
        self.colors = page.colors
        self._grab_attempts = 0

        self.title(title)
        self.resizable(False, False)
        self.configure(fg_color=self.colors["surface"])
        self.transient(parent)

        self.geometry(f"{width}x{height}")
        self._center_on(parent, width, height)

        self.bind("<Escape>", lambda _e: self.destroy())

        # CustomTkinter finishes configuring Toplevel windows shortly after
        # creation; grabbing too early raises "window not viewable" errors.
        self.after(150, self._take_focus)

    def _center_on(self, parent, width, height):
        parent.update_idletasks()

        scale = 1.0
        getter = getattr(self, "_get_window_scaling", None)
        if callable(getter):
            try:
                scale = float(getter())
            except Exception:
                scale = 1.0

        x = parent.winfo_rootx() + (parent.winfo_width() - width * scale) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height * scale) // 2

        # Use the raw Tk call so CustomTkinter does not scale the offset again.
        tk.Toplevel.geometry(self, f"+{max(int(x), 0)}+{max(int(y), 0)}")

    def _take_focus(self):
        if not self.winfo_exists():
            return

        try:
            self.grab_set()
        except tk.TclError:
            self._grab_attempts += 1
            if self._grab_attempts < 10:
                self.after(50, self._take_focus)
            return

        self.lift()
        self.focus_force()
        self.on_shown()

    def on_shown(self):
        """Hook for subclasses."""

    def font(self, kind, size, weight="normal"):
        return ctk.CTkFont(
            family=FONTS[kind][0],
            size=size,
            weight=weight,
        )


# =============================================================
# Confirmation dialog
# =============================================================

class ConfirmDialog(ModalDialog):
    def __init__(
        self,
        page,
        title,
        heading,
        message,
        confirm_text,
        on_confirm,
    ):
        super().__init__(page, title, 420, 230)

        self.on_confirm = on_confirm

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=26, pady=24)

        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(side="bottom", fill="x")

        ctk.CTkLabel(
            container,
            text=heading,
            font=self.font("heading", 20, "bold"),
            text_color=self.colors["text_primary"],
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            container,
            text=message,
            font=self.font("body", 13),
            text_color=self.colors["text_secondary"],
            anchor="w",
            justify="left",
            wraplength=360,
        ).pack(fill="x", pady=(8, 0))

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            height=38,
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["border"],
            text_color=self.colors["text_primary"],
            hover_color=self.colors["sidebar_hover"],
            command=self.destroy,
        ).pack(side="right", padx=(10, 0))

        self.confirm_button = ctk.CTkButton(
            button_frame,
            text=confirm_text,
            width=110,
            height=38,
            fg_color=self.colors["danger"],
            hover_color="#A93226",
            text_color="#FFFFFF",
            command=self._confirm,
        )
        self.confirm_button.pack(side="right")

    def _confirm(self):
        self.confirm_button.configure(state="disabled")
        callback = self.on_confirm
        self.destroy()
        callback()


# =============================================================
# Add / edit dialog
# =============================================================

class ItemDialog(ModalDialog):
    def __init__(self, page, item, categories, on_submit):
        editing = item is not None

        super().__init__(
            page,
            "Edit Menu Item" if editing else "Add Menu Item",
            460,
            580,
        )

        self.item = item
        self.on_submit = on_submit

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=26)

        # Bottom bar is packed first so it is never pushed out of view.
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(side="bottom", fill="x")

        ctk.CTkLabel(
            container,
            text="Edit Menu Item" if editing else "Add Menu Item",
            font=self.font("heading", 22, "bold"),
            text_color=self.colors["text_primary"],
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            container,
            text=(
                "Update the details of this menu item."
                if editing
                else "Add a new item to the restaurant menu."
            ),
            font=self.font("body", 13),
            text_color=self.colors["text_secondary"],
            anchor="w",
        ).pack(fill="x", pady=(4, 20))

        self.name_entry = self._field(
            container,
            "Item Name",
            "e.g. Paneer Butter Masala",
        )

        self.category_box = self._combo_field(
            container,
            "Category",
            categories,
            "e.g. Main Course",
        )

        self.price_entry = self._field(
            container,
            "Price (₹)",
            "e.g. 249.00",
        )

        self.availability = ctk.CTkSwitch(
            container,
            text="Available for ordering",
            font=self.font("body", 13),
            text_color=self.colors["text_primary"],
            progress_color=self.colors["accent"],
        )
        self.availability.pack(anchor="w", pady=(4, 12))

        self.error_label = ctk.CTkLabel(
            container,
            text="",
            font=self.font("small", 12),
            text_color=self.colors["danger"],
            anchor="w",
            justify="left",
            wraplength=390,
        )
        self.error_label.pack(fill="x")

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            height=38,
            width=100,
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["border"],
            text_color=self.colors["text_primary"],
            hover_color=self.colors["sidebar_hover"],
            command=self.destroy,
        ).pack(side="right", padx=(10, 0))

        self.save_button = ctk.CTkButton(
            button_frame,
            text="Save Changes" if editing else "Save Item",
            height=38,
            width=125,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            text_color="#FFFFFF",
            command=self._submit,
        )
        self.save_button.pack(side="right")

        if editing:
            self.name_entry.insert(0, item.name)
            self.category_box.set(item.category)
            self.price_entry.insert(0, f"{item.price:.2f}")
            if item.available:
                self.availability.select()
        else:
            self.category_box.set("")
            self.availability.select()

        self.bind("<Return>", lambda _e: self._submit())

    # ---------------------------------------------------------
    # Form helpers
    # ---------------------------------------------------------

    def _label(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=self.font("body", 12, "bold"),
            text_color=self.colors["text_primary"],
            anchor="w",
        ).pack(fill="x")

    def _field(self, parent, label, placeholder):
        self._label(parent, label)

        entry = ctk.CTkEntry(
            parent,
            height=40,
            placeholder_text=placeholder,
            border_color=self.colors["border"],
        )
        entry.pack(fill="x", pady=(6, 14))
        return entry

    def _combo_field(self, parent, label, values, placeholder):
        self._label(parent, label)

        box = ctk.CTkComboBox(
            parent,
            height=40,
            values=values or [""],
            border_color=self.colors["border"],
            button_color=self.colors["border"],
            button_hover_color=self.colors["accent"],
        )
        box.pack(fill="x", pady=(6, 14))
        return box

    def on_shown(self):
        self.name_entry.focus_set()

    # ---------------------------------------------------------
    # Submit
    # ---------------------------------------------------------

    def _submit(self):
        if not self.winfo_exists():
            return

        result = self.on_submit(
            self.name_entry.get(),
            self.category_box.get(),
            self.price_entry.get(),
            bool(self.availability.get()),
            self.item,
        )

        if result is None:
            self.destroy()
            return

        field, message = result
        self.error_label.configure(text=message)

        target = {
            "name": self.name_entry,
            "category": self.category_box,
            "price": self.price_entry,
        }.get(field)

        if target is not None:
            target.focus_set()


# =============================================================
# Menu page
# =============================================================

class MenuPage(ctk.CTkFrame):
    COLUMNS = (
        "number",
        "name",
        "category",
        "price",
        "status",
        "edit",
        "delete",
    )

    HEADINGS = {
        "number": "No.",
        "name": "Item Name",
        "category": "Category",
        "price": "Price",
        "status": "Status",
        "edit": "Actions",
        "delete": "",
    }

    SORTABLE = ("name", "category", "price", "status")

    def __init__(self, master, colors):
        super().__init__(master, fg_color="transparent")

        self.colors = colors

        self.all_items = []
        self.menu_items = {}      # tree row id -> MenuItem
        self._row_by_item = {}    # MenuItem.id -> tree row id

        self.sort_column = None
        self.sort_reverse = False

        self._search_job = None
        self._active_dialog = None
        self._select_after_load = None

        self.create_header()
        self.create_stats()
        self.create_toolbar()
        self.create_footer()
        self.create_menu_table()
        self.create_context_menu()

        self.load_menu_items()

    # =========================================================
    # Helpers
    # =========================================================

    def font(self, kind, size, weight="normal"):
        return ctk.CTkFont(
            family=FONTS[kind][0],
            size=size,
            weight=weight,
        )

    @staticmethod
    def format_price(value):
        return f"₹{value:,.2f}"

    def destroy(self):
        if self._search_job is not None:
            try:
                self.after_cancel(self._search_job)
            except (tk.TclError, ValueError):
                pass
            self._search_job = None
        super().destroy()

    # =========================================================
    # Header
    # =========================================================

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            header_left,
            text="Menu Management",
            font=self.font("heading", 22, "bold"),
            text_color=self.colors["text_primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_left,
            text="Manage menu items, categories, prices and availability.",
            font=self.font("body", 13),
            text_color=self.colors["text_secondary"],
        ).pack(anchor="w", pady=(4, 0))

        self.add_button = ctk.CTkButton(
            header,
            text="+  Add Menu Item",
            height=38,
            width=150,
            corner_radius=8,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            text_color="#FFFFFF",
            font=self.font("body", 12, "bold"),
            command=self.open_add_item_dialog,
        )
        self.add_button.pack(side="right", padx=(15, 0))

    # =========================================================
    # Summary cards
    # =========================================================

    def create_stats(self):
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 16))

        titles = (
            "Total Items",
            "Available",
            "Unavailable",
            "Categories",
        )

        self.stat_labels = {}

        for index, title in enumerate(titles):
            stats.grid_columnconfigure(index, weight=1, uniform="stats")

            card = ctk.CTkFrame(
                stats,
                fg_color=self.colors["surface"],
                corner_radius=SIZES["card_radius"],
                border_width=1,
                border_color=self.colors["border"],
            )
            card.grid(
                row=0,
                column=index,
                sticky="ew",
                padx=(0 if index == 0 else 6, 0 if index == len(titles) - 1 else 6),
            )

            value = ctk.CTkLabel(
                card,
                text="0",
                font=self.font("heading", 22, "bold"),
                text_color=self.colors["text_primary"],
                anchor="w",
            )
            value.pack(fill="x", padx=18, pady=(12, 0))

            ctk.CTkLabel(
                card,
                text=title,
                font=self.font("small", 12),
                text_color=self.colors["text_secondary"],
                anchor="w",
            ).pack(fill="x", padx=18, pady=(0, 12))

            self.stat_labels[title] = value

    def update_stats(self):
        total = len(self.all_items)
        available = sum(1 for item in self.all_items if item.available)
        categories = {item.category.lower() for item in self.all_items}

        self.stat_labels["Total Items"].configure(text=str(total))
        self.stat_labels["Available"].configure(text=str(available))
        self.stat_labels["Unavailable"].configure(text=str(total - available))
        self.stat_labels["Categories"].configure(text=str(len(categories)))

    # =========================================================
    # Toolbar (search + filters)
    # =========================================================

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))

        self.search_entry = ctk.CTkEntry(
            toolbar,
            height=38,
            width=280,
            placeholder_text="Search by name or category...",
            border_color=self.colors["border"],
            fg_color=self.colors["surface"],
            text_color=self.colors["text_primary"],
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

        self.category_var = tk.StringVar(value=ALL_CATEGORIES)

        self.category_menu = ctk.CTkOptionMenu(
            toolbar,
            height=38,
            width=180,
            values=[ALL_CATEGORIES],
            variable=self.category_var,
            command=lambda _v: self.apply_filters(),
            fg_color=self.colors["surface"],
            button_color=self.colors["border"],
            button_hover_color=self.colors["accent"],
            text_color=self.colors["text_primary"],
            dropdown_text_color=self.colors["text_primary"],
            dropdown_fg_color=self.colors["surface"],
            dropdown_hover_color=self.colors["sidebar_hover"],
        )
        self.category_menu.pack(side="left", padx=(12, 0))

        self.status_filter = ctk.CTkSegmentedButton(
            toolbar,
            values=list(STATUS_FILTERS),
            height=38,
            command=lambda _v: self.apply_filters(),
            fg_color=self.colors["border"],
            selected_color=self.colors["accent"],
            selected_hover_color=self.colors["accent_hover"],
            unselected_color=self.colors["surface"],
            unselected_hover_color=self.colors["sidebar_hover"],
            text_color=self.colors["text_primary"],
        )
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=(12, 0))

        ctk.CTkButton(
            toolbar,
            text="Refresh",
            height=38,
            width=90,
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["border"],
            text_color=self.colors["text_primary"],
            hover_color=self.colors["sidebar_hover"],
            command=self.load_menu_items,
        ).pack(side="right")

    def _on_search_key(self, event):
        if event.keysym == "Escape":
            self.search_entry.delete(0, "end")

        if self._search_job is not None:
            self.after_cancel(self._search_job)

        # Debounce so we don't rebuild the table on every keystroke.
        self._search_job = self.after(180, self._run_search)

    def _run_search(self):
        self._search_job = None
        self.apply_filters()

    # =========================================================
    # Footer
    # =========================================================

    def create_footer(self):
        self.footer_label = ctk.CTkLabel(
            self,
            text="",
            font=self.font("small", 12),
            text_color=self.colors["text_secondary"],
            anchor="w",
        )
        # Packed before the table so it always stays visible.
        self.footer_label.pack(side="bottom", fill="x", pady=(10, 0))

    # =========================================================
    # Table
    # =========================================================

    def create_menu_table(self):
        self.table_card = ctk.CTkFrame(
            self,
            fg_color=self.colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=self.colors["border"],
        )
        self.table_card.pack(fill="both", expand=True)

        table_container = ctk.CTkFrame(
            self.table_card,
            fg_color="transparent",
        )
        table_container.pack(fill="both", expand=True, padx=18, pady=18)

        self._configure_styles()

        self.menu_tree = ttk.Treeview(
            table_container,
            columns=self.COLUMNS,
            show="headings",
            style=TREEVIEW_STYLE,
            selectmode="browse",
        )

        self.menu_tree.bind(
            "<FocusOut>",
            lambda event: self.menu_tree.selection_remove(
                self.menu_tree.selection()
            ),
        )

        for column in self.COLUMNS:
            anchor = "w" if column in ("name", "category") else "center"
            command = (
                (lambda c=column: self.sort_by(c))
                if column in self.SORTABLE
                else ""
            )
            self.menu_tree.heading(
                column,
                text=self.HEADINGS[column],
                anchor=anchor,
                command=command,
            )

        self.menu_tree.column("number", width=65, minwidth=55, stretch=False, anchor="center")
        self.menu_tree.column("name", width=280, minwidth=180, stretch=True, anchor="w")
        self.menu_tree.column("category", width=190, minwidth=140, stretch=True, anchor="w")
        self.menu_tree.column("price", width=130, minwidth=110, stretch=True, anchor="center")
        self.menu_tree.column("status", width=140, minwidth=110, stretch=True, anchor="center")
        self.menu_tree.column("edit", width=90, minwidth=80, stretch=False, anchor="center")
        self.menu_tree.column("delete", width=90, minwidth=80, stretch=False, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.menu_tree.yview,
            style=SCROLLBAR_STYLE,
        )
        self.menu_tree.configure(yscrollcommand=scrollbar.set)

        self.menu_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(6, 0))

        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # Single combined tag per row avoids tag-precedence ambiguity.
        primary = self.colors["text_primary"]
        muted = self.colors["text_secondary"]

        self.menu_tree.tag_configure("row_even", background=self.colors["surface"], foreground=primary)
        self.menu_tree.tag_configure("row_odd", background=self.colors["background"], foreground=primary)
        self.menu_tree.tag_configure("row_even_off", background=self.colors["surface"], foreground=muted)
        self.menu_tree.tag_configure("row_odd_off", background=self.colors["background"], foreground=muted)

        # Empty-state message shown on top of the table.
        self.empty_label = ctk.CTkLabel(
            table_container,
            text="",
            font=self.font("body", 14),
            text_color=self.colors["text_secondary"],
            fg_color=self.colors["surface"],
            justify="center",
        )

        self._action_columns = {
            f"#{self.COLUMNS.index('edit') + 1}": "edit",
            f"#{self.COLUMNS.index('delete') + 1}": "delete",
        }

        self.menu_tree.bind("<Button-1>", self.handle_table_click)
        self.menu_tree.bind("<Double-1>", self.handle_double_click)
        self.menu_tree.bind("<Motion>", self.handle_motion)
        self.menu_tree.bind("<Leave>", lambda _e: self.menu_tree.configure(cursor=""))
        self.menu_tree.bind("<Button-3>", self.show_context_menu)
        self.menu_tree.bind("<Button-2>", self.show_context_menu)  # macOS
        self.menu_tree.bind("<Return>", lambda _e: self.edit_selected())
        self.menu_tree.bind("<Delete>", lambda _e: self.delete_selected())
        self.menu_tree.bind("<Control-n>", lambda _e: self.open_add_item_dialog())
        self.menu_tree.bind("<Control-f>", lambda _e: self.search_entry.focus_set())

    def _configure_styles(self):
        style = ttk.Style()

        if style.theme_use() != "clam":
            try:
                style.theme_use("clam")
            except tk.TclError:
                pass

        style.layout(
            TREEVIEW_STYLE,
            [("Treeview.treearea", {"sticky": "nswe"})],
        )

        style.configure(
            TREEVIEW_STYLE,
            background=self.colors["surface"],
            foreground=self.colors["text_primary"],
            fieldbackground=self.colors["surface"],
            borderwidth=0,
            relief="flat",
            rowheight=48,
            font=(FONTS["body"][0], 12),
        )

        style.configure(
            f"{TREEVIEW_STYLE}.Heading",
            background=self.colors["background"],
            foreground=self.colors["text_primary"],
            borderwidth=0,
            relief="flat",
            padding=(14, 12),
            font=(FONTS["small"][0], 12, "bold"),
        )

        style.map(
            TREEVIEW_STYLE,
            background=[("selected", self.colors["accent"])],
            foreground=[("selected", "#FFFFFF")],
        )

        style.map(
            f"{TREEVIEW_STYLE}.Heading",
            background=[("active", self.colors["sidebar_hover"])],
        )

        style.configure(
            SCROLLBAR_STYLE,
            background=self.colors["sidebar_hover"],
            troughcolor=self.colors["surface"],
            bordercolor=self.colors["surface"],
            arrowcolor=self.colors["text_secondary"],
            relief="flat",
            borderwidth=0,
        )

        style.map(
            SCROLLBAR_STYLE,
            background=[
                ("pressed", self.colors["accent_hover"]),
                ("active", self.colors["accent"]),
            ],
        )

    # =========================================================
    # Context menu
    # =========================================================

    def create_context_menu(self):
        self.context_menu = tk.Menu(
            self,
            tearoff=0,
            bg=self.colors["surface"],
            fg=self.colors["text_primary"],
            activebackground=self.colors["accent"],
            activeforeground="#FFFFFF",
            borderwidth=0,
            font=(FONTS["body"][0], 11),
        )

    def show_context_menu(self, event):
        row_id = self.menu_tree.identify_row(event.y)
        if not row_id:
            return

        self.menu_tree.selection_set(row_id)
        item = self.menu_items.get(row_id)
        if not item:
            return

        self.context_menu.delete(0, "end")
        self.context_menu.add_command(
            label="Edit item",
            command=lambda: self.open_edit_item_dialog(item),
        )
        self.context_menu.add_command(
            label="Mark as unavailable" if item.available else "Mark as available",
            command=lambda: self.set_availability(item, not item.available),
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Delete item",
            command=lambda: self.confirm_delete(item),
        )

        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    # =========================================================
    # Data loading / filtering / sorting
    # =========================================================

    def load_menu_items(self):
        try:
            rows = get_menu_items()
            self.all_items = [MenuItem.from_row(row) for row in rows]
        except (sqlite3.Error, ValueError, TypeError):
            messagebox.showerror(
                "Could Not Load Menu",
                "The menu could not be loaded because of a database error.",
                parent=self.winfo_toplevel(),
            )
            return

        self.refresh_category_filter()
        self.update_stats()
        self.apply_filters()

    # Public alias so the main app can call page.refresh() on navigation.
    refresh = load_menu_items

    def categories(self):
        seen = {}
        for item in self.all_items:
            if item.category:
                seen.setdefault(item.category.lower(), item.category)
        return sorted(seen.values(), key=str.lower)

    def refresh_category_filter(self):
        categories = self.categories()
        self.category_menu.configure(values=[ALL_CATEGORIES] + categories)

        if self.category_var.get() not in categories:
            self.category_var.set(ALL_CATEGORIES)

    def apply_filters(self):
        query = self.search_entry.get().strip().lower()
        category = self.category_var.get()
        status = self.status_filter.get()

        rows = []
        for item in self.all_items:
            if category != ALL_CATEGORIES and item.category != category:
                continue
            if status == "Available" and not item.available:
                continue
            if status == "Unavailable" and item.available:
                continue
            if query and query not in item.name.lower() and query not in item.category.lower():
                continue
            rows.append(item)

        if self.sort_column:
            key_functions = {
                "name": lambda i: i.name.lower(),
                "category": lambda i: (i.category.lower(), i.name.lower()),
                "price": lambda i: i.price,
                "status": lambda i: (not i.available, i.name.lower()),
            }
            rows.sort(
                key=key_functions[self.sort_column],
                reverse=self.sort_reverse,
            )

        self.render_rows(rows)

    def sort_by(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        for name, text in self.HEADINGS.items():
            arrow = ""
            if name == self.sort_column:
                arrow = "  ▼" if self.sort_reverse else "  ▲"
            self.menu_tree.heading(name, text=text + arrow)

        self.apply_filters()

    # =========================================================
    # Rendering
    # =========================================================

    def render_rows(self, rows):
        selected = self.selected_item()
        selected_id = selected.id if selected else None

        y_position = self.menu_tree.yview()[0]

        self.menu_tree.delete(*self.menu_tree.get_children())
        self.menu_items.clear()
        self._row_by_item.clear()

        target_row = None

        for number, item in enumerate(rows, start=1):
            tag = "row_even" if number % 2 == 0 else "row_odd"
            if not item.available:
                tag += "_off"

            tree_id = self.menu_tree.insert(
                "",
                "end",
                values=(
                    number,
                    item.name,
                    item.category,
                    self.format_price(item.price),
                    "Available" if item.available else "Unavailable",
                    "Edit",
                    "Delete",
                ),
                tags=(tag,),
            )

            self.menu_items[tree_id] = item
            self._row_by_item[item.id] = tree_id

            if self._select_after_load == (item.name.lower(), item.category.lower()):
                target_row = tree_id

        if target_row is not None:
            self._select_after_load = None
            self.menu_tree.selection_set(target_row)
            self.menu_tree.see(target_row)
        else:
            if selected_id in self._row_by_item:
                self.menu_tree.selection_set(self._row_by_item[selected_id])
            self.menu_tree.yview_moveto(y_position)

        self.update_empty_state(len(rows))

        total = len(self.all_items)
        self.footer_label.configure(
            text=(
                f"Showing {len(rows)} of {total} item{'s' if total != 1 else ''}"
                "   •   Double-click or press Enter to edit"
                "   •   Right-click for more options"
            )
        )

    def update_empty_state(self, visible_count):
        if visible_count:
            self.empty_label.place_forget()
            return

        if not self.all_items:
            message = "No menu items yet.\nClick “Add Menu Item” to create your first one."
        else:
            message = "No items match your search or filters."

        self.empty_label.configure(text=message)
        self.empty_label.place(relx=0.5, rely=0.55, anchor="center")

    def selected_item(self):
        selection = self.menu_tree.selection()
        if not selection:
            return None
        return self.menu_items.get(selection[0])

    # =========================================================
    # Mouse / keyboard handling
    # =========================================================

    def handle_motion(self, event):
        region = self.menu_tree.identify_region(event.x, event.y)
        column = self.menu_tree.identify_column(event.x)
        row = self.menu_tree.identify_row(event.y)

        over_action = (
            region == "cell"
            and row
            and column in self._action_columns
        )
        self.menu_tree.configure(cursor="hand2" if over_action else "")

    def handle_table_click(self, event):
        if self.menu_tree.identify_region(event.x, event.y) != "cell":
            return

        row_id = self.menu_tree.identify_row(event.y)
        if not row_id:
            return

        self.menu_tree.focus_set()
        self.menu_tree.selection_set(row_id)

        action = self._action_columns.get(
            self.menu_tree.identify_column(event.x)
        )
        item = self.menu_items.get(row_id)

        if not action or not item:
            return

        # Defer so the click finishes before a modal window grabs input.
        if action == "edit":
            self.after(20, lambda: self.open_edit_item_dialog(item))
        else:
            self.after(20, lambda: self.confirm_delete(item))

    def handle_double_click(self, event):
        if self.menu_tree.identify_region(event.x, event.y) != "cell":
            return

        # Action cells already handle single clicks.
        if self.menu_tree.identify_column(event.x) in self._action_columns:
            return

        item = self.menu_items.get(self.menu_tree.identify_row(event.y))
        if item:
            self.open_edit_item_dialog(item)

    def edit_selected(self):
        item = self.selected_item()
        if item:
            self.open_edit_item_dialog(item)

    def delete_selected(self):
        item = self.selected_item()
        if item:
            self.confirm_delete(item)

    # =========================================================
    # Dialog management
    # =========================================================

    def _open_dialog(self, factory):
        """Open one modal at a time; refocus it if already open."""
        dialog = self._active_dialog

        if dialog is not None:
            try:
                if dialog.winfo_exists():
                    dialog.lift()
                    dialog.focus_force()
                    return
            except tk.TclError:
                pass

        self._active_dialog = factory()

    def open_add_item_dialog(self):
        self._open_dialog(
            lambda: ItemDialog(
                self,
                None,
                self.categories(),
                self.submit_item,
            )
        )

    def open_edit_item_dialog(self, item):
        self._open_dialog(
            lambda: ItemDialog(
                self,
                item,
                self.categories(),
                self.submit_item,
            )
        )

    # =========================================================
    # Validation + save
    # =========================================================

    def _validate_item_fields(self, name, category, price_text):
        """Normalize and validate menu item fields."""
        name = " ".join(name.split())
        category = " ".join(category.split())
        price_text = price_text.replace("₹", "").replace(",", "").strip()

        if not name:
            return None, None, ("name", "Item name is required.")

        if len(name) > MAX_NAME_LENGTH:
            return None, None, (
                "name",
                f"Item name must be {MAX_NAME_LENGTH} characters or fewer.",
            )

        if not category:
            return None, None, ("category", "Category is required.")

        if len(category) > MAX_CATEGORY_LENGTH:
            return None, None, (
                "category",
                f"Category must be {MAX_CATEGORY_LENGTH} characters or fewer.",
            )

        if not price_text:
            return None, None, ("price", "Price is required.")

        try:
            price = Decimal(price_text)
        except InvalidOperation:
            return None, None, ("price", "Price must be a valid number.")

        if not price.is_finite():
            return None, None, ("price", "Price must be a valid number.")

        if price <= 0:
            return None, None, ("price", "Price must be greater than zero.")

        if price > MAX_PRICE:
            return None, None, (
                "price",
                f"Price cannot exceed ₹{MAX_PRICE:,.0f}.",
            )

        if price.as_tuple().exponent < -2:
            return None, None, (
                "price",
                "Price can have at most two decimal places.",
            )

        return name, category, (None, price)


    def submit_item(self, name, category, price_text, available, existing):
        """Validate and save a menu item."""
        name, category, validation = self._validate_item_fields(
            name, category, price_text
        )

        if validation[0] is not None:
            return validation

        price = validation[1]

        # Reuse the spelling of an existing category to avoid near-duplicates.
        for known in self.categories():
            if known.lower() == category.lower():
                category = known
                break

        existing_id = existing.id if existing else None

        for other in self.all_items:
            if (
                other.id != existing_id
                and other.name.lower() == name.lower()
                and other.category.lower() == category.lower()
            ):
                return "name", f"“{name}” already exists in {category}."

        try:
            if existing:
                update_menu_item(
                    existing.id,
                    name,
                    category,
                    float(price),
                    available,
                )
            else:
                add_menu_item(
                    name,
                    category,
                    float(price),
                    available,
                )
        except sqlite3.IntegrityError:
            return "name", "An item with these details already exists."
        except sqlite3.Error:
            return (
                None,
                "The item could not be saved because of a database error.",
            )

        if not existing:
            self._select_after_load = (name.lower(), category.lower())

        self.load_menu_items()
        return None

    # =========================================================
    # Availability toggle
    # =========================================================

    def set_availability(self, item, available):
        try:
            update_menu_item(
                item.id,
                item.name,
                item.category,
                item.price,
                available,
            )
        except sqlite3.Error:
            messagebox.showerror(
                "Update Failed",
                "The item's availability could not be updated "
                "because of a database error.",
                parent=self.winfo_toplevel(),
            )
            return

        self.load_menu_items()

    # =========================================================
    # Delete
    # =========================================================

    def confirm_delete(self, item):
        self._open_dialog(
            lambda: ConfirmDialog(
                self,
                title="Delete Menu Item",
                heading="Delete this item?",
                message=(
                    f"“{item.name}” will be permanently removed from the "
                    "menu. This action cannot be undone."
                ),
                confirm_text="Delete",
                on_confirm=lambda: self.delete_item(item),
            )
        )

    def delete_item(self, item):
        parent = self.winfo_toplevel()

        try:
            delete_menu_item(item.id)

        except sqlite3.IntegrityError:
            # The item is referenced by past orders. Offer the safe
            # alternative instead of leaving the user at a dead end.
            if item.available and messagebox.askyesno(
                "Cannot Delete Item",
                f"“{item.name}” is used in existing orders and cannot be "
                "deleted.\n\nMark it as unavailable instead so it no longer "
                "appears for new orders?",
                parent=parent,
            ):
                self.set_availability(item, False)
            elif not item.available:
                messagebox.showinfo(
                    "Cannot Delete Item",
                    f"“{item.name}” is used in existing orders and cannot be "
                    "deleted. It is already marked as unavailable.",
                    parent=parent,
                )
            return

        except sqlite3.Error:
            messagebox.showerror(
                "Delete Failed",
                "The menu item could not be deleted because of a "
                "database error.",
                parent=parent,
            )
            return

        self.load_menu_items()
