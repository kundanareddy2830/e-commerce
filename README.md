# WishMart – Modern Django E‑Commerce Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Built With Django 4.2](https://img.shields.io/badge/Django-4.2-blue.svg)](https://www.djangoproject.com/)

A production‑ready, extensible e‑commerce platform built with **Django 4.2**. Use it as a learning project, a demo for clients, or the foundation for your own online store.

> “Everything you need to start selling – nothing you don’t.”

---

## ✨ Highlights

* **Authentication & Accounts** – registration, social logins, password reset
* **Product Catalogue** – categories, variants, stock & price management
* **Shopping Cart & Checkout** – guest carts, address book, coupons
* **Payments** – Stripe integration wired for live mode
* **Reviews & Ratings** – verified‑purchase enforcement
* **Search & Filters** – full‑text search, faceted filtering, pagination
* **Email Workflows** – order confirmation, welcome series, password reset
* **Responsive UI** – Bootstrap‑inspired, mobile‑first design
* **Security First** – CSRF, secure headers, .env secrets, OWASP hardening

---


A live demo is available at **[https://wishmart-demo.onrender.com]((https://e-commerce-n5fz.onrender.com))** (read‑only sandbox).

---

## ⚙️ Architecture Overview

```
┌───────────┐     HTTP      ┌──────────────┐
│   Client  │ ───────────▶ │   Django     │
│ (Bootstrap│              │  Views/API   │
└───────────┘              └──────┬───────┘
                                  │ ORM
                            ┌─────▼───────┐
                            │ PostgreSQL  │
                            └─────────────┘
                                  │
                            ┌─────▼───────┐
                            │   Stripe    │ (payments)
                            └─────────────┘
```

*Stateless¹ views + signed cookies keep sessions lightweight; background tasks can be wired via Celery/RQ if your store outgrows sync email dispatch.*

---

## 🛠 Tech Stack

| Layer     | Choice                                   | Why                                     |
| --------- | ---------------------------------------- | --------------------------------------- |
| Framework | **Django 4.2**                           | Reliable, batteries‑included            |
| Database  | **SQLite** (dev) → **PostgreSQL** (prod) | Zero‑setup locally, rock‑solid in prod  |
| Front‑End | HTML • CSS • Alpine.js (optional)        | Simplicity first; swap for React easily |
| Payments  | **Stripe**                               | PCI compliant, global                   |
| Deploy    | Gunicorn + Whitenoise on **Render**      | Zero‑Ops container hosting              |

---

## 🚀 Quick Start

```bash
# 1 Clone
$ git clone https://github.com/your‑org/wishmart.git
$ cd wishmart

# 2 Create & activate virtualenv (Python ≥ 3.10)
$ python -m venv .env
$ source .env/bin/activate  # Windows: .env\Scripts\activate

# 3 Install Python deps
$ pip install -r requirements.txt

# 4 Configure secrets
$ cp env.example .env           # edit values ↗

# 5 Initialise DB + seed demo data (optional)
$ python manage.py migrate
$ python manage.py loaddata seed

# 6 Run server
$ python manage.py runserver

# Visit: http://127.0.0.1:8000/
```

> **Heads‑up** — The default `stripe_*` keys in `env.example` run against Stripe’s **test mode**. Swap them before going live.

---

## 🏗 Project Layout

```
wishmart/
├── ecommerce/       # Site settings & ASGI/WSGI entrypoints
├── store/           # Domain apps (catalogue, cart, orders, users)
├── templates/       # Django templates (Jinja‑like)
├── static/          # CSS, JS, images served by Whitenoise
├── media/           # User uploads (S3/CloudFront in prod)
└── tests/           # Pytest suites
```

Clean separation keeps migrations uncoupled from presentation code, so front‑end rewrites (HTMX, React …) never touch your data layer.

---

## 🧑‍💻 Development Workflow

| Task                    | Command                          |
| ----------------------- | -------------------------------- |
| Lint & style‑check      | `make lint` (ruff + black)       |
| Run tests               | `pytest -q`                      |
| Generate coverage badge | `coverage html`                  |
| Collect static (prod)   | `python manage.py collectstatic` |

A pre‑commit hook is configured – commit will fail if linting or tests break.

---

## 🚢 Deploying to Render (1‑Click)

1. **Fork → Connect** the repo in Render.
2. Add environment variables shown in **`env.example`**.
3. Set the build command:

   ```bash
   pip install -r requirements.txt && python manage.py migrate --noinput
   ```
4. Start command:

   ```bash
   gunicorn ecommerce.wsgi --log-file -
   ```
5. Add a free PostgreSQL add‑on & swap `DATABASE_URL`.

> Need autoscaling, background workers or CDN? See the [deployment guide](docs/deploy.md).

---

## 🤝 Contributing

1. **Fork** the project & create your branch: `git checkout -b feature/x`
2. **Commit** your changes with clear messages.
3. **Push** to the branch & open a Pull Request.

Please run `make ci` locally before pushing – CI will mirror the same pipeline.

---

## 📜 License

[MIT](LICENSE) © 2025 Kundana Reddy

---

> **Enjoying WishMart?** ⭐ Star the repo to keep me caffeinated!
