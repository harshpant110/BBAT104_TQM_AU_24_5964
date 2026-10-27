import customtkinter as ctk
from tkinter import messagebox

from database import (
    get_menu_items,
    get_customers,
    create_order,
    add_order_item,
    recalculate_order_totals,
    complete_order,
)
from ui.theme import FONTS, SIZES


class BillingPage(ctk.CTkFrame):
    """Create orders through a temporary cart and the existing database APIs."""

    def __init__(self, master, colors):
        super().__init__(master, fg_color="transparent")
        self.colors = colors
        self.menu_items = []
        self.customers = []
        self.cart = {}

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            toolbar,
            text="Create New Order",
            font=ctk.CTkFont(
                family=FONTS["heading"][0], size=22, weight="bold"
            ),
            text_color=colors["text_primary"],
        ).pack(side="left")

        ctk.CTkButton(
            toolbar,
            text="Refresh Menu",
            width=115,
            command=self.load_data,
        ).pack(side="right")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        self.left = ctk.CTkFrame(
            body,
            fg_color=colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=colors["border"],
        )
        self.left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.right = ctk.CTkFrame(
            body,
            fg_color=colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=colors["border"],
            width=330,
        )
        self.right.pack(side="right", fill="y")
        self.right.pack_propagate(False)

        ctk.CTkLabel(
            self.left,
            text="Available Menu Items",
            font=ctk.CTkFont(
                family=FONTS["subheading"][0], size=16, weight="bold"
            ),
            text_color=colors["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 8))

        self.search = ctk.CTkEntry(
            self.left,
            placeholder_text="Search menu items...",
            placeholder_text_color=colors["text_secondary"],
            height=36,
        )
        self.search.pack(fill="x", padx=16, pady=(0, 10))
        self.search.bind("<KeyRelease>", lambda _event: self.render_menu())

        self.menu_list = ctk.CTkScrollableFrame(
            self.left, fg_color="transparent"
        )
        self.menu_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        ctk.CTkLabel(
            self.right,
            text="Current Order",
            font=ctk.CTkFont(
                family=FONTS["subheading"][0], size=18, weight="bold"
            ),
            text_color=colors["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 10))

        ctk.CTkLabel(
            self.right, text="Customer",
            text_color=colors["text_secondary"],
        ).pack(anchor="w", padx=16)

        self.customer_menu = ctk.CTkOptionMenu(
            self.right,
            values=["Walk-in customer"],
            fg_color=colors["surface"],
            button_color=colors["border"],
            button_hover_color=colors["accent"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_fg_color=colors["surface"],
            dropdown_hover_color=colors["sidebar_hover"],
        )
        self.customer_menu.pack(fill="x", padx=16, pady=(4, 12))

        self.cart_list = ctk.CTkScrollableFrame(
            self.right, fg_color="transparent", height=180
        )
        self.cart_list.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        self.tax_entry = self._money_entry("Tax amount (₹)", "0")
        self.discount_entry = self._money_entry("Discount amount (₹)", "0")

        self.total_label = ctk.CTkLabel(
            self.right,
            text="Subtotal: ₹0.00\nTax: ₹0.00\nDiscount: ₹0.00\nTotal: ₹0.00",
            justify="left",
            anchor="w",
            font=ctk.CTkFont(family=FONTS["body"][0], size=13),
            text_color=colors["text_primary"],
        )
        self.total_label.pack(fill="x", padx=16, pady=(8, 10))

        ctk.CTkLabel(
            self.right, text="Payment Method",
            text_color=colors["text_secondary"],
        ).pack(anchor="w", padx=16)

        self.payment_menu = ctk.CTkOptionMenu(
            self.right,
            values=["Cash", "UPI", "Card"],
            fg_color=colors["surface"],
            button_color=colors["border"],
            button_hover_color=colors["accent"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_fg_color=colors["surface"],
            dropdown_hover_color=colors["sidebar_hover"],
        )
        self.payment_menu.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkButton(
            self.right,
            text="Place Order",
            height=42,
            command=self.place_order,
        ).pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkButton(
            self.right,
            text="Clear Cart",
            height=34,
            fg_color=colors["border"],
            hover_color=colors["sidebar_hover"],
            text_color=colors["text_primary"],
            command=self.clear_cart,
        ).pack(fill="x", padx=16, pady=(0, 16))

        self.load_data()

    def _money_entry(self, label, default):
        ctk.CTkLabel(
            self.right, text=label, text_color=self.colors["text_secondary"]
        ).pack(anchor="w", padx=16)
        entry = ctk.CTkEntry(self.right, height=32)
        entry.pack(fill="x", padx=16, pady=(3, 8))
        entry.insert(0, default)
        entry.bind("<KeyRelease>", lambda _event: self.update_totals())
        return entry

    def load_data(self):
        try:
            self.menu_items = list(get_menu_items())
            self.customers = list(get_customers())
        except Exception as exc:
            messagebox.showerror("Billing Error", str(exc), parent=self)
            return

        self.customer_lookup = {"Walk-in customer": None}
        for customer in self.customers:
            label = f"{customer[1]} (#{customer[0]})"
            self.customer_lookup[label] = customer[0]

        current = self.customer_menu.get()
        options = list(self.customer_lookup)
        self.customer_menu.configure(values=options)
        self.customer_menu.set(current if current in options else options[0])
        self.render_menu()

    def render_menu(self):
        for widget in self.menu_list.winfo_children():
            widget.destroy()

        query = self.search.get().strip().casefold()
        available = [
            item for item in self.menu_items
            if bool(item[4])
            and query in f"{item[1]} {item[2]}".casefold()
        ]

        if not available:
            ctk.CTkLabel(
                self.menu_list,
                text="No available menu items match your search.",
                text_color=self.colors["text_secondary"],
            ).pack(anchor="w", padx=8, pady=16)
            return

        for item in available:
            item_id, name, category, price, _available = item
            row = ctk.CTkFrame(
                self.menu_list,
                fg_color=self.colors["background"],
                corner_radius=8,
            )
            row.pack(fill="x", padx=3, pady=4)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=10, pady=8)

            ctk.CTkLabel(
                info,
                text=name,
                font=ctk.CTkFont(
                    family=FONTS["body"][0], size=13, weight="bold"
                ),
                text_color=self.colors["text_primary"],
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=f"{category} · ₹{float(price):,.2f}",
                text_color=self.colors["text_secondary"],
                anchor="w",
            ).pack(anchor="w", pady=(2, 0))

            ctk.CTkButton(
                row,
                text="Add",
                width=65,
                height=30,
                command=lambda data=item: self.add_to_cart(data),
            ).pack(side="right", padx=10, pady=8)

    def add_to_cart(self, item):
        item_id, name, category, price, available = item
        if not bool(available):
            messagebox.showwarning(
                "Unavailable", f"{name} is currently unavailable.", parent=self
            )
            return

        if item_id in self.cart:
            self.cart[item_id]["quantity"] += 1
        else:
            self.cart[item_id] = {
                "id": item_id,
                "name": name,
                "price": float(price),
                "quantity": 1,
            }
        self.render_cart()

    def change_quantity(self, item_id, delta):
        if item_id not in self.cart:
            return
        new_quantity = self.cart[item_id]["quantity"] + delta
        if new_quantity <= 0:
            del self.cart[item_id]
        else:
            self.cart[item_id]["quantity"] = new_quantity
        self.render_cart()

    def render_cart(self):
        for widget in self.cart_list.winfo_children():
            widget.destroy()

        if not self.cart:
            ctk.CTkLabel(
                self.cart_list,
                text="Your cart is empty.\nAdd items from the menu.",
                text_color=self.colors["text_secondary"],
                justify="left",
            ).pack(anchor="w", padx=8, pady=12)
        else:
            for item_id, item in self.cart.items():
                row = ctk.CTkFrame(
                    self.cart_list,
                    fg_color=self.colors["background"],
                    corner_radius=7,
                )
                row.pack(fill="x", padx=2, pady=3)

                ctk.CTkLabel(
                    row,
                    text=(
                        f"{item['name']}\n₹{item['price']:,.2f} × "
                        f"{item['quantity']} = "
                        f"₹{item['price'] * item['quantity']:,.2f}"
                    ),
                    text_color=self.colors["text_primary"],
                    justify="left",
                    anchor="w",
                ).pack(side="left", fill="x", expand=True, padx=8, pady=7)

                controls = ctk.CTkFrame(row, fg_color="transparent")
                controls.pack(side="right", padx=4)

                ctk.CTkButton(
                    controls, text="−", width=26, height=26,
                    command=lambda iid=item_id: self.change_quantity(iid, -1),
                ).pack(pady=2)
                ctk.CTkButton(
                    controls, text="+", width=26, height=26,
                    command=lambda iid=item_id: self.change_quantity(iid, 1),
                ).pack(pady=2)

        self.update_totals()

    def update_totals(self):
        subtotal = sum(
            item["price"] * item["quantity"] for item in self.cart.values()
        )
        try:
            tax = float(self.tax_entry.get() or 0)
            discount = float(self.discount_entry.get() or 0)
            if tax < 0 or discount < 0:
                raise ValueError
        except ValueError:
            self.total_label.configure(
                text="Enter valid non-negative tax and discount amounts."
            )
            return

        total = subtotal + tax - discount
        if total < 0:
            self.total_label.configure(
                text="Discount cannot exceed subtotal plus tax."
            )
            return

        self.total_label.configure(
            text=(
                f"Subtotal: ₹{subtotal:,.2f}\n"
                f"Tax: ₹{tax:,.2f}\n"
                f"Discount: ₹{discount:,.2f}\n"
                f"Total: ₹{total:,.2f}"
            )
        )

    def clear_cart(self):
        self.cart.clear()
        self.render_cart()

    def place_order(self):
        if not self.cart:
            messagebox.showwarning(
                "Empty Cart", "Add at least one item before placing an order.",
                parent=self,
            )
            return

        try:
            tax = float(self.tax_entry.get() or 0)
            discount = float(self.discount_entry.get() or 0)
            if tax < 0 or discount < 0:
                raise ValueError("Tax and discount must be non-negative.")
        except ValueError:
            messagebox.showerror(
                "Invalid Amount", "Enter valid non-negative tax and discount amounts.",
                parent=self,
            )
            return

        subtotal = sum(
            item["price"] * item["quantity"] for item in self.cart.values()
        )
        if discount > subtotal + tax:
            messagebox.showerror(
                "Invalid Discount",
                "Discount cannot exceed subtotal plus tax.",
                parent=self,
            )
            return

        customer_id = self.customer_lookup.get(self.customer_menu.get())
        payment_method = self.payment_menu.get()

        if not messagebox.askyesno(
            "Confirm Order",
            f"Place this order for ₹{subtotal + tax - discount:,.2f}?",
            parent=self,
        ):
            return

        order_id = None
        try:
            order_id = create_order(customer_id)
            for item in self.cart.values():
                add_order_item(order_id, item["id"], item["quantity"])
            recalculate_order_totals(order_id, tax=tax, discount=discount)
            complete_order(order_id, payment_method)
        except Exception as exc:
            messagebox.showerror(
                "Could Not Complete Order",
                f"{exc}\n\nThe order may remain pending if an earlier step succeeded.",
                parent=self,
            )
            return

        messagebox.showinfo(
            "Order Placed",
            f"Order #{order_id} completed successfully.",
            parent=self,
        )
        self.clear_cart()
        self.tax_entry.delete(0, "end")
        self.tax_entry.insert(0, "0")
        self.discount_entry.delete(0, "end")
        self.discount_entry.insert(0, "0")
        self.update_totals()
        self.event_generate("<<OrderPlaced>>", when="tail")
