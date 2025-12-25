# 🛡️ Threat Monitor API

> A Django REST Framework-based API for monitoring security events and managing alerts with role-based access control.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Authentication & Roles](#authentication--roles)
- [API Endpoints](#api-endpoints)
- [Features](#features)
- [Testing](#testing)
- [Development](#development)
- [Assumptions](#assumptions)

---

## 🎯 Project Overview

Threat Monitor is a security event management system that:

- Ingests security events via REST API (Admin-only)
- Automatically generates alerts for high-severity events (`HIGH`, `CRITICAL`) via Django signals
- Provides role-based access control (Admin: full access, Analyst: read-only alerts)
- Includes API documentation (Swagger UI, ReDoc) and logging

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | Django | 4.2.1 |
| **API** | Django REST Framework | 3.16.1 |
| **Authentication** | JWT (djangorestframework-simplejwt) | 5.5.1 |
| **Database** | SQLite | (development) |
| **Documentation** | drf-spectacular (OpenAPI 3.0) | 0.29.0 |
| **Python** | Python | 3.10+ |

---

## 📁 Project Structure

```
threat_monitor/
├── accounts/          # User management and groups
├── events/            # Event ingestion and processing
├── alerts/            # Alert management
└── threat_monitor/    # Project configuration
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation Steps

#### 1. Clone the repository

```bash
git clone <repository-url>
cd threat_monitor
```

#### 2. Create and activate virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run migrations

```bash
python manage.py migrate
```

#### 5. Create user groups

```bash
python manage.py create_groups
```

#### 6. Create test users (recommended for testing)

```bash
python manage.py create_test_users
```

This creates test users with default password `testpass123`:
- **Admin users:** `admin`, `testadmin` (can create events, manage alerts)
- **Analyst users:** `analyst`, `testanalyst` (read-only alerts, cannot create events)

**Options:**
- `--password PASSWORD`: Set custom password (default: `testpass123`)
- `--reset`: Delete existing test users before creating new ones

#### 7. Create superuser (optional)

```bash
python manage.py createsuperuser
```

#### 8. Run development server

```bash
python manage.py runserver
```

> 🌐 The API will be available at `http://localhost:8000/`

> 💡 **Quick Start Testing:** Use the test users created in step 6:
> - Admin: `admin` / `testpass123`
> - Analyst: `analyst` / `testpass123`
> - Import `Threat_Monitor_API.postman_collection.json` into Postman for ready-to-use API requests

---

## 🔐 Authentication & Roles

### Authentication

The API uses **JWT (JSON Web Token)** authentication. All endpoints require authentication except the token endpoints.

#### Obtain Access Token

**Request:**
```http
POST /api/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Refresh Access Token

**Request:**
```http
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "your_refresh_token"
}
```

#### Using the Token

Include the access token in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

**Example with cURL:**
```bash
curl -H "Authorization: Bearer <access_token>" http://localhost:8000/api/alerts/
```

### User Roles

Two roles are available via Django Groups:

#### 👑 Admin

- ✅ Full access to all endpoints
- ✅ Can create events
- ✅ Can create, read, update, and delete alerts
- ✅ Can update alert status

#### 👤 Analyst

- ✅ Read-only access to alerts (GET only)
- ❌ Cannot create events (403 Forbidden)
- ❌ Cannot modify alerts (403 Forbidden on PATCH, PUT, DELETE)

#### Assigning Roles

**Via Django Admin:**
1. Navigate to `/admin/auth/group/`
2. Add user to `Admin` or `Analyst` group

**Via Django Shell:**
```python
from django.contrib.auth.models import User, Group

user = User.objects.get(username='username')
admin_group = Group.objects.get(name='Admin')
user.groups.add(admin_group)
```

---

## 📡 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|:------:|:--------:|:-----------:|:-------------:|
| `POST` | `/api/token/` | Obtain JWT access token | ❌ No |
| `POST` | `/api/token/refresh/` | Refresh access token | ❌ No |

---

### Events Endpoints

| Method | Endpoint | Description | Auth Required | Rate Limit | Permissions |
|:------:|:--------:|:-----------:|:-------------:|:----------:|:-----------:|
| `POST` | `/api/events/` | Create new security event | ✅ Yes | 100/minute | Admin only |

#### Create Event Request

**Endpoint:** `POST /api/events/`

**Request Body:**
```json
{
    "source_name": "Firewall",
    "event_type": "Intrusion Attempt",
    "severity": "HIGH",
    "description": "Unauthorized access attempt detected"
}
```

**Severity Values:**
- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

> ⚠️ **Note:** Events with `HIGH` or `CRITICAL` severity automatically create alerts with `OPEN` status.

**Response (201 Created):**
```json
{
    "id": 1,
    "source_name": "Firewall",
    "event_type": "Intrusion Attempt",
    "severity": "HIGH",
    "description": "Unauthorized access attempt detected",
    "timestamp": "2025-12-25T14:30:00Z"
}
```

---

### Alerts Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|:------:|:--------:|:-----------:|:-------------:|:-----------:|
| `GET` | `/api/alerts/` | List alerts (paginated) | ✅ Yes | Admin, Analyst (read-only) |
| `GET` | `/api/alerts/{id}/` | Retrieve single alert | ✅ Yes | Admin, Analyst (read-only) |
| `POST` | `/api/alerts/` | Create alert | ✅ Yes | Admin only |
| `PATCH` | `/api/alerts/{id}/` | Update alert status | ✅ Yes | Admin only |
| `PUT` | `/api/alerts/{id}/` | Update alert | ✅ Yes | Admin only |
| `DELETE` | `/api/alerts/{id}/` | Delete alert | ✅ Yes | Admin only |

#### List Alerts

**Endpoint:** `GET /api/alerts/`

**Query Parameters:**

| Parameter | Type | Description | Example |
|:---------:|:----:|:-----------:|:-------:|
| `status` | string | Filter by alert status | `OPEN`, `ACKNOWLEDGED`, `RESOLVED` |
| `severity` | string | Filter by event severity | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `ordering` | string | Order by field | `created_at`, `status`, `-created_at` |

**Example Request:**
```http
GET /api/alerts/?status=OPEN&severity=HIGH&ordering=-created_at
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "count": 50,
    "next": "http://localhost:8000/api/alerts/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Alert: Intrusion Attempt",
            "description": "Unauthorized access attempt detected",
            "severity": "HIGH",
            "status": "OPEN",
            "event_id": 1,
            "event_type": "Intrusion Attempt",
            "created_at": "2025-12-25T14:30:00Z",
            "updated_at": "2025-12-25T14:30:00Z"
        }
    ]
}
```

#### Update Alert Status

**Endpoint:** `PATCH /api/alerts/{id}/`

**Request Body:**
```json
{
    "status": "ACKNOWLEDGED"
}
```

**Allowed Status Values:**
- `ACKNOWLEDGED`
- `RESOLVED`

> ⚠️ **Note:** Only `ACKNOWLEDGED` and `RESOLVED` can be set via API. `OPEN` status is set automatically.

**Response (200 OK):**
```json
{
    "status": "ACKNOWLEDGED"
}
```

**Error Response (403 Forbidden - Analyst):**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

### Documentation Endpoints

| Endpoint | Description |
|:--------:|:-----------:|
| `/api/docs/` | Swagger UI (interactive documentation) |
| `/api/redoc/` | ReDoc (alternative documentation) |
| `/api/schema/` | OpenAPI 3.0 schema (JSON/YAML) |

> 📚 Visit `/api/docs/` for interactive API documentation with "Try it out" functionality.

---

## ✨ Features

### 🔒 Security

- ✅ JWT-based authentication (required for all endpoints except token endpoints)
- ✅ Role-based access control (RBAC) via Django Groups
- ✅ Input validation and sanitization (XSS prevention via HTML tag stripping)
- ✅ Query parameter whitelisting (status and severity filters validated against allowed choices)
- ✅ Rate limiting on event ingestion (100 requests/minute per user)

### 📝 Logging

- ✅ Event ingestion logged to `logs/threat_monitor.log`
- ✅ Alert status updates logged with user information
- ✅ Console and file handlers configured

### 🔔 Automatic Alert Creation

When a **new** event with `HIGH` or `CRITICAL` severity is created:

1. ✅ An alert is automatically generated via Django signal
2. ✅ Alert status is set to `OPEN`
3. ✅ Alert is linked to the event via ForeignKey
4. ✅ Duplicate alerts are prevented (enforced by database UniqueConstraint and application logic)
5. ⚠️ **Note:** Alert creation only occurs on event creation, not on updates

---

## 🧪 Testing

### Run All Tests

```bash
python manage.py test
```

### Run Specific Test Suite

```bash
# Events tests
python manage.py test events.tests

# Alerts tests
python manage.py test alerts.tests
```

### Test Coverage

The test suite includes:
- Event alert creation for HIGH/CRITICAL severity events
- Analyst permission restrictions (cannot create events, cannot update alerts)
- Admin permission grants (can create events, can update alerts)

---

## 🛠️ Development

### Running Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Creating Groups

```bash
python manage.py create_groups
```

### Creating Test Users

```bash
# Create test users with default password
python manage.py create_test_users

# Create test users with custom password
python manage.py create_test_users --password mypassword

# Reset and recreate test users
python manage.py create_test_users --reset
```

**Test Users Created:**
- **Admin users:** `admin`, `testadmin` (can create events, manage alerts)
- **Analyst users:** `analyst`, `testanalyst` (read-only alerts, cannot create events)
- **Default password:** `testpass123` (all users)

### Accessing Admin Panel

Visit `/admin/` and login with superuser credentials.

### Checking System Status

```bash
# System check
python manage.py check

# Verify migrations
python manage.py makemigrations --check
```

---

## 📌 Assumptions & Implementation Details

1. **User Model**: Uses Django's default User model (no custom user model implemented)
2. **Database**: SQLite for development (can be configured for production databases)
3. **Alert Status Updates**: Only `ACKNOWLEDGED` and `RESOLVED` can be set via PATCH endpoint. `OPEN` status is set automatically and cannot be changed via API.
4. **Event Severity**: Strict validation - only `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` accepted (case-insensitive, normalized to uppercase)
5. **Rate Limiting**: Event ingestion endpoint limited to 100 requests/minute per authenticated user
6. **Alert Uniqueness**: One alert per event enforced at database level (UniqueConstraint) and application level (signal logic)
7. **Logging**: Logs written to `logs/threat_monitor.log` and console (INFO level)
8. **Permissions**: Group-based permissions using Django Groups (`Admin`, `Analyst`)
9. **Pagination**: Default page size of 100 items (configurable in DRF settings)
10. **Token Lifetime**: Access tokens valid for 1 hour, refresh tokens for 1 day (configurable in SIMPLE_JWT settings)
11. **Event Creation**: Admin-only access (Analyst cannot create events)
12. **Alert Creation**: Alerts are created automatically via signal, not through API endpoints

---

## 📄 License

[Specify your license here]

## 🤝 Contributing

[Specify contribution guidelines here]

---

**Built with ❤️ using Django REST Framework**
