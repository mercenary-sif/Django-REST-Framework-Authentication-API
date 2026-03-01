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
│ ├── migrations/
│ │   └── __init__.py
│ ├── admin.py
│ ├── apps.py
│ ├── emailSender.py # Email OTP logic
│ ├── models.py # Custom User model
│ ├── serializers.py # DRF serializers
│ ├── tokens.py # JWT handling logic
│ ├── views.py # API views
│ ├── urls.py # App routes
│ └── tests.py
│
├── Authentication_System/ # Project Configuration
│ ├── settings.py
│ ├── urls.py
│ ├── asgi.py
│ └── wsgi.py
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

## 📌 1. User Registration

**POST** `/api/auth/sign-up`

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "whatsapp_number": "0555555555",
  "password": "StrongPassword123",
  "confirm_password": "StrongPassword123"
}
```

Response:

```json
{
  "status": 200,
  "message": "User created successfully. Verification code sent to email."
}
```

---

## 📧 2. Email Verification (OTP)

**POST** `/api/auth/verify-code`

```json
{
  "email": "john@example.com",
  "code": "123456"
}
```

---

## 🔑 3. Login with JWT

**POST** `/api/auth/login`

```json
{
  "email": "john@example.com",
  "password": "StrongPassword123"
}
```

Response:

```json
{
  "access": "your_access_token",
  "refresh": "your_refresh_token"
}
```

---

## 🔄 4. Refresh Token

**POST** `/api/auth/token/refresh`

```json
{
  "refresh": "your_refresh_token"
}
```

---

## 🌍 5. Google OAuth Login

**POST** `/api/auth/google`

```json
{
  "token": "google_id_token_from_frontend"
}
```

The backend verifies the Google token and:

- Creates a new user if not exists
- Logs in the existing user
- Returns JWT tokens

---

## 🔁 6. Forgot Password

**POST** `/api/auth/forgot-password`

```json
{
  "email": "john@example.com"
}
```

---

## 🔄 7. Reset Password

**POST** `/api/auth/reset-password`

```json
{
  "email": "john@example.com",
  "code": "123456",
  "new_password": "NewStrongPassword123"
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
