# ♻️ EcoCollect Backend

EcoCollect Backend is built using Django REST Framework and provides REST APIs for managing e-waste collection requests, recyclers, rewards, notifications, and chat functionality.

---

## 🚀 Features

- JWT Authentication
- Custom User Model
- Role-Based Authorization
- Waste Categories
- Pickup Request Management
- Recycler Assignment
- Reward System
- Notifications
- Chat System
- Ratings & Reviews
- REST APIs

---

## 🛠 Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- SimpleJWT
- Pillow
- CORS Headers

---

## 📂 Project Structure

```
EcoCollect/
│
├── api/
├── media/
├── EcoCollect/
├── manage.py
├── requirements.txt
└── .env
```

---

## ⚙️ Installation

Clone repository

```bash
git clone https://github.com/vigneshkumar1446/ecocollect-backend.git
```

Navigate

```bash
cd ecocollect-backend
```

Create virtual environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Linux

```bash
source .venv/bin/activate
```

Install packages

```bash
pip install -r requirements.txt
```

Create `.env`

```env
SECRET_KEY=your_secret_key

DEBUG=True

DATABASE_URL=postgresql://username:password@localhost:5432/ecocollect

ALLOWED_HOSTS=127.0.0.1,localhost
```

Run migrations

```bash
python manage.py migrate
```

Create superuser

```bash
python manage.py createsuperuser
```

Run server

```bash
python manage.py runserver
```

---

## 🔐 Authentication

JWT Authentication

Obtain Token

```http
POST /api/token/
```

Refresh Token

```http
POST /api/token/refresh/
```

---

## 📚 API Endpoints

### Authentication

```
POST /api/register/
POST /api/token/
POST /api/token/refresh/
```

### Categories

```
GET /api/categories/
POST /api/categories/
```

### Pickup Requests

```
GET /api/pickups/
POST /api/pickups/
```

### Recycler Assignments

```
GET /api/assignments/
```

### Ratings

```
GET /api/rating/
POST /api/rating/
```

### Notifications

```
GET /api/notifications/
```

### Chat

```
GET /api/chatrooms/
GET /api/messages/
```

---

## Database Models

- User
- WasteCategory
- PickupRequest
- RecyclerAssignment
- Reward
- Rating
- Notification
- ChatRoom
- ChatBox

---

## Deployment

Backend

- Render

Database

- PostgreSQL

---

## Developed By

**Vignesh Kumar**

LinkedIn

https://www.linkedin.com/in/vignesh-kumar-34212629b/

GitHub

https://github.com/vigneshkumar1446
