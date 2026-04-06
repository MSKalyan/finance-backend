# Finance Data Processing Backend

## Overview

This project is a Django REST Framework backend for a finance dashboard system.

It provides:

* Role-Based Access Control (RBAC)
* Financial record management
* Dashboard analytics APIs
* Secure JWT authentication

The system follows an **organization-level data model**, where records are shared across users and access is controlled via roles.

---

## Tech Stack

* Django
* Django REST Framework
* SimpleJWT (Authentication)
* SQLite (Database)

---

## Features

### Authentication

* JWT-based authentication
* Secure login endpoint

### Role-Based Access Control

* **Admin** → Full access (CRUD + user management)
* **Analyst** → Read-only access to records and insights
* **Viewer** → Dashboard-only access

### Financial Records

* Create, read, update, delete (soft delete)
* Filtering, search, and pagination
* Category normalization and validation

### Dashboard APIs

* Total income & expense
* Net balance
* Category-wise breakdown
* Monthly trends
* Recent transactions

### Additional Enhancements

* Pagination
* Search & filtering
* Soft delete support
* Rate limiting (throttling)
* Unit & integration tests

---

## Setup Instructions

1. Clone the repository

```bash
git clone <your-repo-url>
cd finance-backend
```

2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Run server

```bash
python manage.py runserver
```

---

## Authentication

### Login

**POST** `/api/login/`

```json
{
  "username": "admin",
  "password": "admin123"
}
```

### Response

```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

### Usage

Include token in headers:

```
Authorization: Bearer <access_token>
```

---

## API Endpoints

### Records

| Method    | Endpoint           | Description   |
| --------- | ------------------ | ------------- |
| GET       | /api/records/      | List records  |
| POST      | /api/records/      | Create record |
| PUT/PATCH | /api/records/{id}/ | Update record |
| DELETE    | /api/records/{id}/ | Soft delete   |

---

### Query Examples

#### Filtering

```
/api/records/?type=income
/api/records/?date__gte=2026-01-01
```

#### Search

```
/api/records/?search=salary
```

#### Pagination

```
/api/records/?page=1&page_size=10
```

#### Ordering

```
/api/records/?ordering=-date
```

---

## Dashboard APIs

| Endpoint                     | Description                    |
| ---------------------------- | ------------------------------ |
| GET /api/dashboard/summary/  | Total income, expense, balance |
| GET /api/dashboard/category/ | Category-wise aggregation      |
| GET /api/dashboard/trends/   | Monthly trends                 |
| GET /api/dashboard/recent/   | Recent transactions            |

---

## Rate Limiting

* Login: **5 requests per minute**
* Records API: **50 requests per day**

If limit exceeds:

```json
{
  "detail": "Request was throttled."
}
```

---

## Testing

Run tests:

```bash
python manage.py test
```

### Test Coverage

* Authentication enforcement
* Role-based permissions (RBAC)
* Record creation and access control
* Soft delete behavior
* Hidden deleted records
* Rate limiting validation

---

## Design Decisions

* **Shared dataset model** (organization-level data)
* **Soft delete** instead of hard delete for data safety
* **Serializer-level validation** for consistency
* **View-level RBAC enforcement**
* **ORM-based aggregation** for dashboard performance

---

## Assumptions

* All users operate on shared financial data
* Categories are normalized (lowercase)
* Custom category required when category = "other"

---

## Future Improvements

* Redis-based caching for production
* Advanced analytics and insights
* Role-based data isolation
* API documentation with Swagger/OpenAPI
* Frontend integration

---

## Summary

This backend demonstrates:

* Clean architecture and separation of concerns
* Strong RBAC implementation
* Reliable data handling
* Scalable API design
* Production-aware enhancements

The system is ready for deployment and further extension.
