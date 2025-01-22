# Org Pedia Server

## How to run the project

This project uses Ollama for local LLM (Large Language Model) processing and PostgreSQL as the database.

## Setup

### 1. Ollama Setup
1. Go to [Ollama's website](https://ollama.ai/) and follow the instructions to install it on your computer.
2. Download either CodeLlama or Llama 3.2 (3B parameters) model using Ollama.

   For example, to download CodeLlama:
   ```bash
   ollama pull codellama
   ```
   Or for Llama 3.2:
   ```bash
   ollama pull llama2:3b
   ```

### 2. PostgreSQL Setup
1. Use the provided `docker-compose.yml` file to run the PostgreSQL database. If you already have PostgreSQL installed, modify the database URL accordingly:
   ```plaintext
   postgresql://postgres:postgres@localhost/org_pedia
   ```
2. Create a new database for the project:
   - Open your PostgreSQL DBMS and create a database named `org_pedia`.

3. Make note of your PostgreSQL username, password, and the database name you just created.

### 3. Project Setup
1. Set up a Python virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the environment variables by copying `.env.example` to `.env` and updating the values as needed. Alternatively, you can set them directly in your shell:

   On Windows:
   ```shell
   set DATABASE_URL="postgresql://postgres:postgres@localhost/org_pedia"
   set JWT_SECRET_KEY=super-secret-key-20124
   set SECRET_KEY=super-secret-key-20124
   set FLASK_APP=app.main
   ```

   On macOS and Linux:
   ```bash
   export DATABASE_URL="postgresql://postgres:postgres@localhost/org_pedia"
   export JWT_SECRET_KEY=super-secret-key-20124
   export SECRET_KEY=super-secret-key-20124
   export FLASK_APP=app.main
   ```

## Database Management

### Initial Setup
To initialize the database and create initial migrations:

```bash
flask db init  # Initialize migrations (run once)
flask db migrate -m "Initial migration"  # Create a migration
flask db upgrade  # Apply the migration
```

### Updating the Database
When making changes to the database schema:

1. Create a new migration:
   ```bash
   flask db migrate -m "Description of the change"
   ```
   For example:
   ```bash
   flask db migrate -m "Add id column to users table"
   ```

2. Apply the new migration:
   ```bash
   flask db upgrade
   ```

## Running the Server

1. Ensure your virtual environment is activated and the `DATABASE_URL` is set.
2. Start the Flask server using Hypercorn:

   ```bash
   hypercorn app.main:app --reload
   ```
   The server will typically run on `http://127.0.0.1:8000/`.

## Development
- The main application logic is in `app.py` or similar files.
- Ensure Ollama is running when testing LLM-related features.
- Make sure your PostgreSQL server is running and accessible.

## Troubleshooting
- If you encounter issues with the LLM, ensure Ollama is running and the correct model is downloaded.
- For database issues:
  - Check that PostgreSQL is running.
  - Verify your database connection string (`DATABASE_URL`).
  - Ensure all migrations are up to date.
  - Check PostgreSQL logs for any errors.

For more detailed information or if you continue to experience issues, please refer to the project documentation or contact the development team.
