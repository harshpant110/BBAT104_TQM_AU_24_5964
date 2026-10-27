import calendar
from collections import defaultdict
from datetime import date, datetime
from tkinter import messagebox

import customtkinter as ctk

from database import get_orders
from ui.theme import FONTS, SIZES


class CalendarPage(ctk.CTkFrame):
    """Monthly order calendar with a selected-day order list."""

    def __init__(self, master, colors):
        super().__init__(master, fg_color="transparent")
        self.colors = colors
        self.today = date.today()
        self.display_year = self.today.year
        self.display_month = self.today.month
        self.selected_date = self.today
        self.orders = []
        self.orders_by_date = defaultdict(list)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            header,
            text="Order Calendar",
            font=ctk.CTkFont(
                family=FONTS["heading"][0], size=22, weight="bold"
            ),
            text_color=colors["text_primary"],
        ).pack(side="left")

        ctk.CTkButton(
            header, text="Refresh", width=90, command=self.load_orders
        ).pack(side="right")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        self.calendar_panel = ctk.CTkFrame(
            body,
            fg_color=colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=colors["border"],
        )
        self.calendar_panel.pack(
            side="left", fill="both", expand=True, padx=(0, 10)
        )

        self.details_panel = ctk.CTkFrame(
            body,
            fg_color=colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=colors["border"],
            width=320,
        )
        self.details_panel.pack(side="right", fill="y")
        self.details_panel.pack_propagate(False)

        navigation = ctk.CTkFrame(
            self.calendar_panel, fg_color="transparent"
        )
        navigation.pack(fill="x", padx=14, pady=(14, 10))

        ctk.CTkButton(
            navigation, text="‹", width=38,
            command=lambda: self.change_month(-1),
        ).pack(side="left")

        self.month_label = ctk.CTkLabel(
            navigation,
            text="",
            font=ctk.CTkFont(
                family=FONTS["subheading"][0], size=18, weight="bold"
            ),
            text_color=colors["text_primary"],
        )
        self.month_label.pack(side="left", expand=True)

        ctk.CTkButton(
            navigation, text="Today", width=65,
            command=self.go_to_today,
        ).pack(side="right")

        ctk.CTkButton(
            navigation, text="›", width=38,
            command=lambda: self.change_month(1),
        ).pack(side="right", padx=(0, 8))

        # Jump directly to a date without an additional dependency.
        self.date_search = ctk.CTkEntry(
            navigation,
            width=120,
            placeholder_text="YYYY-MM-DD",
        )
        self.date_search.pack(side="right", padx=(8, 5))
        self.date_search.bind("<Return>", self.search_date)

        ctk.CTkButton(
            navigation,
            text="Go",
            width=45,
            command=self.search_date,
        ).pack(side="right", padx=(0, 8))

        self.grid_frame = ctk.CTkFrame(
            self.calendar_panel, fg_color="transparent"
        )
        self.grid_frame.pack(
            fill="both", expand=True, padx=12, pady=(0, 14)
        )

        ctk.CTkLabel(
            self.details_panel,
            text="Orders for Selected Day",
            font=ctk.CTkFont(
                family=FONTS["subheading"][0], size=17, weight="bold"
            ),
            text_color=colors["text_primary"],
        ).pack(anchor="w", padx=15, pady=(16, 4))

        self.selected_label = ctk.CTkLabel(
            self.details_panel,
            text="",
            text_color=colors["text_secondary"],
        )
        self.selected_label.pack(anchor="w", padx=15, pady=(0, 8))

        self.day_summary = ctk.CTkLabel(
            self.details_panel,
            text="",
            justify="left",
            anchor="w",
            text_color=colors["text_primary"],
        )
        self.day_summary.pack(fill="x", padx=15, pady=(0, 8))

        self.details_list = ctk.CTkScrollableFrame(
            self.details_panel, fg_color="transparent"
        )
        self.details_list.pack(
            fill="both", expand=True, padx=8, pady=(0, 12)
        )

        self.load_orders()

    @staticmethod
    def parse_order_date(value):
        if not value:
            return None
        try:
            # Handles common SQLite timestamp formats.
            return datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            ).date()
        except (ValueError, TypeError):
            try:
                return datetime.strptime(
                    str(value)[:10], "%Y-%m-%d"
                ).date()
            except (ValueError, TypeError):
                return None

    def load_orders(self):
        try:
            self.orders = list(get_orders())
        except Exception as exc:
            messagebox.showerror(
                "Calendar Error", str(exc), parent=self
            )
            return

        self.orders_by_date.clear()
        for order in self.orders:
            # get_orders returns:
            # id, customer_id, customer_name, subtotal, tax, discount,
            # total, payment_method, status, created_at
            order_date = self.parse_order_date(order[9])
            if order_date is not None:
                self.orders_by_date[order_date].append(order)

        self.render_calendar()
        self.render_selected_day()

    def change_month(self, offset):
        month_index = self.display_year * 12 + self.display_month - 1 + offset
        self.display_year, zero_based_month = divmod(month_index, 12)
        self.display_month = zero_based_month + 1
        self.date_search.delete(0, "end")
        self.date_search.insert(0, self.selected_date.isoformat())
        self.render_calendar()

    def go_to_today(self):
        self.display_year = self.today.year
        self.display_month = self.today.month
        self.selected_date = self.today
        self.date_search.delete(0, "end")
        self.date_search.insert(0, self.today.isoformat())
        self.render_calendar()
        self.render_selected_day()

    def select_day(self, selected):
        self.selected_date = selected
        self.date_search.delete(0, "end")
        self.date_search.insert(0, selected.isoformat())
        self.render_calendar()
        self.render_selected_day()

    def search_date(self, event=None):
        value = self.date_search.get().strip()
        try:
            target = date.fromisoformat(value)
        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                "Enter a valid date in YYYY-MM-DD format, "
                "for example 2026-10-27.",
                parent=self,
            )
            return

        self.display_year = target.year
        self.display_month = target.month
        self.selected_date = target
        self.render_calendar()
        self.render_selected_day()

    def render_calendar(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.month_label.configure(
            text=f"{calendar.month_name[self.display_month]} "
                 f"{self.display_year}"
        )

        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Keep all seven weekday columns equal in width.
        for column in range(7):
            self.grid_frame.grid_columnconfigure(
                column, weight=1, uniform="calendar_columns", minsize=0
            )

        # Keep weekday headers and date rows aligned.
        self.grid_frame.grid_rowconfigure(0, weight=0, minsize=32)

        for column, weekday in enumerate(weekdays):
            ctk.CTkLabel(
                self.grid_frame,
                text=weekday,
                font=ctk.CTkFont(
                    family=FONTS["body"][0], size=12, weight="bold"
                ),
                text_color=self.colors["text_secondary"],
            ).grid(row=0, column=column, padx=2, pady=5, sticky="nsew")

        month_weeks = calendar.monthcalendar(
            self.display_year, self.display_month
        )

        # Give every week equal vertical space, including months with
        # four, five, or six calendar rows.
        for row_index in range(1, len(month_weeks) + 1):
            self.grid_frame.grid_rowconfigure(
                row_index, weight=1, uniform="calendar_rows", minsize=64
            )

        for row_index, week in enumerate(month_weeks, start=1):
            for column, day_number in enumerate(week):
                if day_number == 0:
                    ctk.CTkFrame(
                        self.grid_frame, fg_color="transparent"
                    ).grid(
                        row=row_index, column=column,
                        padx=2, pady=2, sticky="nsew",
                    )
                    continue

                selected = date(
                    self.display_year, self.display_month, day_number
                )
                day_orders = self.orders_by_date.get(selected, [])
                is_selected = selected == self.selected_date
                is_today = selected == self.today

                if is_selected:
                    background = self.colors["accent"]
                    foreground = "#FFFFFF"
                elif is_today:
                    background = self.colors["sidebar_hover"]
                    foreground = self.colors["text_primary"]
                else:
                    background = self.colors["background"]
                    foreground = self.colors["text_primary"]

                label = str(day_number)
                if day_orders:
                    label += f"\n{len(day_orders)} order"
                    if len(day_orders) != 1:
                        label += "s"

                ctk.CTkButton(
                    self.grid_frame,
                    text=label,
                    height=64,
                    corner_radius=8,
                    fg_color=background,
                    hover_color=self.colors["accent_hover"],
                    text_color=foreground,
                    border_width=1 if day_orders else 0,
                    border_color=self.colors["accent"],
                    font=ctk.CTkFont(
                        family=FONTS["body"][0], size=12
                    ),
                    command=lambda chosen=selected: self.select_day(chosen),
                ).grid(
                    row=row_index, column=column,
                    padx=2, pady=2, sticky="nsew",
                )

    def render_selected_day(self):
        selected = self.selected_date
        day_orders = self.orders_by_date.get(selected, [])

        self.selected_label.configure(
            text=selected.strftime("%A, %d %B %Y")
        )

        completed_total = sum(
            float(order[6] or 0)
            for order in day_orders
            if str(order[8]).casefold() == "completed"
        )
        self.day_summary.configure(
            text=(
                f"Orders: {len(day_orders)}\n"
                f"Completed revenue: ₹{completed_total:,.2f}"
            )
        )

        for widget in self.details_list.winfo_children():
            widget.destroy()

        if not day_orders:
            ctk.CTkLabel(
                self.details_list,
                text="No orders on this date.",
                text_color=self.colors["text_secondary"],
                justify="left",
            ).pack(anchor="w", padx=7, pady=10)
            return

        for order in day_orders:
            order_id = order[0]
            customer = order[2] or "Walk-in customer"
            total = float(order[6] or 0)
            payment = order[7] or "Not recorded"
            status = order[8] or "Unknown"

            card = ctk.CTkFrame(
                self.details_list,
                fg_color=self.colors["background"],
                corner_radius=8,
            )
            card.pack(fill="x", padx=3, pady=4)

            ctk.CTkLabel(
                card,
                text=f"Order #{order_id} · ₹{total:,.2f}",
                font=ctk.CTkFont(
                    family=FONTS["body"][0], size=13, weight="bold"
                ),
                text_color=self.colors["text_primary"],
                anchor="w",
            ).pack(fill="x", padx=9, pady=(8, 2))

            ctk.CTkLabel(
                card,
                text=f"{customer}\n{status} · {payment}",
                text_color=self.colors["text_secondary"],
                justify="left",
                anchor="w",
            ).pack(fill="x", padx=9, pady=(0, 8))
