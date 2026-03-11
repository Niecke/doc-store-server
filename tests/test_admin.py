"""
Tests for the admin blueprint: dashboard, user_create, user_delete, user_edit.
"""
import pytest
from html import unescape
from conftest import do_login, do_logout
from models import db, User, Role


def html_text(response):
    """Decode response body and unescape HTML entities (e.g. &#34; → ")."""
    return unescape(response.data.decode())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def login_admin(client, admin_user):
    do_login(client, "admin@test.com", "AdminPass123!")


def login_regular(client, regular_user):
    do_login(client, "user@test.com", "UserPass123!")


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class TestAdminDashboard:
    def test_dashboard_requires_login(self, client):
        response = client.get("/admin/dashboard", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

    def test_dashboard_requires_admin_role(self, client, regular_user):
        login_regular(client, regular_user)
        response = client.get("/admin/dashboard", follow_redirects=True)
        # Should redirect to index with error flash, not show dashboard
        assert response.status_code == 200
        html = html_text(response)
        assert 'Role "admin" required!' in html

    def test_dashboard_accessible_to_admin(self, client, admin_user):
        login_admin(client, admin_user)
        response = client.get("/admin/dashboard")
        assert response.status_code == 200

    def test_dashboard_lists_users(self, client, admin_user, regular_user):
        login_admin(client, admin_user)
        response = client.get("/admin/dashboard")
        html = response.data.decode()
        assert "admin@test.com" in html
        assert "user@test.com" in html


# ---------------------------------------------------------------------------
# User create
# ---------------------------------------------------------------------------

class TestAdminUserCreate:
    def test_user_create_requires_login(self, client):
        response = client.get("/admin/user_create", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

    def test_user_create_get_shows_form(self, client, admin_user):
        login_admin(client, admin_user)
        response = client.get("/admin/user_create")
        assert response.status_code == 200
        html = response.data.decode()
        assert "email" in html.lower()
        assert "password" in html.lower()

    def test_user_create_post_valid_creates_user(self, client, admin_user):
        login_admin(client, admin_user)
        response = client.post(
            "/admin/user_create",
            data={
                "email": "newuser@test.com",
                "password": "NewUserPass1!",
                "active": "on",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        html = html_text(response)
        assert 'User "newuser@test.com" created successfully!' in html

        # Verify the user actually exists in the database
        from sqlalchemy import select
        user = db.session.execute(
            select(User).where(User.email == "newuser@test.com")
        ).scalar_one_or_none()
        assert user is not None
        assert user.active is True

    def test_user_create_post_inactive_user(self, client, admin_user):
        login_admin(client, admin_user)
        client.post(
            "/admin/user_create",
            data={"email": "inactive_new@test.com", "password": "SomePass1!"},
            follow_redirects=True,
        )
        from sqlalchemy import select
        user = db.session.execute(
            select(User).where(User.email == "inactive_new@test.com")
        ).scalar_one_or_none()
        assert user is not None
        assert user.active is False  # 'active' not in form data

    def test_user_create_duplicate_email_shows_error(self, client, admin_user, regular_user):
        login_admin(client, admin_user)
        response = client.post(
            "/admin/user_create",
            data={"email": "user@test.com", "password": "SomePass1!"},
            follow_redirects=True,
        )
        html = response.data.decode()
        assert "Email already exists!" in html

    def test_user_create_password_too_short_shows_error(self, client, admin_user):
        login_admin(client, admin_user)
        response = client.post(
            "/admin/user_create",
            data={"email": "short@test.com", "password": "short"},
            follow_redirects=True,
        )
        # Should stay on the create page with a validation error
        assert response.status_code == 200
        html = response.data.decode()
        # The ValueError message from set_password is flashed
        assert "Password needs to be longer than" in html or "error" in html.lower()

    def test_user_create_preserves_email_on_password_error(self, client, admin_user):
        login_admin(client, admin_user)
        response = client.post(
            "/admin/user_create",
            data={"email": "preserved@test.com", "password": "sh"},
            follow_redirects=True,
        )
        html = response.data.decode()
        assert "preserved@test.com" in html

    def test_user_create_requires_admin_role(self, client, regular_user):
        login_regular(client, regular_user)
        response = client.get("/admin/user_create", follow_redirects=True)
        html = html_text(response)
        assert 'Role "admin" required!' in html


# ---------------------------------------------------------------------------
# User delete
# ---------------------------------------------------------------------------

class TestAdminUserDelete:
    def test_user_delete_requires_login(self, client, regular_user):
        response = client.post(
            f"/admin/user_delete/{regular_user.id}", follow_redirects=False
        )
        assert response.status_code == 302
        assert "/login" in response.location

    def test_user_delete_requires_admin_role(self, client, regular_user):
        login_regular(client, regular_user)
        response = client.post(
            f"/admin/user_delete/{regular_user.id}", follow_redirects=True
        )
        html = html_text(response)
        assert 'Role "admin" required!' in html

    def test_user_delete_removes_user(self, client, admin_user, regular_user):
        user_id = regular_user.id
        login_admin(client, admin_user)
        response = client.post(
            f"/admin/user_delete/{user_id}", follow_redirects=True
        )
        assert response.status_code == 200
        html = response.data.decode()
        assert 'deleted!' in html

        # Confirm user is gone from the database
        assert db.session.get(User, user_id) is None

    def test_user_delete_unknown_id_shows_error(self, client, admin_user):
        login_admin(client, admin_user)
        response = client.post(
            "/admin/user_delete/99999", follow_redirects=True
        )
        html = response.data.decode()
        assert "unknown" in html

    def test_user_delete_internal_admin_blocked(self, client, admin_user):
        # Create a user whose email is literally "admin" (the internal guard)
        protected = User(email="admin", active=True)
        protected.set_password("ProtectedPass1!")
        db.session.add(protected)
        db.session.commit()

        login_admin(client, admin_user)
        response = client.post(
            f"/admin/user_delete/{protected.id}", follow_redirects=True
        )
        html = response.data.decode()
        assert "internal admin user can not be deleted" in html
        # Confirm user still exists
        assert db.session.get(User, protected.id) is not None

    def test_user_delete_requires_post(self, client, admin_user, regular_user):
        login_admin(client, admin_user)
        response = client.get(f"/admin/user_delete/{regular_user.id}")
        assert response.status_code == 405


# ---------------------------------------------------------------------------
# User edit (not implemented)
# ---------------------------------------------------------------------------

class TestAdminUserEdit:
    def test_user_edit_requires_login(self, client):
        response = client.get("/admin/user_edit/1", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

    def test_user_edit_redirects_with_not_implemented(self, client, admin_user):
        login_admin(client, admin_user)
        response = client.get(
            f"/admin/user_edit/{admin_user.id}", follow_redirects=True
        )
        html = response.data.decode()
        assert "Not implemented yet" in html

    def test_user_edit_post_also_redirects(self, client, admin_user):
        login_admin(client, admin_user)
        response = client.post(
            f"/admin/user_edit/{admin_user.id}", follow_redirects=True
        )
        html = response.data.decode()
        assert "Not implemented yet" in html
