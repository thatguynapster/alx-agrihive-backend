# 🌾 AgriHive Backend

AgriHive is a backend-only Django REST Framework (DRF) project that connects **farmers, buyers, and transporters** in a digital agriculture marketplace.

The system allows:

-   **Farmers** → to list products for sale.
-   **Buyers** → to place orders and review products.
-   **Transporters** → to be assigned delivery tasks.
-   **Admins** → to manage everything.

---

## ⚙️ Tech Stack

-   [Python 3.12+](https://www.python.org/)
-   [Django 5](https://www.djangoproject.com/)
-   [Django REST Framework](https://www.django-rest-framework.org/)
-   SQLite (default, switchable to PostgreSQL/MySQL)

---

## 🚀 Setup Instructions

1. **Clone the repository**

    ```bash
    git clone https://github.com/yourusername/alx-agrihive-backend.git
    cd alx-agrihive-backend
    ```

2. **Create & activate virtual environment**

    ```bash
    python -m venv .venv
    source .venv/bin/activate   # Linux/Mac
    .venv\Scripts\activate      # Windows
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run migrations**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **Start server**

    ```bash
    python manage.py runserver
    ```

6. **Run tests**
    ```bash
    python manage.py test
    ```

---

## 📍 API Routes Overview

### 1. **Authentication & Users**

-   `POST /api/auth/register/` → register new user (farmer, buyer, transporter).
-   `POST /api/auth/login/` → login user, returns token.
-   `GET /api/users/` → list users (admin only).
-   `GET /api/users/<id>/` → get user detail (self or admin).

#### Example: Register

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/   -H "Content-Type: application/json"   -d '{"name": "Alice", "email": "alice@test.com", "password": "1234", "role": "buyer"}'
```

---

### 2. **Categories**

-   `GET /api/categories/` → list categories.
-   `POST /api/categories/` → create (admin only).
-   `GET /api/categories/<id>/` → retrieve category.
-   `PUT/PATCH /api/categories/<id>/` → update category (admin).
-   `DELETE /api/categories/<id>/` → delete category (admin).

#### Example: Create Category

```bash
curl -X POST http://127.0.0.1:8000/api/categories/   -H "Authorization: Token <ADMIN_TOKEN>"   -H "Content-Type: application/json"   -d '{"name": "Fruits", "description": "Fresh fruits"}'
```

---

### 3. **Products**

-   `GET /api/products/` → list all products.
-   `POST /api/products/` → create product (farmer only).
-   `GET /api/products/<id>/` → retrieve product.
-   `PUT/PATCH /api/products/<id>/` → update (farmer owner or admin).
-   `DELETE /api/products/<id>/` → delete (farmer owner or admin).

#### Example: Create Product

```bash
curl -X POST http://127.0.0.1:8000/api/products/   -H "Authorization: Token <FARMER_TOKEN>"   -H "Content-Type: application/json"   -d '{"name": "Bananas", "description": "Sweet bananas", "price": 10.5, "quantity": 20, "unit": "kg", "category": 1}'
```

---

### 4. **Orders**

-   `GET /api/orders/` → list orders (buyer sees own, admin sees all).
-   `POST /api/orders/` → create order (buyer only).
-   `GET /api/orders/<id>/` → retrieve order (buyer own or admin).
-   `PATCH /api/orders/<id>/` → update order (admin only).
-   `DELETE /api/orders/<id>/` → delete order (admin only).

#### Example: Buyer Creates Order

```bash
curl -X POST http://127.0.0.1:8000/api/orders/   -H "Authorization: Token <BUYER_TOKEN>"   -H "Content-Type: application/json"   -d '{"product": 1, "quantity": 3}'
```

✅ Response:

```json
{
	"id": 1,
	"buyer": 2,
	"product": 1,
	"product_name": "Bananas",
	"quantity": 3,
	"total_price": "31.50",
	"status": "pending",
	"order_date": "2025-08-30T12:20:00Z"
}
```

---

## ✅ Summary of Permissions

-   **Buyers** → can register, login, browse products, create orders, leave reviews.
-   **Farmers** → can register, login, manage their own products.
-   **Admins** → full access (categories, orders, products, assignments).

---

## 🧪 Running Tests

```bash
python manage.py test
```

Covers:

-   Authentication
-   Users permissions
-   Categories CRUD
-   Products CRUD
-   Orders CRUD (buyer & admin behaviors)
