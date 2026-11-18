from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user("stud", "stud@example.com", "StrongPass123!")
        self.admin = User.objects.create_superuser("boss", "boss@example.com", "StrongPass123!")

    def test_register_hashes_password_and_makes_student(self):
        data = {"first_name": "A", "last_name": "B", "username": "newuser", "email": "new@example.com",
                "contact_number": "0917", "password1": "StrongPass123!", "password2": "StrongPass123!"}
        r = self.client.post(reverse("register"), data)
        self.assertRedirects(r, reverse("login"))
        u = User.objects.get(username="newuser")
        self.assertNotEqual(u.password, "StrongPass123!")
        self.assertTrue(u.password.startswith("pbkdf2_"))
        self.assertEqual(u.profile.role, "student")

    def test_register_validation(self):
        base = {"first_name": "A", "last_name": "B", "username": "x1", "email": "stud@example.com",
                "password1": "StrongPass123!", "password2": "StrongPass123!"}
        self.assertContains(self.client.post(reverse("register"), base), "already exists")
        bad = dict(base, email="not-an-email")
        self.assertEqual(User.objects.filter(username="x1").count(), 0)
        self.client.post(reverse("register"), bad)
        self.assertEqual(User.objects.filter(username="x1").count(), 0)
        mismatch = dict(base, email="ok@example.com", password2="different")
        self.client.post(reverse("register"), mismatch)
        self.assertEqual(User.objects.filter(username="x1").count(), 0)

    def test_login_invalid_and_valid(self):
        r = self.client.post(reverse("login"), {"username": "stud", "password": "wrong"})
        self.assertContains(r, "Invalid username or password")
        r = self.client.post(reverse("login"), {"username": "stud", "password": "StrongPass123!"}, follow=True)
        self.assertRedirects(r, reverse("student_dashboard"))

    def test_admin_goes_to_admin_dashboard(self):
        self.client.login(username="boss", password="StrongPass123!")
        self.assertRedirects(self.client.get(reverse("dashboard")), reverse("admin_dashboard"))

    def test_login_required_redirects(self):
        for name in ("dashboard", "student_dashboard", "admin_dashboard", "profile", "profile_edit"):
            r = self.client.get(reverse(name))
            self.assertRedirects(r, f"{reverse('login')}?next={reverse(name)}", fetch_redirect_response=False)

    def test_role_isolation(self):
        self.client.login(username="stud", password="StrongPass123!")
        self.assertEqual(self.client.get(reverse("admin_dashboard")).status_code, 403)
        self.client.logout()
        self.client.login(username="boss", password="StrongPass123!")
        self.assertEqual(self.client.get(reverse("student_dashboard")).status_code, 403)

    def test_logout_ends_session(self):
        self.client.login(username="stud", password="StrongPass123!")
        self.client.post(reverse("logout"))
        self.assertEqual(self.client.get(reverse("profile")).status_code, 302)

    def test_profile_update_only_own(self):
        self.client.login(username="stud", password="StrongPass123!")
        r = self.client.post(reverse("profile_edit"), {"first_name": "New", "last_name": "Name",
                             "email": "stud@example.com", "contact_number": "09999"})
        self.assertRedirects(r, reverse("profile"))
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "New")
        self.assertEqual(self.student.profile.contact_number, "09999")
        self.admin.refresh_from_db()
        self.assertNotEqual(self.admin.first_name, "New")
