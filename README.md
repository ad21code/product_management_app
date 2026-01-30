# Flask E-Commerce Store with Stripe Integration

A full-stack e-commerce application built with Python (Flask) and Stripe. This project demonstrates a complete product management system with a secure checkout flow, shopping cart functionality, and an admin dashboard.

## 🚀 Features

* **User Interface:**
    * Modern, responsive design using **Bootstrap 5** and custom CSS.
    * "Lag-free" shopping cart with instant quantity updates (AJAX).
    * Mobile-friendly navigation with a hamburger menu.
* **E-Commerce Functionality:**
    * Browse products with image, title, and price.
    * Add to cart, update quantities, and remove items.
    * Real-time cart total calculation.
* **Payment Integration:**
    * Secure checkout using **Stripe Checkout API**.
    * Webhooks/Success routing to verify payments server-side.
* **Admin Dashboard:**
    * Add new products (Title, Image URL, Price).
    * View transaction history with timestamp, status, and session IDs.
* **Backend:**
    * **Flask** framework with Blueprints for modular architecture.
    * **SQLite** database with **SQLAlchemy** ORM.

## 🛠️ Tech Stack

* **Backend:** Python, Flask, SQLAlchemy
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API), Bootstrap 5, Jinja2 Templating
* **Database:** SQLite (dev), compatible with PostgreSQL/MySQL
* **Payments:** Stripe API

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR_USERNAME/flask-ecommerce-stripe.git](https://github.com/YOUR_USERNAME/flask-ecommerce-stripe.git)
cd flask-ecommerce-stripe
