# Quick Admin Access Guide

## Your Current Users & Passwords

**IMPORTANT**: Passwords are encrypted with bcrypt and **cannot be retrieved**. You can only:
- **Verify** passwords during login
- **Reset** passwords to new values

## All Users in Database

| Username | Email | Is Active | Is Superuser | Created |
|----------|-------|-----------|--------------|---------|
| **testuser** | test@example.com | Yes | **YES** (Admin) | 2026-01-07 |
| frontendtest | frontend@test.com | Yes | No | 2026-01-08 |
| Eugen Tamon | eus.java@gmail.com | Yes | No | 2026-01-08 |
| joy | joy@gmail.com | Yes | No | 2026-01-08 |

---

## Quick Start: Access Admin Features

### Step 1: Login as Superuser

Login with the **testuser** account (the only superuser):

```bash
# Using the API
POST http://localhost:8000/api/auth/login
{
  "username": "testuser",
  "password": "<your_password_for_testuser>"
}
```

**OR** use the browser:
1. Go to http://localhost:8000/docs
2. Click "Authorize" (top right)
3. Login with testuser credentials
4. Copy the access_token

### Step 2: View All Users

```bash
GET http://localhost:8000/api/users
Authorization: Bearer <your_token>
```

**OR** in Swagger UI (http://localhost:8000/docs):
1. Find "/api/users" endpoint
2. Click "Try it out"
3. Click "Execute"

---

## Common Admin Tasks

### Reset a User's Password

```bash
POST /api/users/{user_id}/reset-password
{
  "new_password": "newpassword123"
}
```

**Example**:
If you forgot the password for "frontendtest":
1. Get their user ID from `GET /api/users`
2. Reset password: `POST /api/users/eaf7f653-e768-4b53-86ba-045c9a8a1b7a/reset-password`

### Make Another User an Admin

```bash
POST /api/users/{user_id}/promote-superuser
```

### Deactivate a User

```bash
POST /api/users/{user_id}/deactivate
```

---

## All Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/users | List all users |
| GET | /api/users/{id} | Get user details |
| PUT | /api/users/{id} | Update user info |
| POST | /api/users/{id}/reset-password | Reset password |
| POST | /api/users/{id}/promote-superuser | Make admin |
| POST | /api/users/{id}/demote-superuser | Remove admin |
| POST | /api/users/{id}/activate | Activate account |
| POST | /api/users/{id}/deactivate | Deactivate account |
| DELETE | /api/users/{id} | Delete user |

---

## Testing the API

### Option 1: Swagger UI (Easiest)
1. Go to http://localhost:8000/docs
2. Click "Authorize"
3. Login with testuser
4. Test endpoints interactively

### Option 2: Python Script
```bash
cd backend
source venv/Scripts/activate  # Windows: venv\Scripts\activate
python test_admin_api.py
```

### Option 3: cURL
```bash
# Get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"your_password"}' \
  | jq -r '.access_token')

# List users
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/users
```

---

## Security Notes

### Why Can't I See Passwords?
- Passwords are **one-way encrypted** with bcrypt
- Even admins cannot decrypt them
- This is a **security best practice**
- You can only **reset** passwords, not view them

### What If I Forgot a Password?
1. Login as testuser (superuser)
2. Reset the user's password using `/api/users/{id}/reset-password`
3. Inform the user of their new password
4. They can change it after logging in

### Important Restrictions
- ❌ Cannot delete yourself
- ❌ Cannot deactivate yourself
- ❌ Cannot demote yourself from superuser
- ✅ Can manage all other users

---

## Files for Reference

- **Full Documentation**: [ADMIN_USER_MANAGEMENT.md](ADMIN_USER_MANAGEMENT.md)
- **API Test Script**: [backend/test_admin_api.py](backend/test_admin_api.py)
- **API Code**: [backend/app/api/users.py](backend/app/api/users.py)

---

## Need Help?

1. Check http://localhost:8000/docs for API documentation
2. Read [ADMIN_USER_MANAGEMENT.md](ADMIN_USER_MANAGEMENT.md) for detailed guide
3. View server logs in the terminal for error details

---

## Server Status

- **Backend**: http://localhost:8000 ✅ Running
- **Frontend**: http://localhost:3000 ✅ Running
- **API Docs**: http://localhost:8000/docs
- **Database**: PostgreSQL connected ✅
