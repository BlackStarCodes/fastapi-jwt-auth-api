# fastapi-jwt-auth-api
A simple FastAPI REST API demonstrating authentication, authorization, CRUD operations, and PostgreSQL integration.

## Description
A REST API built with FastAPI for user management. It demonstrates CRUD operations, password hashing, JWT authentication, authorization, SQLAlchemy ORM, and PostgreSQL.

## Features
- User registration
- User login with JWT authentication
- Password hashing using pwdlib
- CRUD operations
- Authorization (users can only modify or delete their own account)
- PostgreSQL database
- SQLAlchemy ORM 

### Prerequisites
1. git
2. Python 3.11+
3. PostgreSQL
4. A PostgreSQL database

### Installation
1. create a new directory to clone the repository

2. open your terminal, follow the below instructions in the terminal

3. enter the below to clone repo to current working directory:

`git clone https://github.com/nishy010/fastapi-jwt-auth-api.git`

4. change into project directory:

`cd fastapi-jwt-auth-api/`

5. create virtual environment for this app with:

`python -m venv .venv`

6. activate the venv with:

`source .venv/Scripts/activate`

7. install the required dependencies:

`pip install -r requirements.txt`


### Configuration and Running
1. change directory to src

`cd src/`

2. Update values in .env file with your Postgres credentials and JWT secret. check the .env.example for reference if needed

3. Start the FastAPI development server

`fastapi dev main.py`

4. Open your browser and access the interactive api docs at:

`http://127.0.0.1:8000/docs`

or

`http://localhost:8000/docs`

### Authentication

Protected endpoints require authentication.

To authenticate in the Swagger UI/Interactive docs:

1. Click the **Authorize** button.
2. Enter your username and password.
3. Click **Authorize**.
4. Swagger will automatically obtain and include the JWT access token in protected requests.


### Tech Stack
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- pwdlib
- JWT
