# Admin User Management Guide

## Overview

A complete admin user management system has been added to the application. Superusers can now view, manage, and control all user accounts through API endpoints.

## Current Superuser Account

**Username**: `testuser`
**Email**: `test@example.com`
**Status**: Active Superuser ✅

Use this account to access all admin endpoints.

---

## All Users in Database

| Username | Email | Full Name | Active | Superuser | Created |
|----------|-------|-----------|--------|-----------|---------|
| testuser | test@example.com | test user | ✅ Yes | ✅ Yes | 2026-01-07 |
| frontendtest | frontend@test.com | Frontend Test | ✅ Yes | ❌ No | 2026-01-08 |
| Eugen Tamon | eus.java@gmail.com | None | ✅ Yes | ❌ No | 2026-01-08 |
| joy | joy@gmail.com | None | ✅ Yes | ❌ No | 2026-01-08 |

---

## API Endpoints

All endpoints require **superuser authentication** (Bearer token from login).

### Authentication Flow

```bash
# 1. Login as superuser
POST /api/auth/login
{
  "username": "testuser",
  "password": "your_password"
}

# Response includes access_token
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": { ... }
}

# 2. Use token in subsequent requests
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

### 1. List All Users

**Endpoint**: `GET /api/users`

**Query Parameters**:
- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 100) - Max records to return
- `is_active` (bool, optional) - Filter by active status
- `is_superuser` (bool, optional) - Filter by superuser status

**Example**:
```bash
# List all users
GET /api/users

# List only active users
GET /api/users?is_active=true

# List only superusers
GET /api/users?is_superuser=true

# Pagination
GET /api/users?skip=10&limit=20
```

**Response**:
```json
{
  "users": [
    {
      "id": "165db9da-c283-4559-81d6-41d99fcfa32d",
      "username": "testuser",
      "email": "test@example.com",
      "full_name": "test user",
      "is_active": true,
      "is_superuser": true,
      "created_at": "2026-01-07T13:30:47.731657",
      "updated_at": "2026-01-08T17:41:58.550381"
    }
  ],
  "total": 4,
  "skip": 0,
  "limit": 100
}
```

---

### 2. Get User Details

**Endpoint**: `GET /api/users/{user_id}`

**Example**:
```bash
GET /api/users/165db9da-c283-4559-81d6-41d99fcfa32d
```

**Response**:
```json
{
  "id": "165db9da-c283-4559-81d6-41d99fcfa32d",
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "test user",
  "is_active": true,
  "is_superuser": true,
  "created_at": "2026-01-07T13:30:47.731657",
  "updated_at": "2026-01-08T17:41:58.550381"
}
```

---

### 3. Update User

**Endpoint**: `PUT /api/users/{user_id}`

**Body** (all fields optional):
```json
{
  "username": "newusername",
  "email": "newemail@example.com",
  "full_name": "New Full Name",
  "is_active": true,
  "is_superuser": false
}
```

**Example**:
```bash
PUT /api/users/165db9da-c283-4559-81d6-41d99fcfa32d
{
  "full_name": "Updated Name"
}
```

**Validation**:
- Username must be 3-100 characters
- Email must be valid email format
- Username and email must be unique
- Returns 400 if username/email already exists

---

### 4. Reset User Password

**Endpoint**: `POST /api/users/{user_id}/reset-password`

**Body**:
```json
{
  "new_password": "newpassword123"
}
```

**Example**:
```bash
POST /api/users/eaf7f653-e768-4b53-86ba-045c9a8a1b7a/reset-password
{
  "new_password": "securepass456"
}
```

**Validation**:
- Password must be 8-100 characters
- Password is securely hashed with bcrypt

---

### 5. Promote User to Superuser

**Endpoint**: `POST /api/users/{user_id}/promote-superuser`

**Example**:
```bash
POST /api/users/eaf7f653-e768-4b53-86ba-045c9a8a1b7a/promote-superuser
```

**Response**: Updated user object with `is_superuser: true`

---

### 6. Demote Superuser to Regular User

**Endpoint**: `POST /api/users/{user_id}/demote-superuser`

**Example**:
```bash
POST /api/users/eaf7f653-e768-4b53-86ba-045c9a8a1b7a/demote-superuser
```

**Security**:
- ❌ Cannot demote yourself
- Returns 400 error if attempting self-demotion

---

### 7. Activate User Account

**Endpoint**: `POST /api/users/{user_id}/activate`

**Example**:
```bash
POST /api/users/eaf7f653-e768-4b53-86ba-045c9a8a1b7a/activate
```

**Effect**: Sets `is_active = true`, user can login

---

### 8. Deactivate User Account

**Endpoint**: `POST /api/users/{user_id}/deactivate`

**Example**:
```bash
POST /api/users/eaf7f653-e768-4b53-86ba-045c9a8a1b7a/deactivate
```

**Effect**: Sets `is_active = false`, user cannot login

**Security**:
- ❌ Cannot deactivate yourself
- Returns 400 error if attempting self-deactivation

---

### 9. Delete User

**Endpoint**: `DELETE /api/users/{user_id}`

**Example**:
```bash
DELETE /api/users/eaf7f653-e768-4b53-86ba-045c9a8a1b7a
```

**Response**: 204 No Content (success)

**Security**:
- ❌ Cannot delete yourself
- Returns 400 error if attempting self-deletion
- ⚠️ **Permanent action** - cannot be undone

---

## Security Features

### Password Security
- **Bcrypt Hashing**: All passwords use bcrypt with salt rounds
- **One-Way Encryption**: Passwords cannot be decrypted, only verified
- **No Plaintext Storage**: Admins cannot see user passwords
- **Secure Reset**: Admin password resets require new password input

### Authorization
- **Superuser Only**: All endpoints require `is_superuser = true`
- **Bearer Token**: JWT authentication required
- **Session Validation**: Tokens must be active and not expired
- **Self-Protection**: Cannot demote, deactivate, or delete yourself

### Data Protection
- **Password Hashes Not Exposed**: API responses never include password_hash
- **Audit Trail**: All user changes update `updated_at` timestamp
- **Active Session Check**: Deactivated users are immediately logged out

---

## Testing the API

### Option 1: Using the Test Script

```bash
cd backend
source venv/Scripts/activate  # Windows: venv\Scripts\activate
python test_admin_api.py
```

**Note**: Update the password in `test_admin_api.py` line 22 before running.

### Option 2: Using cURL

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "your_password"}'

# Save the token, then list users
curl -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Option 3: Using API Documentation

1. Go to http://localhost:8000/docs
2. Click "Authorize" button (top right)
3. Login with testuser credentials
4. Use the token to test endpoints
5. Try all `/api/users` endpoints in the Swagger UI

---

## Common Tasks

### Task 1: View All Users
```bash
GET /api/users
```

### Task 2: Reset a Forgotten Password
```bash
# Get user ID from list
GET /api/users

