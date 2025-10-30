RoshTech Industries - Central CRM

1. Project Overview

This is the central Customer Relationship Management (CRM) platform for RoshTech Industries.

This system is designed to be the single source of truth for all business operations, managing client accounts, contacts, and sales opportunities. It is architected to be flexible and scalable, serving as the business foundation for all future divisions, including:

RoshTech Technologies (CPS #BONAZONKE)

RoshTech Logistics

RoshTech Properties

2. Technology Stack

Backend: Python 3, Flask

Database: SQLAlchemy, Flask-Migrate (using SQLite for development)

Authentication: Flask-Login for user session management

Frontend: HTML, Tailwind CSS, JavaScript

Templating: Jinja2

3. Project Setup

Follow these steps to set up and run the application locally.

1. Clone the Repository

# Replace with your new repository URL
git clone [https://github.com/SirMphuthi/roshtech-crm.git](https://github.com/SirMphuthi/roshtech-crm.git)
cd roshtech-crm


2. Create and Activate the Virtual Environment

This creates an isolated environment for your Python packages.

# 1. Create the environment (only do this once)
python3 -m venv venv

# 2. Activate the environment (do this every time you start work)
source venv/bin/activate


(Your terminal prompt should now show (venv))

3. Install Dependencies

This installs all the libraries listed in the requirements.txt file.

pip install -r requirements.txt


4. Configure the Environment

This tells Flask where to find your application.

export FLASK_APP=run.py


5. Create the Database (One-Time Setup)

These commands will create your database and all the tables based on the app/models.py file.

# 1. Initialize the migrations folder (only do this once)
flask db init

# 2. Create the first migration script
flask db migrate -m "Initial CRM database structure"

# 3. Apply the migration to create the database tables
flask db upgrade


(You should now see an app.db file in your project folder)

4. Running the Application

After the one-time setup is complete, you can run the application with this command:

python3 run.py


Your CRM will be running at http://127.0.0.1:5000.

© 2025 RoshTech Industries. All Rights Reserved.
