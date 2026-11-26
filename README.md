# E-commerce Storefront (Flask)

A learning storefront with product search, a session cart, and a demo checkout.

## Stack
Python 3, Flask, Flask-SQLAlchemy (SQLite), HTML, CSS, vanilla JavaScript.

## Changes in this customized version
- Category and text search
- Cart quantity updates and stock checks
- Checkout creates a persistent order and reduces stock
- No real payment processing

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. The app creates a local SQLite database and sample products on first run.

## Source and attribution
Feature inspiration: [kolosochok/django-ecommerce](https://github.com/kolosochok/django-ecommerce), MIT License. This repository contains a simplified, reworked implementation for practice; original copyright notice is retained in LICENSE.

Demo only: use fictional data. Do not enter real payment details.