# Reset password
POST /api/users/{user_id}/reset-password
{
  "new_password": "newpassword123"
}
```

### Task 3: Create Another Admin
```bash
# First, identify the user ID
GET /api/users

# Promote to superuser
POST /api/users/{user_id}/promote-superuser
```

### Task 4: Disable a User Account
```bash
POST /api/users/{user_id}/deactivate
```

### Task 5: Re-enable a User Account
```bash
POST /api/users/{user_id}/activate
```

---

## Error Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 200 | Success | Request completed successfully |
| 204 | No Content | Delete successful |
| 400 | Bad Request | Invalid data, duplicate username/email, self-action attempt |
| 401 | Unauthorized | Invalid or missing token |
| 403 | Forbidden | Not a superuser, inactive user |
| 404 | Not Found | User ID doesn't exist |
| 500 | Server Error | Database error, internal issue |

---

## Files Created/Modified

### New Files
- `backend/app/api/users.py` - Admin user management endpoints
- `backend/test_admin_api.py` - API testing script
- `ADMIN_USER_MANAGEMENT.md` - This documentation

### Modified Files
- `backend/app/schemas/user.py` - Added UserUpdate, PasswordReset, UserListResponse schemas
- `backend/app/main.py` - Registered users router

### Existing Files Used
- `backend/app/api/deps.py` - get_current_user, get_current_superuser dependencies
- `backend/app/utils/security.py` - Password hashing utilities
- `backend/app/models/user.py` - User model

---

## Database Query (Direct Access)

If you need to query users directly from the database:

```python
cd backend
source venv/Scripts/activate
python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def get_users():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        for user in users:
            print(f'{user.username} - {user.email} - Superuser: {user.is_superuser}')

asyncio.run(get_users())
"
```

---

## Next Steps

1. **Test the endpoints** using http://localhost:8000/docs
2. **Promote additional admins** if needed
3. **Reset passwords** for users who forgot them
4. **Monitor user activity** through the list endpoints
5. **Consider adding** user activity logs in future phases

---

## Security Reminders

⚠️ **Important**:
- Passwords are **securely hashed** and cannot be retrieved
- Only **superusers** can access these endpoints
- Cannot perform destructive actions on **your own account**
- User deletion is **permanent** and irreversible
- Always use **HTTPS in production** to protect tokens
- Rotate superuser passwords regularly
- Audit superuser access periodically

---

## Support

For issues or questions:
- Check API documentation: http://localhost:8000/docs
- Review error responses in the API
- Check backend logs for detailed errors
- Verify token is valid and not expired
