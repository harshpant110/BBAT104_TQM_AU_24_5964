import customtkinter as ctk

from ui.theme import FONTS, SIZES


class SettingsPage(ctk.CTkFrame):
    """Application appearance and information settings."""

    def __init__(self, master, colors, current_mode, on_mode_change):
        super().__init__(master, fg_color="transparent")
        self.colors = colors
        self.current_mode = current_mode
        self.on_mode_change = on_mode_change

        ctk.CTkLabel(
            self,
            text="Application Settings",
            font=ctk.CTkFont(
                family=FONTS["heading"][0], size=22, weight="bold"
            ),
            text_color=colors["text_primary"],
        ).pack(anchor="w", pady=(4, 4))

        ctk.CTkLabel(
            self,
            text="Personalize the appearance of your billing system.",
            font=ctk.CTkFont(
                family=FONTS["body"][0], size=13
            ),
            text_color=colors["text_secondary"],
        ).pack(anchor="w", pady=(0, 22))

        appearance = ctk.CTkFrame(
            self,
            fg_color=colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=colors["border"],
        )
        appearance.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            appearance,
            text="Appearance",
            font=ctk.CTkFont(
                family=FONTS["subheading"][0], size=16, weight="bold"
            ),
            text_color=colors["text_primary"],
        ).pack(anchor="w", padx=20, pady=(18, 6))

        ctk.CTkLabel(
            appearance,
            text="Choose the interface mode used throughout the application.",
            font=ctk.CTkFont(
                family=FONTS["body"][0], size=13
            ),
            text_color=colors["text_secondary"],
        ).pack(anchor="w", padx=20, pady=(0, 12))

        self.mode_switch = ctk.CTkSwitch(
            appearance,
            text="Dark mode",
            font=ctk.CTkFont(
                family=FONTS["body"][0], size=13
            ),
            text_color=colors["text_primary"],
            command=self.change_mode,
        )
        self.mode_switch.pack(anchor="w", padx=20, pady=(0, 20))

        if current_mode == "dark":
            self.mode_switch.select()

        preview = ctk.CTkFrame(
            self,
            fg_color=colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=colors["border"],
        )
        preview.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            preview,
            text="Current Theme",
            font=ctk.CTkFont(
                family=FONTS["subheading"][0], size=16, weight="bold"
            ),
            text_color=colors["text_primary"],
        ).pack(anchor="w", padx=20, pady=(18, 12))

        swatches = ctk.CTkFrame(preview, fg_color="transparent")
        swatches.pack(fill="x", padx=20, pady=(0, 18))

        for label, color in (
            ("Background", colors["background"]),
            ("Surface", colors["surface"]),
            ("Accent", colors["accent"]),
            ("Sidebar", colors["sidebar"]),
        ):
            item = ctk.CTkFrame(swatches, fg_color="transparent")
            item.pack(side="left", expand=True, fill="x", padx=(0, 10))

            ctk.CTkFrame(
                item,
                height=36,
                fg_color=color,
                corner_radius=6,
                border_width=1,
                border_color=colors["border"],
            ).pack(fill="x", pady=(0, 6))

            ctk.CTkLabel(
                item,
                text=label,
                font=ctk.CTkFont(
                    family=FONTS["small"][0], size=11
                ),
                text_color=colors["text_secondary"],
            ).pack(anchor="w")

        info = ctk.CTkFrame(
            self,
            fg_color=colors["surface"],
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=colors["border"],
        )
        info.pack(fill="x")

        ctk.CTkLabel(
            info,
            text="Application Information",
            font=ctk.CTkFont(
                family=FONTS["subheading"][0], size=16, weight="bold"
            ),
            text_color=colors["text_primary"],
        ).pack(anchor="w", padx=20, pady=(18, 10))

        for label, value in (
            ("Application", "Restaurant Billing System"),
            ("Database", "SQLite"),
            ("Appearance mode", current_mode.title()),
        ):
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=(0, 10))

            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(
                    family=FONTS["body"][0], size=13
                ),
                text_color=colors["text_secondary"],
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(
                    family=FONTS["body"][0], size=13, weight="bold"
                ),
                text_color=colors["text_primary"],
            ).pack(side="right")

        ctk.CTkLabel(
            info,
            text="Theme changes apply immediately and do not alter restaurant data.",
            font=ctk.CTkFont(
                family=FONTS["small"][0], size=11
            ),
            text_color=colors["text_secondary"],
        ).pack(anchor="w", padx=20, pady=(2, 18))

    def change_mode(self):
        self.on_mode_change("dark" if self.mode_switch.get() else "light")
