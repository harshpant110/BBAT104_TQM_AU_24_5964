from database import initialize_database
from ui.app import RestaurantBillingApp


def main():
    initialize_database()

    app = RestaurantBillingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
