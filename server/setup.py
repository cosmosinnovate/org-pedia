# import os
# import platform
# import subprocess

# # Constants for environment variables
# ENV_VARS = {
#     "DATABASE_URL": "postgresql://postgres:postgres@localhost/org_pedia",
#     "JWT_SECRET_KEY": "super-secret-key-20124",
#     "SECRET_KEY": "super-secret-key-20124",
#     "FLASK_APP": "app.main",
# }

# # Determine the operating system
# OS_TYPE = platform.system()  # Returns 'Windows', 'Linux', or 'Darwin' (for macOS)

# def run_command(command, shell=False):
#     """Helper function to run shell commands."""
#     try:
#         subprocess.run(command, shell=shell, check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Error: {e}")
#         exit(1)

# # Step 1: Set up Python virtual environment
# def setup_virtual_environment():
#     print("Setting up Python virtual environment...")
#     if not os.path.exists("venv") and not os.path.exists(".venv"):
#         run_command(["python", "-m", "venv", "venv"])
#         print("Virtual environment created.")

#     # Activate the virtual environment
#     print("Activating virtual environment...")
#     if OS_TYPE == "Windows":
#         if os.path.exists("venv"):
#             activate_script = r"venv\Scripts\activate"
#         else:
#             activate_script = r".venv\Scripts\activate"
#     else:  # macOS/Linux
#         if os.path.exists("venv"):
#             activate_script = "source venv/bin/activate"
#         else:
#             activate_script = "source .venv/bin/activate"
    
#     # Activate the virtual environment in the current shell
#     activate_command = f"{activate_script} && python -m pip install --upgrade pip"
#     run_command(activate_command, shell=True)
#     print("Virtual environment activated.")

# # Step 2: Install dependencies
# def install_dependencies():
#     print("Installing dependencies from requirements.txt...")
#     run_command(["pip", "install", "-r", "requirements.txt"])
#     print("Dependencies installed.")

# # Step 3: Set environment variables
# def set_environment_variables():
#     print("Setting environment variables...")
#     for key, value in ENV_VARS.items():
#         if OS_TYPE == "Windows":
#             run_command(f"set {key}={value}", shell=True)
#         else:  # macOS/Linux
#             run_command(f"export {key}={value}", shell=True)
#     print("Environment variables set.")

# # Step 4: Check database connection
# def check_database_connection():
    
#     import psycopg2
#     from psycopg2 import OperationalError
#     print("Checking database connection...")
#     try:
#         conn = psycopg2.connect(ENV_VARS["DATABASE_URL"])
#         conn.close()
#         print("Database connection successful.")
#     except OperationalError as e:
#         print("Failed to connect to the database.")
#         print(e)
#         exit(1)

# # Step 5: Initialize and apply database migrations
# def setup_database():
#     print("Setting up database...")
#     run_command(["flask", "db", "init"])
#     run_command(["flask", "db", "migrate", "-m", "Initial migration"])
#     run_command(["flask", "db", "upgrade"])
#     print("Database setup complete.")

# # Step 6: Start the server
# def start_server():
#     print("Starting the server...")
#     run_command(["hypercorn", "app.main:app", "--reload"])

# if __name__ == "__main__":
#     print(f"Detected OS: {OS_TYPE}")
#     try:
#         set_environment_variables()
#         check_database_connection()
#         setup_database()
#         start_server()
#     except Exception as e:
#         print(f"An error occurred: {e}")
import os
from pdb import run
import platform
import subprocess
import psycopg2
from psycopg2 import OperationalError

# Constants for environment variables
ENV_VARS = {
    "DATABASE_URL": "postgresql://postgres:postgres@localhost/org_pedia",
    "JWT_SECRET_KEY": "super-secret-key-20124",
    "SECRET_KEY": "super-secret-key-20124",
    "FLASK_APP": "app.main",
}

# Determine the operating system
OS_TYPE = platform.system()  # Returns 'Windows', 'Linux', or 'Darwin' (for macOS)

def run_command(command, shell=False):
    """Helper function to run shell commands."""
    try:
        subprocess.run(command, shell=shell, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        exit(1)
    print("Virtual environment activated.")

# Step 2: Install dependencies
def install_dependencies():
    print("Installing dependencies from requirements.txt...")
    run_command(["pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed.")

# Step 3: Set environment variables
def set_environment_variables():
    print("Setting environment variables...")
    for key, value in ENV_VARS.items():
        if OS_TYPE == "Windows":
            run_command(f"set {key}={value}", shell=True)
        else:  # macOS/Linux
            run_command(f"export {key}={value}", shell=True)
    print("Environment variables set.")

# Step 4: Create database if it doesn't exist
def create_database():
    print("Creating database if it doesn't exist...")
    try:
        conn = psycopg2.connect("dbname=postgres user=postgres password=postgres host=localhost")
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'org_pedia'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute("CREATE DATABASE org_pedia")
            print("Database 'org_pedia' created.")
        else:
            print("Database 'org_pedia' already exists.")
        cursor.close()
        conn.close()
    except OperationalError as e:
        print("Failed to create the database.")
        print(e)
        exit(1)

# Step 5: Check database connection
def check_database_connection():
    print("Checking database connection...")
    try:
        conn = psycopg2.connect(ENV_VARS["DATABASE_URL"])
        conn.close()
        print("Database connection successful.")
    except OperationalError as e:
        print("Failed to connect to the database.")
        print(e)
        exit(1)

# Step 6: Initialize and apply database migrations
def setup_database():
    print("Setting up database...")
    if not os.path.exists("migrations"):
        run_command(["flask", "db", "init"])
        run_command(["flask", "db", "migrate", "-m", "Initial migration"])
        run_command(["flask", "db", "upgrade"])
        print("Database setup complete.")
    else:
        print("Database already set up.")

# Step 7: Start the server
def start_server():
    print("Starting the server...")
    run_command(["hypercorn", "app.main:app", "--reload"])

if __name__ == "__main__":
    print(f"Detected OS: {OS_TYPE}")
    try:
        set_environment_variables()
        create_database()
        check_database_connection()
        setup_database()
        start_server()
    except Exception as e:
        print(f"An error occurred: {e}")