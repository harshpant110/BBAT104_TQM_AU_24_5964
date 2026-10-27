from ui.pages.menu import MenuPage
from ui.pages.customers import CustomersPage
from ui.pages.orders import OrdersPage
from ui.pages.calendar import CalendarPage
from ui.pages.billing import BillingPage
from ui.pages.settings import SettingsPage

from database import (get_dashboard_stats, get_daily_revenue, get_orders, get_popular_items)

import customtkinter as ctk

from ui.theme import COLORS, DARK_COLORS, FONTS, SIZES
from datetime import date, timedelta


class RestaurantBillingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_mode = "dark"

        self.title("Restaurant Billing System")
        self.geometry("1280x800")
        self.minsize(1100, 700)

        self.setup_theme()
        self.create_layout()
        self.show_dashboard()

    def setup_theme(self):
        ctk.set_appearance_mode(self.current_mode)
        ctk.set_default_color_theme("blue")

    @property
    def colors(self):
        return DARK_COLORS if self.current_mode == "dark" else COLORS

    def create_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()

        self.main_area = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.colors["background"],
        )
        self.main_area.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        self.create_header()

        self.content_frame = ctk.CTkFrame(
            self.main_area,
            corner_radius=0,
            fg_color="transparent",
        )
        self.content_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=SIZES["padding"],
            pady=(0, SIZES["padding"]),
        )

        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=SIZES["sidebar_width"],
            corner_radius=0,
            fg_color=self.colors["sidebar"],
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        self.sidebar.grid_propagate(False)

        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
        )
        logo_frame.pack(
            fill="x",
            padx=22,
            pady=(28, 35),
        )

        logo = ctk.CTkLabel(
            logo_frame,
            text="RESTAURANT",
            font=ctk.CTkFont(
                family=FONTS["title"][0],
                size=20,
                weight="bold",
            ),
            text_color=self.colors["accent"],
        )
        logo.pack(anchor="w")

        logo_subtitle = ctk.CTkLabel(
            logo_frame,
            text="BILLING SYSTEM",
            font=ctk.CTkFont(
                family=FONTS["small"][0],
                size=11,
                weight="bold",
            ),
            text_color=self.colors["text_secondary"],
        )
        logo_subtitle.pack(anchor="w", pady=(2, 0))

        self.nav_buttons = {}

        navigation_items = [
            ("Dashboard", "▦"),
            ("Menu", "≡"),
            ("Orders", "▤"),
            ("Customers", "♙"),
            ("Billing", "₹"),
            ("Calendar", "□"),
        ]

        for name, icon in navigation_items:
            button = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}   {name}",
                height=44,
                corner_radius=SIZES["button_radius"],
                anchor="w",
                fg_color="transparent",
                hover_color=self.colors["sidebar_hover"],
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(
                    family=FONTS["body"][0],
                    size=13,
                ),
                command=lambda page=name: self.show_page(page),
            )
            button.pack(
                fill="x",
                padx=14,
                pady=3,
            )

            self.nav_buttons[name] = button

        settings_button = ctk.CTkButton(
            self.sidebar,
            text="  ⚙   Settings",
            height=44,
            corner_radius=SIZES["button_radius"],
            anchor="w",
            fg_color="transparent",
            hover_color=self.colors["sidebar_hover"],
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(
                family=FONTS["body"][0],
                size=13,
            ),
            command=lambda: self.show_page("Settings"),
        )
        settings_button.pack(
            side="bottom",
            fill="x",
            padx=14,
            pady=(3, 14),
        )

        self.theme_switch = ctk.CTkSwitch(
            self.sidebar,
            text="Dark Mode",
            font=ctk.CTkFont(
                family=FONTS["small"][0],
                size=12,
            ),
            text_color=self.colors["text_secondary"],
            command=self.toggle_theme,
        )
        self.theme_switch.pack(
            side="bottom",
            padx=20,
            pady=(10, 10),
            anchor="w",
        )
        self.theme_switch.select()

    def create_header(self):
        self.header = ctk.CTkFrame(
            self.main_area,
            height=SIZES["header_height"],
            corner_radius=16,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"],
        )
        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(20, 15),
        )
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(0, weight=1)

        self.page_title = ctk.CTkLabel(
            self.header,
            text="Dashboard",
            font=ctk.CTkFont(
                family=FONTS["heading"][0],
                size=20,
                weight="bold",
            ),
            text_color=self.colors["text_primary"],
        )
        self.page_title.grid(
            row=0,
            column=0,
            padx=25,
            pady=20,
            sticky="w",
        )

        self.user_label = ctk.CTkLabel(
            self.header,
            text="Administrator",
            font=ctk.CTkFont(
                family=FONTS["body"][0],
                size=13,
            ),
            text_color=self.colors["text_secondary"],
        )
        self.user_label.grid(
            row=0,
            column=1,
            padx=25,
            pady=20,
        )

    def show_dashboard(self):
        self.show_page("Dashboard")

    def show_page(self, page_name):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.page_title.configure(text=page_name)

        for name, button in self.nav_buttons.items():
            if name == page_name:
                button.configure(
                    fg_color=self.colors["accent"],
                    text_color="#FFFFFF",
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=self.colors["text_secondary"],
                )

        if page_name == "Dashboard":
            self.create_dashboard()
        elif page_name == "Menu":
            menu_page = MenuPage(self.content_frame, self.colors)
            menu_page.pack(fill="both", expand=True)
        elif page_name == "Customers":
            customers_page = CustomersPage(self.content_frame, self.colors)
            customers_page.pack(fill="both", expand=True)
        elif page_name == "Orders":
            orders_page = OrdersPage(self.content_frame, self.colors)
            orders_page.pack(fill="both", expand=True)
        elif page_name == "Billing":
            billing_page = BillingPage(self.content_frame, self.colors)
            billing_page.pack(fill="both", expand=True)
        elif page_name == "Calendar":
            calendar_page = CalendarPage(self.content_frame, self.colors)
            calendar_page.pack(fill="both", expand=True)
        elif page_name == "Settings":
            settings_page = SettingsPage(
                self.content_frame,
                self.colors,
                self.current_mode,
                self.set_theme_mode,
            )
            settings_page.pack(fill="both", expand=True)
        else:
            self.create_placeholder(page_name)


    def create_dashboard(self):
        container = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            corner_radius=0,
        )
        container.pack(fill="both", expand=True)

        # Dashboard heading and quick actions
        top = ctk.CTkFrame(container, fg_color="transparent")
        top.pack(fill="x", pady=(4, 20))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top,
            text="Good evening, Administrator",
            font=ctk.CTkFont(
                family=FONTS["heading"][0], size=24, weight="bold"
            ),
            text_color=self.colors["text_primary"],
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            top,
            text="Your restaurant at a glance",
            font=ctk.CTkFont(family=FONTS["body"][0], size=12),
            text_color=self.colors["text_secondary"],
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        ctk.CTkButton(
            top,
            text="+ New Bill",
            width=112,
            height=38,
            fg_color=self.colors["success"],
            hover_color=self.colors["success"],
            command=lambda: self.show_page("Billing"),
        ).grid(row=0, column=1, rowspan=2, padx=(12, 0))

        ctk.CTkButton(
            top,
            text="Manage Menu",
            width=120,
            height=38,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            command=lambda: self.show_page("Menu"),
        ).grid(row=0, column=2, rowspan=2, padx=(8, 0))

        stats = get_dashboard_stats()

        # KPI cards use existing dashboard statistics.
        card_data = [
            ("COMPLETED REVENUE", f"₹{stats['completed_revenue']:,.2f}",
             "From completed orders", "#2F65E8"),
            ("TOTAL ORDERS", str(stats["total_orders"]),
             f"{stats['completed_orders']} completed", "#16A34A"),
            ("PENDING ORDERS", str(stats["pending_orders"]),
             "Awaiting completion", "#D97706"),
            ("CUSTOMERS", str(stats["customers"]),
             "Registered customers", "#8B5CF6"),
        ]

        cards = ctk.CTkFrame(container, fg_color="transparent")
        cards.pack(fill="x")
        for column in range(4):
            cards.grid_columnconfigure(column, weight=1, uniform="kpi")

        for column, (title, value, description, accent) in enumerate(card_data):
            card = ctk.CTkFrame(
                cards,
                fg_color=self.colors["surface"],
                corner_radius=14,
                border_width=1,
                border_color=self.colors["border"],
            )
            card.grid(
                row=0, column=column, sticky="nsew",
                padx=(0 if column == 0 else 6, 0 if column == 3 else 6),
                pady=2,
            )

            ctk.CTkFrame(
                card, height=4, fg_color=accent, corner_radius=2
            ).pack(fill="x", padx=15, pady=(14, 10))

            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(family=FONTS["small"][0], size=10, weight="bold"),
                text_color=self.colors["text_secondary"],
            ).pack(anchor="w", padx=15)

            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(family=FONTS["title"][0], size=23, weight="bold"),
                text_color=self.colors["text_primary"],
            ).pack(anchor="w", padx=15, pady=(5, 2))

            ctk.CTkLabel(
                card,
                text=description,
                font=ctk.CTkFont(family=FONTS["small"][0], size=10),
                text_color=self.colors["text_secondary"],
            ).pack(anchor="w", padx=15, pady=(0, 15))

        # Analytics row: real daily revenue and best-selling items.
        analytics = ctk.CTkFrame(container, fg_color="transparent")
        analytics.pack(fill="x", pady=(18, 0))
        analytics.grid_columnconfigure(0, weight=3, uniform="analytics")
        analytics.grid_columnconfigure(1, weight=2, uniform="analytics")

        revenue_card = ctk.CTkFrame(
            analytics,
            fg_color=self.colors["surface"],
            corner_radius=14,
            border_width=1,
            border_color=self.colors["border"],
        )
        revenue_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ctk.CTkLabel(
            revenue_card,
            text="Revenue Trend",
            font=ctk.CTkFont(family=FONTS["subheading"][0], size=15, weight="bold"),
            text_color=self.colors["text_primary"],
        ).pack(anchor="w", padx=18, pady=(16, 3))

        ctk.CTkLabel(
            revenue_card,
            text="Completed orders · Last 7 days",
            font=ctk.CTkFont(family=FONTS["small"][0], size=10),
            text_color=self.colors["text_secondary"],
        ).pack(anchor="w", padx=18, pady=(0, 12))

        revenue_rows = get_daily_revenue(days=7)
        revenue_by_day = {
            str(day): float(amount or 0)
            for day, amount in revenue_rows
        }

        today = date.today()
        revenue_values = [
            (
                (today - timedelta(days=offset)).isoformat(),
                revenue_by_day.get(
                    (today - timedelta(days=offset)).isoformat(),
                    0.0,
                ),
            )
            for offset in range(6, -1, -1)
        ]
        max_revenue = max((amount for _, amount in revenue_values), default=0)

        if not revenue_values or max_revenue <= 0:
            ctk.CTkLabel(
                revenue_card,
                text="No completed-order revenue recorded in this period.",
                font=ctk.CTkFont(family=FONTS["body"][0], size=12),
                text_color=self.colors["text_secondary"],
            ).pack(anchor="w", padx=18, pady=(8, 22))
        else:
            for day, amount in revenue_values:
                bar_row = ctk.CTkFrame(revenue_card, fg_color="transparent")
                bar_row.pack(fill="x", padx=18, pady=5)
                bar_row.grid_columnconfigure(1, weight=1)

                ctk.CTkLabel(
                    bar_row,
                    text=day[5:],
                    width=44,
                    anchor="w",
                    font=ctk.CTkFont(family=FONTS["small"][0], size=10),
                    text_color=self.colors["text_secondary"],
                ).grid(row=0, column=0, padx=(0, 8))

                bar = ctk.CTkProgressBar(
                    bar_row,
                    height=10,
                    corner_radius=5,
                    fg_color=self.colors["border"],
                    progress_color=self.colors["accent"],
                )
                bar.grid(row=0, column=1, sticky="ew", padx=(0, 10))
                bar.set(amount / max_revenue)

                ctk.CTkLabel(
                    bar_row,
                    text=f"₹{amount:,.0f}",
                    width=78,
                    anchor="e",
                    font=ctk.CTkFont(family=FONTS["small"][0], size=10),
                    text_color=self.colors["text_primary"],
                ).grid(row=0, column=2)

            ctk.CTkFrame(revenue_card, height=8, fg_color="transparent").pack()

        popular_card = ctk.CTkFrame(
            analytics,
            fg_color=self.colors["surface"],
            corner_radius=14,
            border_width=1,
            border_color=self.colors["border"],
        )
        popular_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        ctk.CTkLabel(
            popular_card,
            text="Popular Items",
            font=ctk.CTkFont(family=FONTS["subheading"][0], size=15, weight="bold"),
            text_color=self.colors["text_primary"],
        ).pack(anchor="w", padx=18, pady=(16, 12))

        popular = get_popular_items(limit=5)
        max_sold = max((int(quantity or 0) for _, quantity in popular), default=0)

        if not popular:
            ctk.CTkLabel(
                popular_card,
                text="No sales yet. Complete an order to see popular items.",
                wraplength=250,
                font=ctk.CTkFont(family=FONTS["body"][0], size=12),
                text_color=self.colors["text_secondary"],
            ).pack(anchor="w", padx=18, pady=(4, 20))
        else:
            for rank, (item_name, quantity_sold) in enumerate(popular, start=1):
                item_row = ctk.CTkFrame(popular_card, fg_color="transparent")
                item_row.pack(fill="x", padx=18, pady=5)
                item_row.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(
                    item_row,
                    text=f"{rank}. {item_name}",
                    font=ctk.CTkFont(family=FONTS["body"][0], size=12),
                    text_color=self.colors["text_primary"],
                    anchor="w",
                ).grid(row=0, column=0, sticky="w")

                ctk.CTkLabel(
                    item_row,
                    text=f"{quantity_sold} sold",
                    font=ctk.CTkFont(family=FONTS["small"][0], size=10),
                    text_color=self.colors["text_secondary"],
                ).grid(row=0, column=1, sticky="e")

                progress = ctk.CTkProgressBar(
                    popular_card,
                    height=7,
                    corner_radius=4,
                    fg_color=self.colors["border"],
                    progress_color=self.colors["accent"],
                )
                progress.pack(fill="x", padx=18, pady=(1, 5))
                progress.set((int(quantity_sold or 0) / max_sold) if max_sold else 0)

        # Recent orders retain the existing order query and record fields.
        recent_card = ctk.CTkFrame(
            container,
            fg_color=self.colors["surface"],
            corner_radius=14,
            border_width=1,
            border_color=self.colors["border"],
        )
        recent_card.pack(fill="x", pady=(18, 8))

        recent_header = ctk.CTkFrame(recent_card, fg_color="transparent")
        recent_header.pack(fill="x", padx=18, pady=(15, 8))
        recent_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            recent_header,
            text="Recent Orders",
            font=ctk.CTkFont(family=FONTS["subheading"][0], size=15, weight="bold"),
            text_color=self.colors["text_primary"],
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            recent_header,
            text="View Orders",
            width=95,
            height=30,
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["border"],
            text_color=self.colors["text_primary"],
            hover_color=self.colors["sidebar_hover"],
            command=lambda: self.show_page("Orders"),
        ).grid(row=0, column=1, sticky="e")

        table_head = ctk.CTkFrame(
            recent_card, fg_color=self.colors["sidebar_hover"], corner_radius=6
        )
        table_head.pack(fill="x", padx=12, pady=(0, 4))
        for column, weight in enumerate((1, 3, 1, 1)):
            table_head.grid_columnconfigure(column, weight=weight)

        for column, label in enumerate(("ORDER", "CUSTOMER / DATE", "STATUS", "TOTAL")):
            ctk.CTkLabel(
                table_head,
                text=label,
                font=ctk.CTkFont(family=FONTS["small"][0], size=10, weight="bold"),
                text_color=self.colors["text_secondary"],
                anchor="w" if column < 2 else "e",
            ).grid(
                row=0, column=column, sticky="ew",
                padx=10, pady=10,
            )

        orders = get_orders()[:5]
        if not orders:
            ctk.CTkLabel(
                recent_card,
                text="No orders yet. Create your first bill to get started.",
                font=ctk.CTkFont(family=FONTS["body"][0], size=12),
                text_color=self.colors["text_secondary"],
            ).pack(anchor="w", padx=20, pady=18)
        else:
            for index, order in enumerate(orders):
                (
                    order_id, _customer_id, customer_name, _subtotal,
                    _tax, _discount, total, _payment_method, status, created_at,
                ) = order

                row = ctk.CTkFrame(
                    recent_card,
                    fg_color="transparent" if index % 2 == 0 else self.colors["background"],
                    corner_radius=5,
                )
                row.pack(fill="x", padx=12, pady=2)
                for column, weight in enumerate((1, 3, 1, 1)):
                    row.grid_columnconfigure(column, weight=weight)

                values = (
                    f"#{order_id}",
                    f"{customer_name or 'Walk-in customer'}  ·  {created_at}",
                    status,
                    f"₹{total:,.2f}",
                )
                for column, value in enumerate(values):
                    status_color = (
                        self.colors["success"] if status == "Completed"
                        else self.colors["warning"] if status == "Pending"
                        else self.colors["text_secondary"]
                    ) if column == 2 else self.colors["text_primary"]

                    ctk.CTkLabel(
                        row,
                        text=str(value),
                        font=ctk.CTkFont(
                            family=FONTS["body"][0],
                            size=11,
                            weight="bold" if column in (0, 3) else "normal",
                        ),
                        text_color=status_color,
                        anchor="w" if column < 2 else "e",
                    ).grid(
                        row=0, column=column, sticky="ew",
                        padx=10, pady=11,
                    )

    def create_placeholder(self, page_name):
        card = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=self.colors["border"],
        )
        card.pack(
            fill="both",
            expand=True,
        )

        ctk.CTkLabel(
            card,
            text=f"{page_name} Module",
            font=ctk.CTkFont(
                family=FONTS["heading"][0],
                size=24,
                weight="bold",
            ),
            text_color=self.colors["text_primary"],
        ).pack(pady=(80, 10))

        ctk.CTkLabel(
            card,
            text="This module will be implemented in a later development step.",
            font=ctk.CTkFont(
                family=FONTS["body"][0],
                size=13,
            ),
            text_color=self.colors["text_secondary"],
        ).pack()

    def toggle_theme(self):
        self.set_theme_mode(
            "dark" if self.theme_switch.get() else "light"
        )

    def set_theme_mode(self, mode):
        if mode not in ("dark", "light"):
            return

        self.current_mode = mode
        if self.theme_switch.get() != (mode == "dark"):
            if mode == "dark":
                self.theme_switch.select()
            else:
                self.theme_switch.deselect()

        ctk.set_appearance_mode(self.current_mode)
        self.refresh_theme()

    def refresh_theme(self):
        colors = self.colors

        # Main areas
        self.sidebar.configure(
            fg_color=colors["sidebar"]
        )

        self.main_area.configure(
            fg_color=colors["background"]
        )

        self.header.configure(
            fg_color=colors["surface"]
        )

        self.content_frame.configure(
            fg_color="transparent"
        )

        # Header
        self.page_title.configure(
            text_color=colors["text_primary"]
        )

        self.user_label.configure(
            text_color=colors["text_secondary"]
        )

        # Navigation
        for name, button in self.nav_buttons.items():
            if name == self.page_title.cget("text"):
                button.configure(
                    fg_color=colors["accent"],
                    text_color="#FFFFFF",
                    hover_color=colors["accent_hover"]
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=colors["text_secondary"],
                    hover_color=colors["sidebar_hover"]
                )

        # Theme switch
        self.theme_switch.configure(
            text_color=colors["text_secondary"]
        )

        # Rebuild the current page so all cards and labels
        # receive the new theme colors immediately.
        current_page = self.page_title.cget("text")
        self.show_page(current_page)
