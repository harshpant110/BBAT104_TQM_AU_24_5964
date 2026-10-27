import re
import customtkinter as ctk
from tkinter import messagebox

from database import (
    get_customers,
    add_customer,
    update_customer,
    delete_customer,
)
from ui.theme import FONTS, SIZES

DATABASE_ERROR_TITLE = "Database Error"


class CustomersPage(ctk.CTkFrame):
    def __init__(self, master, colors):
        super().__init__(master, fg_color="transparent")
        self.colors = colors
        self.selected_customer = None

        self._build_ui()
        self.refresh_customers()

    def _build_ui(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 16))

        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Search customers by name, phone, or email...",
            placeholder_text_color=self.colors["text_secondary"],
            text_color=self.colors["text_primary"],
            height=38,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", lambda _event: self.refresh_customers())

        ctk.CTkButton(
            toolbar,
            text="+ Add Customer",
            height=38,
            command=self.clear_form,
        ).pack(side="right")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        self.table_card = ctk.CTkFrame(
            body,
            fg_color=self.colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=self.colors["border"],
        )
        self.table_card.pack(side="left", fill="both", expand=True, padx=(0, 12))

        ctk.CTkLabel(
            self.table_card,
            text="Customer Directory",
            font=ctk.CTkFont(family=FONTS["subheading"][0], size=16, weight="bold"),
            text_color=self.colors["text_primary"],
        ).pack(anchor="w", padx=16, pady=(16, 10))

        self.customer_list = ctk.CTkScrollableFrame(
            self.table_card,
            fg_color="transparent",
        )
        self.customer_list.pack(fill="both", expand=True, padx=10, pady=(0, 12))

        self.form_card = ctk.CTkFrame(
            body,
            fg_color=self.colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=self.colors["border"],
            width=290,
        )
        self.form_card.pack(side="right", fill="y")
        self.form_card.pack_propagate(False)

        ctk.CTkLabel(
            self.form_card,
            text="Customer Details",
            font=ctk.CTkFont(family=FONTS["subheading"][0], size=16, weight="bold"),
            text_color=self.colors["text_primary"],
        ).pack(anchor="w", padx=18, pady=(18, 16))

        self.name_entry = self._field("Full Name")
        self.phone_entry = self._field("Phone Number (optional)")
        self.email_entry = self._field("Email Address (optional)")

        self.save_button = ctk.CTkButton(
            self.form_card,
            text="Add Customer",
            height=38,
            command=self.save_customer,
        )
        self.save_button.pack(fill="x", padx=18, pady=(18, 8))

        ctk.CTkButton(
            self.form_card,
            text="Clear Form",
            height=34,
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["border"],
            text_color=self.colors["text_primary"],
            command=self.clear_form,
        ).pack(fill="x", padx=18, pady=4)

        ctk.CTkButton(
            self.form_card,
            text="Delete Selected",
            height=34,
            fg_color="#B42318",
            hover_color="#912018",
            command=self.remove_customer,
        ).pack(fill="x", padx=18, pady=(8, 18))

        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family=FONTS["small"][0], size=12),
            text_color=self.colors["text_secondary"],
        )
        self.status_label.pack(anchor="w", pady=(8, 0))

    def _field(self, placeholder):
        entry = ctk.CTkEntry(
            self.form_card,
            placeholder_text=placeholder,
            height=36,
        )
        entry.pack(fill="x", padx=18, pady=6)
        return entry

    def refresh_customers(self):
        for widget in self.customer_list.winfo_children():
            widget.destroy()

        try:
            customers = get_customers()
        except Exception as exc:
            messagebox.showerror(DATABASE_ERROR_TITLE, str(exc), parent=self)
            return

        query = self.search_entry.get().strip().casefold()
        filtered = [
            customer for customer in customers
            if query in " ".join(str(value or "") for value in customer).casefold()
        ]

        if not filtered:
            ctk.CTkLabel(
                self.customer_list,
                text="No customers found. Add your first customer.",
                text_color=self.colors["text_secondary"],
            ).pack(anchor="w", padx=8, pady=16)

        for customer in filtered:
            customer_id, name, phone, email = customer
            row = ctk.CTkFrame(
                self.customer_list,
                fg_color=self.colors["background"],
                corner_radius=8,
            )
            row.pack(fill="x", padx=3, pady=4)

            details = ctk.CTkFrame(row, fg_color="transparent")
            details.pack(side="left", fill="x", expand=True, padx=12, pady=10)

            ctk.CTkLabel(
                details,
                text=name,
                font=ctk.CTkFont(family=FONTS["body"][0], size=13, weight="bold"),
                text_color=self.colors["text_primary"],
            ).pack(anchor="w")

            ctk.CTkLabel(
                details,
                text=f"ID #{customer_id}  ·  {phone or 'No phone'}  ·  {email or 'No email'}",
                font=ctk.CTkFont(family=FONTS["small"][0], size=11),
                text_color=self.colors["text_secondary"],
                anchor="w",
                wraplength=330,
            ).pack(anchor="w", pady=(3, 0))

            ctk.CTkButton(
                row,
                text="Edit",
                width=60,
                height=30,
                command=lambda item=customer: self.select_customer(item),
            ).pack(side="right", padx=10, pady=10)

        self.status_label.configure(
            text=f"Showing {len(filtered)} of {len(customers)} customers"
        )

    def select_customer(self, customer):
        self.selected_customer = customer
        _, name, phone, email = customer

        for entry, value in (
            (self.name_entry, name),
            (self.phone_entry, phone or ""),
            (self.email_entry, email or ""),
        ):
            entry.delete(0, "end")
            entry.insert(0, value)

        self.save_button.configure(text="Save Changes")

    def clear_form(self):
        self.selected_customer = None
        for entry in (self.name_entry, self.phone_entry, self.email_entry):
            entry.delete(0, "end")
        self.save_button.configure(text="Add Customer")

    def save_customer(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()

        try:
            phone = phone.strip()
            email = email.strip()

            if phone:
                normalized_phone = re.sub(r"[\s()-]", "", phone)
                if normalized_phone.startswith("+91"):
                    normalized_phone = normalized_phone[3:]
                elif normalized_phone.startswith("91") and len(normalized_phone) == 12:
                    normalized_phone = normalized_phone[2:]

                if not re.fullmatch(r"[6-9]\d{9}", normalized_phone):
                    raise ValueError(
                        "Enter a valid 10-digit Indian mobile number, "
                        "optionally with the +91 country code."
                    )

            if email and not re.fullmatch(
                r"[A-Za-z0-9][\w.%+-]*@gmail\.com",
                email,
                re.IGNORECASE,
            ):
                raise ValueError(
                    "Enter a valid Gmail address ending in @gmail.com."
                )

            if self.selected_customer:
                updated = update_customer(
                    self.selected_customer[0], name, phone, email
                )
                if not updated:
                    messagebox.showwarning(
                        "Customer Not Found",
                        "This customer no longer exists.",
                        parent=self,
                    )
                    self.refresh_customers()
                    return
                message = "Customer updated successfully."
            else:
                add_customer(name, phone, email)
                message = "Customer added successfully."

            self.clear_form()
            self.refresh_customers()
            self.status_label.configure(text=message)

        except ValueError as exc:
            messagebox.showwarning("Check Customer Details", str(exc), parent=self)
        except Exception as exc:
            messagebox.showerror(DATABASE_ERROR_TITLE, str(exc), parent=self)

    def remove_customer(self):
        if not self.selected_customer:
            messagebox.showinfo(
                "Select Customer",
                "Click Edit beside a customer before deleting it.",
                parent=self,
            )
            return

        customer_id, name, *_ = self.selected_customer
        confirmed = messagebox.askyesno(
            "Delete Customer",
            f"Delete {name}?\n\nLinked order history will be retained.",
            parent=self,
        )
        if not confirmed:
            return

        try:
            deleted = delete_customer(customer_id)
            if deleted:
                self.clear_form()
                self.refresh_customers()
                self.status_label.configure(text="Customer deleted.")
            else:
                messagebox.showwarning(
                    "Customer Not Found",
                    "This customer no longer exists.",
                    parent=self,
                )
                self.refresh_customers()
        except ValueError as exc:
            messagebox.showwarning("Cannot Delete Customer", str(exc), parent=self)
        except Exception as exc:
            messagebox.showerror(DATABASE_ERROR_TITLE, str(exc), parent=self)
