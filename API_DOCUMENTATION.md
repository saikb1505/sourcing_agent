# Sourcing Agent API Documentation

Complete API reference for building a frontend application with Lovable.

## Overview

- **Framework**: FastAPI
- **Authentication**: JWT Bearer Tokens (OAuth2)
- **Base URL**: `http://localhost:8000` (configure for production)
- **Content-Type**: `application/json`

---

## Authentication

All protected endpoints require the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Token Expiration
- Default: 30 minutes
- Algorithm: HS256

---

## API Endpoints

### 1. Authentication (`/api/auth`)

#### POST `/api/auth/login`
Authenticate user and receive JWT token.

**Auth Required**: No

**Request** (form-data):
```
username: string (username or email)
password: string
```

**Response** `200 OK`:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors**:
- `401 Unauthorized`: Incorrect username or password
- `403 Forbidden`: User account is inactive

---

#### GET `/api/auth/me`
Get current authenticated user information.

**Auth Required**: Yes

**Response** `200 OK`:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

#### PUT `/api/auth/me/password`
Update current user's password.

**Auth Required**: Yes

**Request**:
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

**Response** `200 OK`:
```json
{
  "message": "Password updated successfully"
}
```

**Errors**:
- `400 Bad Request`: Current password is incorrect

---

### 2. Search Operations (`/api/search`)

All search endpoints require authentication.

#### POST `/api/search/generate`
Generate an optimized search query from natural language using AI.

**Auth Required**: Yes

**Request**:
```json
{
  "user_input": "Find Ruby on Rails developers in Hyderabad with 5+ years experience"
}
```

**Response** `200 OK`:
```json
{
  "id": 42,
  "user_input": "Find Ruby on Rails developers in Hyderabad with 5+ years experience",
  "generated_query": "site:linkedin.com/in \"Ruby on Rails\" OR \"RoR\" developer Hyderabad \"5 years\" OR \"6 years\" OR \"7 years\"",
  "created_at": "2024-01-15T14:30:00Z"
}
```

---

#### POST `/api/search/execute/{query_id}`
Execute a previously saved search query.

**Auth Required**: Yes

**Path Parameters**:
- `query_id` (integer): ID of the search query to execute

**Response** `200 OK`:
```json
{
  "search_query_id": 42,
  "results_count": 87,
  "search_timestamp": "2024-01-15T14:35:00Z"
}
```

**Errors**:
- `404 Not Found`: Search query not found

---

#### POST `/api/search/generate-and-execute`
Generate a search query and immediately execute it (combined operation).

**Auth Required**: Yes

**Request**:
```json
{
  "user_input": "Python developers in Bangalore with AWS experience"
}
```

**Response** `200 OK`:
```json
{
  "search_query_id": 43,
  "results_count": 124,
  "search_timestamp": "2024-01-15T14:40:00Z"
}
```

---

#### GET `/api/search/queries`
Get all search queries created by the current user.

**Auth Required**: Yes

**Query Parameters**:
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 50): Maximum records to return

**Response** `200 OK`:
```json
[
  {
    "id": 42,
    "user_input": "Find Ruby on Rails developers in Hyderabad",
    "generated_query": "site:linkedin.com/in \"Ruby on Rails\" developer Hyderabad",
    "last_search_date": "2024-01-15T14:35:00Z",
    "created_user_id": 1,
    "last_run_user_id": 1,
    "created_at": "2024-01-15T14:30:00Z",
    "updated_at": "2024-01-15T14:35:00Z"
  }
]
```

---

#### GET `/api/search/queries/{query_id}`
Get a specific search query by ID.

**Auth Required**: Yes

**Path Parameters**:
- `query_id` (integer): ID of the search query

**Response** `200 OK`:
```json
{
  "id": 42,
  "user_input": "Find Ruby on Rails developers in Hyderabad",
  "generated_query": "site:linkedin.com/in \"Ruby on Rails\" developer Hyderabad",
  "last_search_date": "2024-01-15T14:35:00Z",
  "created_user_id": 1,
  "last_run_user_id": 1,
  "created_at": "2024-01-15T14:30:00Z",
  "updated_at": "2024-01-15T14:35:00Z"
}
```

**Errors**:
- `404 Not Found`: Search query not found

---

#### GET `/api/search/queries/{query_id}/results`
Get all search results for a specific query.

**Auth Required**: Yes

**Path Parameters**:
- `query_id` (integer): ID of the search query

**Query Parameters**:
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100): Maximum records to return

**Response** `200 OK`:
```json
{
  "search_query_id": 42,
  "total_results": 87,
  "results": [
    {
      "id": 1,
      "search_query_id": 42,
      "result_payload": {
        "title": "John Doe - Senior Ruby Developer",
        "link": "https://linkedin.com/in/johndoe",
        "snippet": "Experienced Ruby on Rails developer...",
        "display_link": "linkedin.com"
      },
      "search_timestamp": "2024-01-15T14:35:00Z",
      "enriched_timestamp": null,
      "executed_by_user_id": 1,
      "created_at": "2024-01-15T14:35:00Z"
    }
  ]
}
```

