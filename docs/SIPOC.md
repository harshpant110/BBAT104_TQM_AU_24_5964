# SIPOC — Restaurant Billing System

## Process boundary
From maintaining menu/customer information through order creation and bill completion.

| Suppliers | Inputs | High-level process | Outputs | Customers |
|---|---|---|---|---|
| Restaurant staff | Menu items and prices | Maintain menu | Current menu records | Staff and customers |
| Restaurant staff | Customer details | Create or update customer | Customer records | Restaurant staff |
| Staff / customer order | Selected items and quantities | Validate order | Validated order items | Billing operator |
| Billing operator | Items, tax, discount, payment method | Calculate and complete bill | Completed order and bill totals | Customer and staff |
| Application database | Stored orders and payment data | Retrieve orders and reports | Order history and report metrics | Management |

## Assumptions and validation
This SIPOC is a high-level process model based on the inspected application scope.
Confirm the actual operational workflow with the project owner and SRS.
