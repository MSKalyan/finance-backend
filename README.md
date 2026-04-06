# Finance Backend System (Django + DRF)

## Overview

This project is a backend system for managing financial records with **Role-Based Access Control (RBAC)** and **analytics dashboards**.

It is built using Django and Django REST Framework, with a lightweight template-based frontend for demonstration.

---

## Features

### 1. Authentication

* JWT-based authentication using SimpleJWT
* Secure login with access & refresh tokens

### 2. Role-Based Access Control (RBAC)

| Role    | Permissions                            |
| ------- | -------------------------------------- |
| Admin   | Full CRUD on records + user management |
| Analyst | Read-only records + dashboard access   |
| Viewer  | Dashboard only                         |

---

### 3. Financial Records Management

* Create, read, update, delete records
* Fields:

  * amount
  * type (income / expense)
  * category
  * custom_category (when category = "other")
  * date
  * description
* Soft delete implemented

---

### 4. Dashboard APIs

* Total income, expense, balance
* Category-wise breakdown
* Monthly trends
* Recent transactions

---

### 5. Filtering, Search, Pagination

* Filter by type, category, date, amount
* Search across category, custom_category, description
* Ordering (date, amount)
* Pagination enabled

---

### 6. Validation

* Custom validation for `custom_category`
* Required when category = "other"

---

## Tech Stack

* Django
* Django REST Framework
* SimpleJWT
* SQLite
* HTML Templates (for demo UI)

---

## Project Setup

### 1. Clone Repository

```bash
git clone https://github.com/MSKalyan/finance-backend.git
cd finance_backend
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run Migrations

```bash
python manage.py migrate
```

---

### 5. Create Demo Users

```bash
python manage.py shell
```

```python
from users.models import User

def create_user_safe(email, password, role):
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": email,
            "role": role
        }
    )

    if created:
        user.set_password(password)
        user.save()

create_user_safe("admin@test.com", "admin123", "admin")
create_user_safe("analyst@test.com", "analyst123", "analyst")
create_user_safe("viewer@test.com", "viewer123", "viewer")
```

---

### 6. Run Server

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000/
```

---

## Demo Credentials

* **Admin**

  * Email: [admin@test.com](mailto:admin@test.com)
  * Password: admin

* **Analyst**

  * Email: [analyst@test.com](mailto:analyst@test.com)
  * Password: analyst

* **Viewer**

  * Email: [viewer@test.com](mailto:viewer@test.com)
  * Password: viewer

---

## API Endpoints (Core)

### Auth

* `/api/users/register/`
* `/api/users/login/`
* `/api/users/refresh/`

### Records

* `/api/records/` (CRUD + filters)

### Dashboard

* `/api/dashboard/summary/`
* `/api/dashboard/categories/`
* `/api/dashboard/recent/`
* `/api/dashboard/trends/`

---

## Notes

* Data is shared across users (organization-level model)
* RBAC enforced at both API and UI level
* Templates included only for easier evaluation

---

## Conclusion

This project demonstrates:

* Clean RBAC implementation
* Efficient aggregation using ORM
* Scalable API design
* Real-world backend features (soft delete, throttling, filtering)
