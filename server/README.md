# Org Pedia Server

## How to run the project.

## Two parts setup.
If you don't have bedrock setup, you can download ollama and run it locally on your computer.

## Ollama
Go to ollama and follow the instructions to install it on your computer and also download codellama or llama3.1 8B parameters

## Bedrock
If you have aws account/not. Try to create one use existing one. Once you are in your console. Go to bedrock create your LLM instances. Once you have it ready, create your own creds and set it up on your computer.

## Project setup.
You must setup python environment and run pip install -r requirements.txt

## Add your database into in env file
- AWS creds
- Database creds
- etc



# Database

## Create and Apply New Migrations
- After ensuring that the database is up to date, create the new migration for adding the id column:

- Initial database migration

```
flask db init  # Initialize migrations (run once)
flask db migrate -m "Initial migration"  # Create a migration
flask db upgrade  # Apply the migration
```




```bash 
flask db migrate -m "Add id column to users table
```

- Then apply this new migration:
```bash
flask db upgrade
```