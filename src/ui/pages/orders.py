import customtkinter as ctk
from tkinter import messagebox

from database import get_orders, get_order
from ui.theme import FONTS, SIZES


class OrdersPage(ctk.CTkFrame):
    def __init__(self, master, colors):
        super().__init__(master, fg_color="transparent")
        self.colors = colors
        self.orders = []

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 14))

        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Search by order ID or customer...",
            placeholder_text_color=colors["text_secondary"],
            height=38,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda _event: self.render_orders())

        self.status_filter = ctk.CTkOptionMenu(
            toolbar,
            values=["All", "Pending", "Completed"],
            command=lambda _value: self.render_orders(),
            height=38,
            width=140,
        )
        self.status_filter.set("All")
        self.status_filter.pack(side="right")

        self.card = ctk.CTkFrame(
            self,
            fg_color=colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=colors["border"],
        )
        self.card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.card,
            text="Order Directory",
            font=ctk.CTkFont(
                family=FONTS["subheading"][0],
                size=16,
                weight="bold",
            ),
            text_color=colors["text_primary"],
        ).pack(anchor="w", padx=18, pady=(18, 10))

        self.list_frame = ctk.CTkScrollableFrame(
            self.card,
            fg_color="transparent",
        )
        self.list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family=FONTS["small"][0], size=12),
            text_color=colors["text_secondary"],
        )
        self.status_label.pack(anchor="w", pady=(8, 0))

        self.refresh_orders()

    def refresh_orders(self):
        try:
            self.orders = get_orders()
        except Exception as exc:
            messagebox.showerror("Orders Error", str(exc), parent=self)
            return
        self.render_orders()

    def render_orders(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        query = self.search_entry.get().strip().casefold()
        selected_status = self.status_filter.get()
        filtered = []

        for order in self.orders:
            order_id = order[0]
            customer_name = order[2] or "Walk-in customer"
            status = order[8]

            if selected_status != "All" and status != selected_status:
                continue

            searchable = f"{order_id} {customer_name}".casefold()
            if query and query not in searchable:
                continue

            filtered.append(order)

        if not filtered:
            ctk.CTkLabel(
                self.list_frame,
                text="No matching orders found.",
                text_color=self.colors["text_secondary"],
            ).pack(anchor="w", padx=8, pady=18)

        for order in filtered:
            (
                order_id,
                _customer_id,
                customer_name,
                _subtotal,
                _tax,
                _discount,
                total,
                payment_method,
                status,
                created_at,
            ) = order

            row = ctk.CTkFrame(
                self.list_frame,
                fg_color=self.colors["background"],
                corner_radius=8,
            )
            row.pack(fill="x", padx=3, pady=4)

            details = ctk.CTkFrame(row, fg_color="transparent")
            details.pack(side="left", fill="x", expand=True, padx=12, pady=10)

            ctk.CTkLabel(
                details,
                text=f"Order #{order_id}  ·  {customer_name or 'Walk-in customer'}",
                font=ctk.CTkFont(
                    family=FONTS["body"][0],
                    size=13,
                    weight="bold",
                ),
                text_color=self.colors["text_primary"],
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                details,
                text=(
                    f"{created_at}  ·  {payment_method}  ·  "
                    f"{status}  ·  Total: ₹{float(total):,.2f}"
                ),
                font=ctk.CTkFont(family=FONTS["small"][0], size=11),
                text_color=self.colors["text_secondary"],
                anchor="w",
                wraplength=650,
            ).pack(anchor="w", pady=(4, 0))

            ctk.CTkButton(
                row,
                text="Details",
                width=76,
                height=30,
                command=lambda oid=order_id: self.show_details(oid),
            ).pack(side="right", padx=12, pady=10)

        self.status_label.configure(
            text=f"Showing {len(filtered)} of {len(self.orders)} orders"
        )

    def show_details(self, order_id):
        try:
            order = get_order(order_id)
        except Exception as exc:
            messagebox.showerror("Order Details Error", str(exc), parent=self)
            return

        if not order:
            messagebox.showwarning(
                "Order Not Found",
                "This order no longer exists.",
                parent=self,
            )
            self.refresh_orders()
            return

        window = ctk.CTkToplevel(self)
        window.title(f"Order #{order_id} Details")
        window.geometry("520x520")
        window.minsize(440, 360)
        window.transient(self.winfo_toplevel())
        window.grab_set()

        ctk.CTkLabel(
            window,
            text=f"Order #{order_id}",
            font=ctk.CTkFont(
                family=FONTS["heading"][0],
                size=20,
                weight="bold",
            ),
            text_color=self.colors["text_primary"],
        ).pack(anchor="w", padx=22, pady=(22, 12))

        content = ctk.CTkScrollableFrame(window, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        if isinstance(order, dict):
            lines = [f"{key.replace('_', ' ').title()}: {value}" for key, value in order.items()]
        elif hasattr(order, "keys"):
            lines = [f"{key.replace('_', ' ').title()}: {order[key]}" for key in order.keys()]
        else:
            lines = [str(value) for value in order]

        for line in lines:
            ctk.CTkLabel(
                content,
                text=line,
                text_color=self.colors["text_primary"],
                anchor="w",
                justify="left",
                wraplength=440,
            ).pack(fill="x", anchor="w", padx=6, pady=5)

        ctk.CTkButton(
            window,
            text="Close",
            command=window.destroy,
        ).pack(anchor="e", padx=22, pady=(0, 18))
