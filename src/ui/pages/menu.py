import sqlite3
import tkinter as tk
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


class MenuPage(ctk.CTkFrame):
    def __init__(self, master, colors):
        super().__init__(
            master,
            fg_color="transparent"
        )

        self.colors = colors
        self.menu_items = {}

        self.create_header()
        self.create_menu_table()
        self.load_menu_items()

    # =========================================================
    # Header
    # =========================================================

    def create_header(self):
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            pady=(0, 20)
        )

        header_left = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        header_left.pack(
            side="left",
            fill="x",
            expand=True
        )

        ctk.CTkLabel(
            header_left,
            text="Menu Management",
            font=ctk.CTkFont(
                family=FONTS["heading"][0],
                size=22,
                weight="bold"
            ),
            text_color=self.colors["text_primary"]
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            header_left,
            text="Manage menu items, categories, prices and availability.",
            font=ctk.CTkFont(
                family=FONTS["body"][0],
                size=13
            ),
            text_color=self.colors["text_secondary"]
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        self.add_button = ctk.CTkButton(
            header,
            text="+  Add Menu Item",
            height=38,
            width=150,
            corner_radius=8,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                family=FONTS["body"][0],
                size=12,
                weight="bold"
            ),
            command=self.open_add_item_dialog
        )

        self.add_button.pack(
            side="right",
            padx=(15, 0)
        )

    # =========================================================
    # Menu Table
    # =========================================================

    def create_menu_table(self):
        self.table_card = ctk.CTkFrame(
            self,
            fg_color=self.colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=self.colors["border"]
        )

        self.table_card.pack(
            fill="both",
            expand=True
        )

        table_container = ctk.CTkFrame(
            self.table_card,
            fg_color="transparent"
        )

        table_container.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        # -----------------------------------------------------
        # Treeview style
        # -----------------------------------------------------

        self.tree_style = ttk.Style()

        try:
            self.tree_style.theme_use("clam")
        except tk.TclError:
            pass

        self.tree_style.layout(
            TREEVIEW_STYLE,
            [
                (
                    "Treeview.treearea",
                    {
                        "sticky": "nswe"
                    }
                )
            ]
        )

        self.tree_style.configure(
            TREEVIEW_STYLE,
            background=self.colors["surface"],
            foreground=self.colors["text_primary"],
            fieldbackground=self.colors["surface"],
            borderwidth=0,
            relief="flat",
            rowheight=60,
            font=(
                FONTS["body"][0],
                12
            )
        )

        self.tree_style.configure(
            f"{TREEVIEW_STYLE}.Heading",
            background=self.colors["background"],
            foreground=self.colors["text_primary"],
            borderwidth=0,
            relief="flat",
            padding=(14, 12),
            font=(
                FONTS["small"][0],
                12,
                "bold"
            )
        )

        self.tree_style.map(
            TREEVIEW_STYLE,
            background=[
                (
                    "selected",
                    self.colors["accent"]
                )
            ],
            foreground=[
                (
                    "selected",
                    "#FFFFFF"
                )
            ]
        )

        self.tree_style.map(
            f"{TREEVIEW_STYLE}.Heading",
            background=[
                (
                    "active",
                    self.colors["sidebar_hover"]
                )
            ]
        )

        # -----------------------------------------------------
        # Scrollbar style
        # -----------------------------------------------------

        self.tree_style.configure(
            SCROLLBAR_STYLE,
            background=self.colors["sidebar_hover"],
            troughcolor=self.colors["surface"],
            bordercolor=self.colors["surface"],
            arrowcolor=self.colors["text_secondary"],
            relief="flat",
            borderwidth=0
        )

        self.tree_style.map(
            SCROLLBAR_STYLE,
            background=[
                (
                    "active",
                    self.colors["accent"]
                ),
                (
                    "pressed",
                    self.colors["accent_hover"]
                )
            ]
        )

        # -----------------------------------------------------
        # Treeview
        # -----------------------------------------------------

        columns = (
            "number",
            "name",
            "category",
            "price",
            "status",
            "actions"
        )

        self.menu_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            style=TREEVIEW_STYLE,
            selectmode="browse",
            takefocus=False
        )

        # -----------------------------------------------------
        # Headings
        # -----------------------------------------------------

        self.menu_tree.heading(
            "number",
            text="No.",
            anchor="center"
        )

        self.menu_tree.heading(
            "name",
            text="Item Name",
            anchor="w"
        )

        self.menu_tree.heading(
            "category",
            text="Category",
            anchor="w"
        )

        self.menu_tree.heading(
            "price",
            text="Price",
            anchor="center"
        )

        self.menu_tree.heading(
            "status",
            text="Status",
            anchor="center"
        )

        self.menu_tree.heading(
            "actions",
            text="Actions",
            anchor="center"
        )

        # -----------------------------------------------------
        # Column widths
        # -----------------------------------------------------

        self.menu_tree.column(
            "number",
            width=65,
            minwidth=55,
            stretch=False,
            anchor="center"
        )

        self.menu_tree.column(
            "name",
            width=260,
            minwidth=180,
            stretch=True,
            anchor="w"
        )

        self.menu_tree.column(
            "category",
            width=190,
            minwidth=140,
            stretch=True,
            anchor="w"
        )

        self.menu_tree.column(
            "price",
            width=130,
            minwidth=110,
            stretch=True,
            anchor="center"
        )

        self.menu_tree.column(
            "status",
            width=150,
            minwidth=120,
            stretch=True,
            anchor="center"
        )

        self.menu_tree.column(
            "actions",
            width=210,
            minwidth=190,
            stretch=True,
            anchor="center"
        )

        # -----------------------------------------------------
        # Scrollbar
        # -----------------------------------------------------

        scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.menu_tree.yview,
            style=SCROLLBAR_STYLE
        )

        self.menu_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.menu_tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(6, 0)
        )

        table_container.grid_rowconfigure(
            0,
            weight=1
        )

        table_container.grid_columnconfigure(
            0,
            weight=1
        )

        # -----------------------------------------------------
        # Row styling
        # -----------------------------------------------------

        self.menu_tree.tag_configure(
            "row_even",
            background=self.colors["surface"],
            foreground=self.colors["text_primary"]
        )

        self.menu_tree.tag_configure(
            "row_odd",
            background=self.colors["background"],
            foreground=self.colors["text_primary"]
        )

        # -----------------------------------------------------
        # Mouse events
        # -----------------------------------------------------

        self.menu_tree.bind(
            "<Button-1>",
            self.handle_table_click
        )

        self.menu_tree.bind(
            "<Double-1>",
            self.handle_double_click
        )

    # =========================================================
    # Load menu items
    # =========================================================

    def load_menu_items(self):
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)

        self.menu_items.clear()

        items = get_menu_items()

        for display_number, item in enumerate(
            items,
            start=1
        ):
            _, name, category, price, available = item

            status_text = (
                "Available"
                if available
                else "Unavailable"
            )

            action_text = "Edit   |   Delete"

            row_tag = (
                "row_even"
                if display_number % 2 == 0
                else "row_odd"
            )

            tree_id = self.menu_tree.insert(
                "",
                "end",
                values=(
                    display_number,
                    name,
                    category,
                    f"₹{price:.2f}",
                    status_text,
                    action_text
                ),
                tags=(row_tag,)
            )

            self.menu_items[tree_id] = item

    # =========================================================
    # Table click handling
    # =========================================================

    def handle_table_click(self, event):
        row_id = self.menu_tree.identify_row(
            event.y
        )

        column_id = self.menu_tree.identify_column(
            event.x
        )

        if not row_id:
            return

        if column_id != "#6":
            return

        bbox = self.menu_tree.bbox(
            row_id,
            "#6"
        )

        if not bbox:
            return

        column_x = bbox[0]
        column_width = bbox[2]

        relative_x = event.x - column_x

        item = self.menu_items.get(
            row_id
        )

        if not item:
            return

        if relative_x < column_width / 2:
            self.open_edit_item_dialog(
                item
            )
        else:
            item_id = item[0]

            self.confirm_delete(
                item_id
            )

    def handle_double_click(self, event):
        row_id = self.menu_tree.identify_row(
            event.y
        )

        if not row_id:
            return

        item = self.menu_items.get(
            row_id
        )

        if item:
            self.open_edit_item_dialog(
                item
            )

    # =========================================================
    # Add item
    # =========================================================

    def open_add_item_dialog(self):
        dialog = self.create_item_dialog(
            "Add Menu Item"
        )

        self.create_item_form(
            dialog,
            item=None
        )

    # =========================================================
    # Edit item
    # =========================================================

    def open_edit_item_dialog(self, item):
        dialog = self.create_item_dialog(
            "Edit Menu Item"
        )

        self.create_item_form(
            dialog,
            item=item
        )

    # =========================================================
    # Create item dialog
    # =========================================================

    def create_item_dialog(self, title):
        dialog = ctk.CTkToplevel(
            self
        )

        dialog.title(
            title
        )

        dialog.geometry(
            "480x520"
        )

        dialog.resizable(
            False,
            False
        )

        dialog.transient(
            self.winfo_toplevel()
        )

        # Make sure the window exists and is visible
        # before applying the modal grab.
        dialog.update_idletasks()
        dialog.wait_visibility()

        dialog.grab_set()
        dialog.focus_force()

        return dialog

    # =========================================================
    # Item form
    # =========================================================

    def create_item_form(
        self,
        dialog,
        item=None
    ):
        container = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        ctk.CTkLabel(
            container,
            text=(
                "Add Menu Item"
                if item is None
                else "Edit Menu Item"
            ),
            font=ctk.CTkFont(
                family=FONTS["heading"][0],
                size=22,
                weight="bold"
            ),
            text_color=self.colors["text_primary"]
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            container,
            text=(
                "Add a new item to the restaurant menu."
                if item is None
                else "Update the selected menu item."
            ),
            font=ctk.CTkFont(
                family=FONTS["body"][0],
                size=13
            ),
            text_color=self.colors["text_secondary"]
        ).pack(
            anchor="w",
            pady=(4, 20)
        )

        name_entry = self.create_form_field(
            container,
            "Item Name",
            "e.g. Paneer Butter Masala"
        )

        category_entry = self.create_form_field(
            container,
            "Category",
            "e.g. Main Course"
        )

        price_entry = self.create_form_field(
            container,
            "Price (₹)",
            "e.g. 249.00"
        )

        availability = ctk.CTkCheckBox(
            container,
            text="Item is available",
            text_color=self.colors["text_primary"]
        )

        availability.pack(
            anchor="w",
            pady=(5, 15)
        )

        if item:
            _, name, category, price, available = item

            name_entry.insert(
                0,
                name
            )

            category_entry.insert(
                0,
                category
            )

            price_entry.insert(
                0,
                str(price)
            )

            if available:
                availability.select()
        else:
            availability.select()

        error_label = ctk.CTkLabel(
            container,
            text="",
            font=ctk.CTkFont(
                family=FONTS["small"][0],
                size=11
            ),
            text_color=self.colors["danger"]
        )

        error_label.pack(
            anchor="w",
            pady=(0, 10)
        )

        button_frame = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        button_frame.pack(
            side="bottom",
            fill="x"
        )

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
            command=dialog.destroy
        ).pack(
            side="right",
            padx=(10, 0)
        )

        ctk.CTkButton(
            button_frame,
            text=(
                "Save Changes"
                if item
                else "Save Item"
            ),
            height=38,
            width=115,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            text_color="#FFFFFF",
            command=lambda: self.save_item(
                dialog,
                name_entry,
                category_entry,
                price_entry,
                availability,
                error_label,
                item
            )
        ).pack(
            side="right"
        )

        name_entry.focus()

    def create_form_field(
        self,
        parent,
        label_text,
        placeholder
    ):
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(
                family=FONTS["body"][0],
                size=12,
                weight="bold"
            ),
            text_color=self.colors["text_primary"]
        ).pack(
            anchor="w"
        )

        entry = ctk.CTkEntry(
            parent,
            height=40,
            placeholder_text=placeholder
        )

        entry.pack(
            fill="x",
            pady=(6, 15)
        )

        return entry

    # =========================================================
    # Validation + save
    # =========================================================

    def save_item(
        self,
        dialog,
        name_entry,
        category_entry,
        price_entry,
        availability,
        error_label,
        existing_item
    ):
        name = name_entry.get().strip()
        category = category_entry.get().strip()
        price_text = price_entry.get().strip()
        available = bool(
            availability.get()
        )

        if not name:
            error_label.configure(
                text="Item name is required."
            )
            name_entry.focus()
            return

        if not category:
            error_label.configure(
                text="Category is required."
            )
            category_entry.focus()
            return

        if not price_text:
            error_label.configure(
                text="Price is required."
            )
            price_entry.focus()
            return

        try:
            price = float(
                price_text
            )
        except ValueError:
            error_label.configure(
                text="Price must be a valid number."
            )
            price_entry.focus()
            return

        if price <= 0:
            error_label.configure(
                text="Price must be greater than zero."
            )
            price_entry.focus()
            return

        if existing_item:
            item_id = existing_item[0]

            update_menu_item(
                item_id,
                name,
                category,
                price,
                available
            )
        else:
            add_menu_item(
                name,
                category,
                price,
                available
            )

        dialog.destroy()

        self.load_menu_items()

    # =========================================================
    # Delete confirmation
    # =========================================================

    def confirm_delete(self, item_id):
        dialog = ctk.CTkToplevel(
            self
        )

        dialog.title(
            "Delete Menu Item"
        )

        dialog.geometry(
            "400x220"
        )

        dialog.resizable(
            False,
            False
        )

        dialog.transient(
            self.winfo_toplevel()
        )

        dialog.update_idletasks()
        dialog.wait_visibility()

        dialog.grab_set()
        dialog.focus_force()

        container = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )

        ctk.CTkLabel(
            container,
            text="Delete Menu Item?",
            font=ctk.CTkFont(
                family=FONTS["heading"][0],
                size=20,
                weight="bold"
            ),
            text_color=self.colors["text_primary"]
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            container,
            text="This action cannot be undone.",
            font=ctk.CTkFont(
                family=FONTS["body"][0],
                size=13
            ),
            text_color=self.colors["text_secondary"]
        ).pack(
            anchor="w",
            pady=(8, 20)
        )

        button_frame = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        button_frame.pack(
            side="bottom",
            fill="x"
        )

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            height=36,
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["border"],
            text_color=self.colors["text_primary"],
            hover_color=self.colors["sidebar_hover"],
            command=dialog.destroy
        ).pack(
            side="right",
            padx=(10, 0)
        )

        ctk.CTkButton(
            button_frame,
            text="Delete",
            width=100,
            height=36,
            fg_color=self.colors["danger"],
            hover_color="#A93226",
            text_color="#FFFFFF",
            command=lambda: self.delete_item(
                item_id,
                dialog
            )
        ).pack(
            side="right"
        )

    # =========================================================
    # Delete item
    # =========================================================

    def delete_item(
        self,
        item_id,
        dialog
    ):
        try:
            delete_menu_item(
                item_id
            )

        except sqlite3.IntegrityError:
            dialog.destroy()

            messagebox.showerror(
                "Cannot Delete Item",
                (
                    "This menu item cannot be deleted "
                    "because it is used in an existing order."
                ),
                parent=self.winfo_toplevel()
            )

            return

        except sqlite3.Error:
            dialog.destroy()

            messagebox.showerror(
                "Delete Failed",
                (
                    "The menu item could not be deleted "
                    "because of a database error."
                ),
                parent=self.winfo_toplevel()
            )

            return

        dialog.destroy()

        self.load_menu_items()
