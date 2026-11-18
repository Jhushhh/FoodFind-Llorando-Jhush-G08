# FoodFind – Campus Food-Finding and Budget Guide (Account Feature)

Full-stack Django (templates) with PostgreSQL/Supabase.

## Setup
```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # Mac/Linux: cp .env.example .env  -> then edit .env
python manage.py migrate
python manage.py createsuperuser   # this account gets the Admin role
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Roles
- **Student** – everyone who registers through the form.
- **Admin** – created with `createsuperuser` (or change a user's role in `/django-admin/`).

## Pages
| URL | Who |
|---|---|
| /register/, /login/ | everyone |
| /dashboard/ | redirects by role |
| /dashboard/student/ | students only |
| /dashboard/admin/ | admins only (others get 403) |
| /profile/, /profile/edit/ | logged-in user (own profile only) |

## Tests
`python manage.py test accounts`
