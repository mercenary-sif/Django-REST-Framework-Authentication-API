# 🔐 Django REST Framework Authentication API

A secure and production-ready authentication API built with Django REST Framework and JWT (SimpleJWT), featuring Google OAuth integration, email verification via OTP, and a complete password reset flow.

This project provides a fully functional authentication backend designed for modern web and mobile applications.

-------------

A secure authentication API built with:

- 🐍 Django
- 🔥 Django REST Framework
- 🔑 JWT (SimpleJWT)
- 🌍 Google OAuth 2.0
- 📧 Email Verification (OTP)
- 🔄 Password Reset Flow

---

## 🚀 Features

- User Registration
- JWT Login (Access + Refresh Tokens)
- Google OAuth Login
- Email Confirmation via OTP
- Password Reset with Code Verification
- Secure Password Hashing
- Token Refresh & Blacklisting

---

## 🏗️ Tech Stack

- Python 3.x
- Django
- Django REST Framework
- djangorestframework-simplejwt
- google-auth
- SQLite

---

## 📂 Project Structure

AUTHENTICATION_SYSTEM/
│
├── Auth/ # Authentication App
│ 
│
├── Authentication_System/ # Project Configuration
│ 
├── manage.py
├── .gitignore
└── requirements.txt

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
```
### 2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows

### 3️⃣ Install Dependencies

pip install -r requirements.txt
---

### 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_secret_key_here
DEBUG=True

# Database (default SQLite used)
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id_here
```

---

### 5️⃣ Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 6️⃣ Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

---

### 7️⃣ Run Development Server

```bash
python manage.py runserver
```

Server will run at:

```
http://127.0.0.1:8000/
```

---

# 🔐 Authentication Flow


---

## 1️⃣ User Registration

**POST** `/api/auth/sing-up`

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "whatsapp_number": "+213555555555",
  "password": "StrongPassword123",
  "confirm_password": "StrongPassword123"
}
```

Response:

```json
{
  "message": "New account successfully created"
}
```

---

## 2️⃣ Confirm Email (OTP Verification)

**POST** `/api/auth/confirm-email`

```json
{
  "email": "john@example.com",
  "code": "123456"
}
```

Response:

```json
{
  "message": "Email confirmé avec succès."
}
```

---

## 3️⃣ Login (Email & Password)

**POST** `/api/auth/sing-in`

```json
{
  "email": "john@example.com",
  "password": "StrongPassword123"
}
```

Response:

```json
{
  "message": "Connection successful.",
  "tokens": {
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token"
  }
}
```

---

## 4️⃣ Google OAuth Login

**POST** `/api/auth/google`

```json
{
  "token": "google_id_token_from_frontend"
}
```

Response:

```json
{
  "tokens": {
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token"
  },
  "user": {
    "email": "john@gmail.com",
    "first_name": "John",
    "last_name": "Doe",
    "profile_picture": "https://..."
  },
  "status": true
}
```

---

## 5️⃣ Refresh Token

**POST** `/api/auth/token/refresh`

```json
{
  "refresh": "your_refresh_token"
}
```

Response:

```json
{
  "message": "Successful refreshment.",
  "tokens": {
    "access": "new_access_token",
    "refresh": "new_refresh_token"
  }
}
```

---

# 🔁 Password Reset Flow

---

## 6️⃣ Request Reset Code

**POST** `/api/auth/request-reset-code`

```json
{
  "email": "john@example.com"
}
```

Response:

```json
{
  "message": "The code was sent to email: john@example.com"
}
```

---

## 7️⃣ Verify Reset Code

**POST** `/api/auth/verify-reset-code`

```json
{
  "email": "john@example.com",
  "code": "123456"
}
```

Response:

```json
{
  "message": "Reset your password. Make sure it's strong."
}
```

---

## 8️⃣ Change Password

**POST** `/api/auth/change-password`

```json
{
  "email": "john@example.com",
  "password": "NewStrongPassword123",
  "confirm_password": "NewStrongPassword123"
}
```

Response:

```json
{
  "message": "Password changed successfully."
}
```

---

# 🛡️ Security Features

- Passwords hashed using Django's built-in hashing system
- JWT Authentication (Access + Refresh tokens)
- Refresh Token Rotation
- Token Blacklisting
- OTP Expiration System
- Google ID Token Verification (Server-side)
- Environment Variables Protection

---

# 🔑 Protected Routes

To access protected routes, include:

```
Authorization: Bearer <access_token>
```

Example:

```
GET /api/protected-route
```

---

# 🧪 Testing with Postman

1. Register a new user
2. Verify email using OTP
3. Login to receive JWT tokens
4. Use Access Token for protected endpoints
5. Refresh token when expired

---

# 📦 Requirements

Main dependencies:

```
Django
djangorestframework
djangorestframework-simplejwt
google-auth
python-dotenv
```

---

# 🧠 Architecture Overview

- Custom User Model (Email as username)
- JWT Authentication (Stateless)
- Google OAuth 2.0 Integration
- OTP-based Email Verification
- Password Reset System
- Modular App Structure (Auth app)

---

# 📌 Future Improvements

- Rate limiting (throttling)
- Redis for OTP storage
- Production-ready PostgreSQL config
- Docker support
- CI/CD pipeline
- Role-based permissions (Admin/User)

---

# 👨‍💻 Author

Built with ❤️ using Django REST Framework.

---

# 📄 License

This project is open-source and available under the MIT License.
