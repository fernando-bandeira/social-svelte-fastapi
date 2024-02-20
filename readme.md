# Svelte/FastAPI Social Network

## Description

This is a Svelte/FastAPI social network project that combines a frontend built with Svelte and a backend powered by FastAPI. The project uses PostgreSQL as the database, and you can customize the database details in the "backend/database.py" file.

## Getting Started

### Prerequisites

Before running the project, ensure you have the following installed:

- Node.js and NPM
- Python
- PostgreSQL

### Installation

1. Install NPM, Python, and PostgreSQL.
2. Create a PostgreSQL database named "social" (you can modify the database details in the "backend/database.py" file).

### Environment Variables

Create a `.env` file inside the "backend/" directory with the following information:

```env
SECRET_KEY=your_secret_key_here
DB_PASS=your_database_password_here
```

Replace your_secret_key_here and your_database_password_here with your desired values.

If you don't know what the secret key should be, you can generate one at random with Python:

```
import secrets

api_secret_key = secrets.token_hex(32)
print(api_secret_key)
```

However, don't generate this inside the project dinamically. Instead, save it directly in the .env file.


## Running the Project

### Frontend

Navigate to the "frontend/" directory and follow these steps:

Install dependencies:
```
npm install
```

Run the development server:
```
npm run dev
```

This will install the necessary dependencies and start the Svelte development server.

### Backend

Navigate to the "backend/" directory and follow these steps:

Install Python dependencies (preferably in a virtual environment):
```
pip install -r requirements.txt
```

Run the FastAPI server with automatic reloading:
```
uvicorn main:app --reload
```
