# Restaurant Billing System — Project Scope

## 1. Project Overview

The Restaurant Billing System is a Python-based desktop application designed to support the core operational activities of a restaurant, including menu management, order processing, billing, payment handling, and customer management.

The project is developed as part of **BBAT104 — Fundamentals of TQM** with the assigned quality goal **Q03 — Improve Usability**.

The project combines functional software development with Total Quality Management (TQM) and Statistical Quality Control (SQC) practices to identify, analyze, and improve usability-related issues.

## 2. Core System Modules

### 2.1 Dashboard

The application will provide a central dashboard containing relevant restaurant information and quick access to major system functions.

Planned information includes:

* Today's sales
* Today's orders
* Total revenue
* Popular menu items
* Quick actions

The dashboard will also satisfy the **Dashboard Overview** requirement of Q03.

### 2.2 Menu Management

The Menu Management module will maintain the restaurant's menu.

Functions include:

* Menu categories
* Menu items
* Item prices
* Item availability
* Create menu item
* View menu items
* Update menu item
* Delete menu item

### 2.3 Order Management

The Order Management module will handle customer orders.

Functions include:

* Create orders
* Add menu items to an order
* Remove menu items
* Modify item quantities
* Manage order status
* View order history

### 2.4 Billing & Payments

The Billing & Payments module will calculate and record restaurant bills.

Functions include:

* Subtotal calculation
* Tax calculation
* Discount handling
* Final bill calculation
* Payment method selection
* Bill history

### 2.5 Customer Management

The Customer Management module will maintain customer information.

Functions include:

* Customer records
* Customer contact information
* Customer order history
* Create customer
* View customer
* Update customer
* Delete customer

### 2.6 Search & Filters

Search and filtering functionality will allow users to efficiently locate relevant information.

Planned capabilities include:

* Menu search
* Order search
* Customer search
* Date-based filtering
* Status-based filtering

Search and filtering will also contribute to the **Search Filters** requirement of Q03.

## 3. Q03 — Improve Usability

The project will implement all five suggested features assigned to Q03:

1. **Dark Mode**
2. **Custom Themes**
3. **Dashboard Overview**
4. **Search Filters**
5. **Calendar**

These features will be integrated into the core application rather than implemented as isolated demonstrations.

## 4. TQM and Quality Scope

The project will apply relevant TQM and SQC techniques throughout development, including:

* Critical to Quality (CTQ)
* SIPOC
* Failure Mode and Effects Analysis (FMEA)
* Risk Priority Number (RPN)
* Defect Logging
* Checksheets
* Pareto Analysis
* Fishbone/Ishikawa Analysis
* PDCA

Actual defects, test results, measurements, and quality evidence will be recorded based on the application's development and testing process.

## 5. Technology Scope

The planned technology stack is:

* Python 3.x
* Tkinter / CustomTkinter
* SQLite3
* Pandas where required
* Matplotlib / Seaborn where required
* Visual Studio Code
* GitHub

## 6. Out of Scope

The following are outside the current project scope:

* Online food ordering
* Online payment gateway integration
* Cloud deployment
* Multi-branch restaurant management
* Employee payroll management
* Inventory management
* Kubernetes, Docker, or microservices
* External cloud databases

These exclusions keep the project focused on the assigned Restaurant Billing System baseline and Q03 usability objective.

## 7. Scope Statement

The project will deliver a functional Python desktop Restaurant Billing System with core restaurant management and billing capabilities, enhanced through the five Q03 usability features and supported by documented TQM/SQC quality-improvement activities.
