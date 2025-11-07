# 🏢 Hostel Management System (Flask/MySQL)

## Project Overview
A comprehensive web application for hostel operations, built with Flask, MySQL, and leveraging stored procedures and triggers for reliable data management. This system provides role-based access for students and administrators to manage rooms, fees, and visitors.

## Key Features

* **Role-Based Access:** Separate dashboards for Student and Admin (Warden).
* **Automated Allocation:** Uses a MySQL Stored Procedure (`HandleRoomAllocation`) to manage room transfers and status updates.
* **Capacity Validation:** Enforces room limits using a database **TRIGGER** before insertion.
* **Financial Tracking:** Calculates pending fees using a database **FUNCTION** (`CalculatePendingFees`).
* **Modular Design:** Uses Flask Blueprints for clean routing architecture.

## 🛠️ Setup and Installation

### Prerequisites
* Python 3.x
* MySQL 8.0+

### Step 1: Clone and Setup Environment
```bash
# Clone the repository (once you've pushed it to GitHub)
# git clone [YOUR GITHUB REPO URL]
# cd Hostel_Management_System

# Create and activate the virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Linux/macOS
# .\venv\Scripts\activate   # On Windows