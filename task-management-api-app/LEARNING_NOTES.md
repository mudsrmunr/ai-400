# Task Management API - Learning Notes

## Project Overview
Building a Task Management API using:
- **FastAPI**: A modern, high-performance Python web framework for building APIs
- **SQLModel**: An ORM (Object-Relational Mapping) library that combines SQLAlchemy and Pydantic
- **pytest**: A testing framework for writing and running tests
- **Neon.com**: A serverless PostgreSQL database service

---

## Key Concepts Learned

### 1. Environment Variables & Security

**Technical Terms:**
- **Environment Variable**: A dynamic value stored outside your code that your application can read at runtime
- **`.env` file**: A configuration file that stores environment variables locally
- **`.gitignore`**: A Git configuration file that specifies which files Git should ignore/not track
- **Version Control**: A system (like Git) that tracks changes to files over time

**How it works:**
```
.gitignore contains → ".env"
                         ↓
Git reads .gitignore → sees ".env" rule
                         ↓
Git ignores .env file → never uploads to GitHub
                         ↓
Your secrets stay on your computer only
```

**Security Rule**: Never hardcode (write directly) sensitive data like passwords, API keys, or connection strings in your source code.

---

### 2. Project Architecture

**Technical Terms:**
- **API (Application Programming Interface)**: A set of rules that allows different software to communicate
- **Endpoint**: A specific URL path that handles a particular type of request (e.g., `/tasks`, `/tasks/1`)
- **HTTP Methods**:
  - `GET` - Retrieve data (Read)
  - `POST` - Send data to create something (Create)
  - `PUT/PATCH` - Update existing data (Update)
  - `DELETE` - Remove data (Delete)
- **CRUD**: Create, Read, Update, Delete - the four basic operations

**Folder Structure Explained:**
```
app/
├── main.py      → Entry point, creates FastAPI instance
├── config.py    → Configuration settings, reads from .env
├── database.py  → Database connection setup
├── models/      → SQLModel classes (database table definitions)
├── schemas/     → Pydantic models (request/response data validation)
├── routers/     → API endpoint definitions
└── crud/        → Database operation functions
```

---

### 3. SQLModel & Databases

**Technical Terms:**
- **ORM (Object-Relational Mapping)**: A technique that lets you interact with databases using Python objects instead of raw SQL
- **Model**: A Python class that represents a database table
- **Schema**: A definition of what data looks like (structure and validation rules)
- **Migration**: The process of updating database structure when your models change

---

## Session Log

### Session 1 - Project Setup
- Discussed FastAPI, SQLModel, pytest overview
- Explained environment variable security (.env, .gitignore)
- Planned folder structure
- User preference: Technical jargon WITH explanations
- Database: Neon.com (PostgreSQL)
- Features: Basic CRUD (Create, Read, Update, Delete tasks)

---

## Quick Reference

### Task Entity Fields
- `id`: Unique identifier (Primary Key)
- `title`: Task title (required)
- `description`: Detailed description (optional)
- `status`: Current status (e.g., pending, in_progress, completed)
- `priority`: Priority level (e.g., low, medium, high)
- `due_date`: When task should be completed (optional)
- `created_at`: When task was created (auto-generated)
- `updated_at`: When task was last modified (auto-generated)

