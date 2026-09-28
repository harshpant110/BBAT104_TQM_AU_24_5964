# System Architecture

## 1. Architecture Overview

The Restaurant Billing System is a desktop-based application developed using Python. It follows a simple modular architecture where the graphical user interface handles user interaction, application modules handle restaurant operations, and SQLite is used for local data storage.

The main modules include Menu Management, Customer Management, Order Management, Billing and Payments, and Search and Filters.

The Q03 usability features are integrated into the application to improve the user experience. These features include Dark Mode, Custom Themes, Dashboard Overview, Search Filters, and Calendar.

## 2. System Components

The system will be divided into the following main components:

- **User Interface:** Provides the screens and controls used by restaurant staff.
- **Menu Management:** Handles menu categories, items, prices, and availability.
- **Customer Management:** Stores and manages customer information.
- **Order Management:** Handles creating orders and managing their items and status.
- **Billing and Payments:** Calculates bills and records payment details.
- **Search and Filters:** Helps users find menu, customer, and order records quickly.
- **Dashboard:** Shows important information such as sales, orders, and popular items.
- **SQLite Database:** Stores the application data locally.
- **Q03 Usability Features:** Provides Dark Mode, Custom Themes, Dashboard Overview, Search Filters, and Calendar.

## 3. Data Flow

The user interacts with the application through the graphical interface. Based on the selected operation, the request is passed to the relevant module.

For example, when creating an order, the user selects menu items and quantities. The order module processes this information and stores the required data in the database. The billing module then uses the order details to calculate the bill.

The basic flow is:

**User → Graphical Interface → Application Module → SQLite Database → Graphical Interface**

The database returns the required information to the application, which then displays the result to the user.

## 4. Technology Stack

The project will use the following technologies:

- **Python:** Main programming language.
- **Tkinter / CustomTkinter:** For the desktop user interface.
- **SQLite3:** For storing application data locally.
- **Pandas:** For data handling where required.
- **Matplotlib / Seaborn:** For charts and quality analysis where required.
- **Git and GitHub:** For version control and project management.
- **VS Code:** Main development environment.

## 5. Q03 Usability Layer

The Q03 features are included to make the application easier and more convenient to use.

The main usability improvements are:

- **Dark Mode:** Gives users an alternative interface appearance.
- **Custom Themes:** Allows users to choose from available themes.
- **Dashboard Overview:** Provides a quick view of important restaurant information.
- **Search Filters:** Helps users find required records faster.
- **Calendar:** Provides an easy way to select and work with dates.

These features are integrated into the main application interface rather than being separate systems.   