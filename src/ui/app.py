from ui.pages.menu import MenuPage

import customtkinter as ctk

from ui.theme import COLORS, DARK_COLORS, FONTS, SIZES


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
            menu_page = MenuPage(
                self.content_frame,
                self.colors
            )
            menu_page.pack(
                fill="both",
                expand=True
            )
        else:
            self.create_placeholder(page_name)

    def create_dashboard(self):
        container = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
        )
        container.pack(
            fill="both",
            expand=True,
        )

        welcome = ctk.CTkLabel(
            container,
            text="Good evening, Administrator",
            font=ctk.CTkFont(
                family=FONTS["heading"][0],
                size=22,
                weight="bold",
            ),
            text_color=self.colors["text_primary"],
        )
        welcome.pack(anchor="w", pady=(5, 3))

        subtitle = ctk.CTkLabel(
            container,
            text="Here is an overview of your restaurant today.",
            font=ctk.CTkFont(
                family=FONTS["body"][0],
                size=13,
            ),
            text_color=self.colors["text_secondary"],
        )
        subtitle.pack(anchor="w", pady=(0, 25))

        cards_frame = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        cards_frame.pack(fill="x")

        cards = [
            ("Today's Revenue", "₹0.00", "No sales recorded"),
            ("Today's Orders", "0", "No orders yet"),
            ("Pending Orders", "0", "All caught up"),
            ("Customers", "0", "Registered customers"),
        ]

        for title, value, description in cards:
            card = ctk.CTkFrame(
                cards_frame,
                fg_color=self.colors["surface"],
                corner_radius=SIZES["card_radius"],
                border_width=1,
                border_color=self.colors["border"],
            )
            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(0, 12),
            )

            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(
                    family=FONTS["small"][0],
                    size=12,
                ),
                text_color=self.colors["text_secondary"],
            ).pack(anchor="w", padx=18, pady=(18, 5))

            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(
                    family=FONTS["title"][0],
                    size=24,
                    weight="bold",
                ),
                text_color=self.colors["text_primary"],
            ).pack(anchor="w", padx=18)

            ctk.CTkLabel(
                card,
                text=description,
                font=ctk.CTkFont(
                    family=FONTS["small"][0],
                    size=11,
                ),
                text_color=self.colors["text_secondary"],
            ).pack(anchor="w", padx=18, pady=(2, 18))

        lower_frame = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        lower_frame.pack(
            fill="both",
            expand=True,
            pady=(20, 0),
        )

        recent_orders = ctk.CTkFrame(
            lower_frame,
            fg_color=self.colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=self.colors["border"],
        )
        recent_orders.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10),
        )

        ctk.CTkLabel(
            recent_orders,
            text="Recent Orders",
            font=ctk.CTkFont(
                family=FONTS["subheading"][0],
                size=15,
                weight="bold",
            ),
            text_color=self.colors["text_primary"],
        ).pack(anchor="w", padx=20, pady=(20, 5))

        ctk.CTkLabel(
            recent_orders,
            text="Orders will appear here once billing is started.",
            font=ctk.CTkFont(
                family=FONTS["small"][0],
                size=12,
            ),
            text_color=self.colors["text_secondary"],
        ).pack(anchor="w", padx=20, pady=5)

        popular_items = ctk.CTkFrame(
            lower_frame,
            fg_color=self.colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=self.colors["border"],
        )
        popular_items.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0),
        )

        ctk.CTkLabel(
            popular_items,
            text="Popular Items",
            font=ctk.CTkFont(
                family=FONTS["subheading"][0],
                size=15,
                weight="bold",
            ),
            text_color=self.colors["text_primary"],
        ).pack(anchor="w", padx=20, pady=(20, 5))

        ctk.CTkLabel(
            popular_items,
            text="Popular menu items will appear here.",
            font=ctk.CTkFont(
                family=FONTS["small"][0],
                size=12,
            ),
            text_color=self.colors["text_secondary"],
        ).pack(anchor="w", padx=20, pady=5)

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
        self.current_mode = (
            "dark" if self.theme_switch.get() else "light"
        )

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
