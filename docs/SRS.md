# Software Requirements Specification (SRS)

## Restaurant Billing System

## 1. Introduction

### 1.1 Purpose

The Restaurant Billing System is a Python-based desktop application for managing basic restaurant operations such as menu items, customers, orders, billing, and payments.

The project focuses on the BBAT104 TQM quality goal **Q03 — Improve Usability** through:

- Dark Mode
- Custom Themes
- Dashboard Overview
- Search Filters
- Calendar

### 1.2 Intended Users

The main users are restaurant staff who manage menu items, customers, orders, and billing.

### 1.3 Project Scope

The system will provide a simple graphical interface for daily restaurant operations. Data will be stored locally using SQLite.

---

## 2. System Overview

### 2.1 Application Type

The system will be a standalone desktop application developed using Python.

### 2.2 Main Modules

The application will include:

- Menu Management
- Customer Management
- Order Management
- Billing and Payments
- Search and Filters
- Dashboard
- Q03 Usability Features

### 2.3 Technology

- Python 3.x
- Tkinter / CustomTkinter
- SQLite3
- Pandas where required
- Matplotlib / Seaborn where required
- VS Code
- Git and GitHub

### 2.4 Basic Requirements

The system should provide:

- Simple navigation between modules
- Clear information display
- Input validation
- Useful error messages
- Feedback after important operations
- Consistent interface design

---

## 3. Functional Requirements

### 3.1 Menu Management

The system shall allow staff to:

- Add, view, update, and delete menu items.
- Manage menu categories.
- Store item name, category, price, and availability.
- View the current availability of items.

### 3.2 Customer Management

The system shall allow staff to:

- Add, view, update, and delete customer records.
- Store basic customer contact information.
- View customer order history where applicable.

### 3.3 Order Management

The system shall allow staff to:

- Create new orders.
- Add and remove menu items.
- Change item quantities.
- Associate orders with customers.
- Calculate order subtotal.
- Maintain order status.
- View previous orders.

### 3.4 Billing and Payments

The system shall:

- Calculate the bill subtotal.
- Apply tax and discounts where applicable.
- Calculate the final amount.
- Record payment method.
- Store completed bills.
- Display bill history.

### 3.5 Search and Filters

The system shall allow users to:

- Search menu items.
- Search customers.
- Search orders.
- Filter records by date or status.
- Combine relevant search and filter options.

### 3.6 Dashboard Overview

The dashboard shall provide a quick view of restaurant activity, including:

- Today's sales
- Today's orders
- Total revenue
- Popular items
- Quick access to important functions

### 3.7 Dark Mode

The system shall allow users to switch between light and dark modes while keeping the interface readable and consistent.

### 3.8 Custom Themes

The system shall provide multiple predefined themes that can be applied across the application.

### 3.9 Calendar

The system shall provide a calendar interface for date selection and other relevant date-based activities.

### 3.10 Data Persistence

The system shall use SQLite to store:

- Menu data
- Customer data
- Orders
- Order items
- Billing information

### 3.11 Validation and Error Handling

The system shall:

- Validate important user inputs.
- Prevent incomplete or invalid data where applicable.
- Display clear error messages.
- Provide feedback after successful operations.
- Handle expected errors without unnecessarily closing the application.

---

## 4. Non-Functional Requirements

### 4.1 Usability

The application should be simple to understand and use. Navigation, labels, buttons, forms, and messages should remain consistent across modules.

The five Q03 features should improve the overall user experience.

### 4.2 Performance

Normal operations such as searching, loading records, creating orders, and generating bills should respond without unnecessary delay.

### 4.3 Reliability

The system should maintain correct and consistent data during normal operations and handle expected errors safely.

### 4.4 Maintainability

The application should use a modular structure with clear naming and organized source code so that individual components can be modified and tested easily.

### 4.5 Data Integrity

The system should validate important inputs and maintain consistency between menu, customer, order, and billing records.

---

## 5. Constraints and Assumptions

### 5.1 Constraints

The project is limited to a desktop-based Restaurant Billing System.

The following are outside the current scope:

- Online food ordering
- Online payment gateway
- Cloud deployment
- Multi-branch management
- Employee payroll
- Inventory management
- Microservices or distributed architecture

### 5.2 Assumptions

- The application will be operated by restaurant staff.
- Restaurant data will be stored locally.
- Users will provide required information during normal operations.
- The system will operate within the defined project scope.

---

## 6. Usability Verification

The five Q03 features will be tested as part of the application:

- Dark Mode
- Custom Themes
- Dashboard Overview
- Search Filters
- Calendar

Defects found during testing will be recorded and used as part of the project's TQM improvement process.