**Errors**:
- `404 Not Found`: Search query not found

---

#### DELETE `/api/search/queries/{query_id}`
Delete a search query and all its results.

**Auth Required**: Yes

**Path Parameters**:
- `query_id` (integer): ID of the search query to delete

**Response** `200 OK`:
```json
{
  "message": "Search query deleted successfully"
}
```

**Errors**:
- `404 Not Found`: Search query not found
- `403 Forbidden`: Not authorized to delete this query

---

#### POST `/api/search/results/{result_id}/enrich`
Mark a search result as enriched.

**Auth Required**: Yes

**Path Parameters**:
- `result_id` (integer): ID of the search result

**Response** `200 OK`:
```json
{
  "id": 1,
  "enriched_timestamp": "2024-01-15T15:00:00Z"
}
```

**Errors**:
- `404 Not Found`: Search result not found

---

#### GET `/api/search/queries/{query_id}/export`
Export search results to CSV file.

**Auth Required**: Yes

**Path Parameters**:
- `query_id` (integer): ID of the search query

**Response** `200 OK`:
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename=search_results_{query_id}.csv`

**CSV Columns**:
- `user_input`
- `generated_query`
- `name`
- `snippet`
- `linkedin_url`
- `created_time`

**Errors**:
- `404 Not Found`: Search query not found

---

### 3. Admin Operations (`/api/admin`)

All admin endpoints require admin-level authentication.

#### User Management

##### POST `/api/admin/users`
Create a new user (only way to create users - no self-registration).

**Auth Required**: Yes (Admin)

**Request**:
```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "full_name": "New User",
  "password": "securepassword123",
  "is_admin": false
}
```

**Response** `201 Created`:
```json
{
  "id": 5,
  "email": "newuser@example.com",
  "username": "newuser",
  "full_name": "New User",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-15T16:00:00Z",
  "updated_at": "2024-01-15T16:00:00Z"
}
```

**Errors**:
- `400 Bad Request`: Email already registered / Username already taken

---

##### GET `/api/admin/users`
List all users.

**Auth Required**: Yes (Admin)

**Query Parameters**:
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100): Maximum records to return

**Response** `200 OK`:
```json
[
  {
    "id": 1,
    "email": "admin@example.com",
    "username": "admin",
    "full_name": "Admin User",
    "is_active": true,
    "is_admin": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

---

##### GET `/api/admin/users/{user_id}`
Get a specific user by ID.

**Auth Required**: Yes (Admin)

**Path Parameters**:
- `user_id` (integer): ID of the user

**Response** `200 OK`:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errors**:
- `404 Not Found`: User not found

---

##### PUT `/api/admin/users/{user_id}`
Update user details.

**Auth Required**: Yes (Admin)

**Path Parameters**:
- `user_id` (integer): ID of the user

**Request** (all fields optional):
```json
{
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "Updated Name",
  "is_active": true,
  "is_admin": false
}
```

**Response** `200 OK`:
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "Updated Name",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T16:30:00Z"
}
```

**Errors**:
- `404 Not Found`: User not found
- `400 Bad Request`: Email already registered / Username already taken

---

##### POST `/api/admin/users/{user_id}/deactivate`
Deactivate a user account.

**Auth Required**: Yes (Admin)

**Path Parameters**:
- `user_id` (integer): ID of the user

**Response** `200 OK`:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": false,
  "is_admin": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T17:00:00Z"
}
```

**Errors**:
- `404 Not Found`: User not found
- `400 Bad Request`: Cannot deactivate your own account

---

##### POST `/api/admin/users/{user_id}/activate`
Activate a user account.

**Auth Required**: Yes (Admin)

**Path Parameters**:
- `user_id` (integer): ID of the user

**Response** `200 OK`:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T17:05:00Z"
}
```

**Errors**:
- `404 Not Found`: User not found

---

##### POST `/api/admin/users/{user_id}/reset-password`
Reset a user's password.

**Auth Required**: Yes (Admin)

**Path Parameters**:
- `user_id` (integer): ID of the user

**Query Parameters**:
- `new_password` (string): The new password

**Response** `200 OK`:
```json
{
  "message": "Password reset successfully"
}
```

**Errors**:
- `404 Not Found`: User not found

---

##### DELETE `/api/admin/users/{user_id}`
Delete a user permanently.

**Auth Required**: Yes (Admin)

**Path Parameters**:
- `user_id` (integer): ID of the user

**Response** `200 OK`:
```json
{
  "message": "User deleted successfully"
}
```

**Errors**:
- `404 Not Found`: User not found
- `400 Bad Request`: Cannot delete your own account

---

#### Query Management

##### GET `/api/admin/queries`
Get all search queries across all users.

**Auth Required**: Yes (Admin)

**Query Parameters**:
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100): Maximum records to return

**Response** `200 OK`:
```json
[
  {
    "id": 42,
    "user_input": "Find Ruby on Rails developers in Hyderabad",
    "generated_query": "site:linkedin.com/in \"Ruby on Rails\" developer Hyderabad",
    "last_search_date": "2024-01-15T14:35:00Z",
    "created_user_id": 1,
    "last_run_user_id": 1,
    "created_at": "2024-01-15T14:30:00Z",
    "updated_at": "2024-01-15T14:35:00Z"
  }
]
```

---

##### GET `/api/admin/queries/user/{user_id}`
Get all search queries for a specific user.

**Auth Required**: Yes (Admin)

**Path Parameters**:
- `user_id` (integer): ID of the user

**Query Parameters**:
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100): Maximum records to return

**Response** `200 OK`:
```json
[
  {
    "id": 42,
    "user_input": "Find Ruby on Rails developers in Hyderabad",
    "generated_query": "site:linkedin.com/in \"Ruby on Rails\" developer Hyderabad",
    "last_search_date": "2024-01-15T14:35:00Z",
    "created_user_id": 1,
    "last_run_user_id": 1,
    "created_at": "2024-01-15T14:30:00Z",
    "updated_at": "2024-01-15T14:35:00Z"
  }
]
```

---

##### DELETE `/api/admin/queries/{query_id}`
Delete any search query.

**Auth Required**: Yes (Admin)

**Path Parameters**:
- `query_id` (integer): ID of the search query

**Response** `200 OK`:
```json
{
  "message": "Search query deleted successfully"
}
```

**Errors**:
- `404 Not Found`: Search query not found

---

#### System Statistics

##### GET `/api/admin/stats`
Get system-wide statistics.

**Auth Required**: Yes (Admin)

**Response** `200 OK`:
```json
{
  "total_users": 25,
  "active_users": 22,
  "admin_users": 3,
  "total_search_queries": 150
}
```

---

### 4. Health Check

#### GET `/`
Root endpoint - basic health check.

**Auth Required**: No

**Response** `200 OK`:
```json
{
  "message": "Sourcing Agent API",
  "version": "1.0.0",
  "status": "running"
}
```

---

#### GET `/health`
Health check endpoint.

**Auth Required**: No

**Response** `200 OK`:
```json
{
  "status": "healthy"
}
```

---

## Data Models

### User

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| email | string | User's email address |
| username | string | Unique username |
| full_name | string (nullable) | User's full name |
| is_active | boolean | Whether account is active |
| is_admin | boolean | Whether user has admin privileges |
| created_at | datetime | Account creation timestamp |
| updated_at | datetime | Last update timestamp |

### SearchQuery

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| user_input | string | Original natural language input |
| generated_query | string | AI-optimized search query |
| last_search_date | datetime (nullable) | When query was last executed |
| created_user_id | integer | ID of user who created the query |
| last_run_user_id | integer (nullable) | ID of user who last executed |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### SearchResult

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| search_query_id | integer | Associated search query ID |
| result_payload | object | Search result data (title, link, snippet, etc.) |
| search_timestamp | datetime | When search was executed |
| enriched_timestamp | datetime (nullable) | When result was enriched |
| executed_by_user_id | integer | ID of user who executed search |
| created_at | datetime | Creation timestamp |

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

---

## Frontend Integration Guide for Lovable

### Authentication Flow

1. **Login**: POST to `/api/auth/login` with username/password
2. **Store Token**: Save `access_token` in localStorage or secure storage
3. **Attach Token**: Include `Authorization: Bearer <token>` header on all requests
4. **Refresh**: Re-authenticate when token expires (401 response)

### Typical User Workflows

#### Search Workflow
1. User enters natural language search → `POST /api/search/generate-and-execute`
2. Display results count and timestamp
3. Fetch results → `GET /api/search/queries/{id}/results`
4. Display paginated results list
5. Allow CSV export → `GET /api/search/queries/{id}/export`

#### History View
1. Fetch user's queries → `GET /api/search/queries`
2. Display list with search dates
3. Allow re-execution → `POST /api/search/execute/{id}`
4. Allow deletion → `DELETE /api/search/queries/{id}`

#### Admin Dashboard
1. Fetch stats → `GET /api/admin/stats`
2. Display user management → `GET /api/admin/users`
3. Create new users → `POST /api/admin/users`
4. Manage user status → Activate/Deactivate endpoints

### Recommended Pages

1. **Login Page** - Authentication form
2. **Dashboard** - Quick stats and recent searches
3. **Search Page** - Main search interface with results display
4. **History Page** - List of past searches with actions
5. **Results Detail** - Paginated results view with enrichment status
6. **Admin Panel** (admin only) - User management and system stats
7. **Profile/Settings** - Password change, user info

### State Management Suggestions

```typescript
// Auth State
interface AuthState {
  token: string | null;
  user: User | null;
  isAdmin: boolean;
  isAuthenticated: boolean;
}

// Search State
interface SearchState {
  queries: SearchQuery[];
  currentQuery: SearchQuery | null;
  results: SearchResult[];
  totalResults: number;
  isLoading: boolean;
}
```

---

## CORS Configuration

The API allows all origins (`*`) for development. Configure appropriately for production:

```python
allow_origins=["https://your-lovable-app.com"]
```
