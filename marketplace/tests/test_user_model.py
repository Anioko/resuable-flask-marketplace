import time
import unittest

from app import create_app, db
from app.models import AnonymousUser, Permission, Role, User


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='password')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='password')
        with self.assertRaises(AttributeError):
            u.password()

    def test_password_verification(self):
        u = User(password='password')
        self.assertTrue(u.verify_password('password'))
        self.assertFalse(u.verify_password('notpassword'))

    def test_password_salts_are_random(self):
        u = User(password='password')
        u2 = User(password='password')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm_account(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='password')
        u2 = User(password='notpassword')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm_account(token))

    def test_expired_confirmation_token(self):
        u = User(password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm_account(token))

    def test_valid_reset_token(self):
        u = User(password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_password_reset_token()
        self.assertTrue(u.reset_password(token, 'notpassword'))
        self.assertTrue(u.verify_password('notpassword'))

    def test_invalid_reset_token(self):
        u1 = User(password='password')
        u2 = User(password='notpassword')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_password_reset_token()
        self.assertFalse(u2.reset_password(token, 'notnotpassword'))
        self.assertTrue(u2.verify_password('notpassword'))

    def test_valid_email_change_token(self):
        u = User(email='user@example.com', password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('otheruser@example.org')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'otheruser@example.org')

    def test_invalid_email_change_token(self):
        u1 = User(email='user@example.com', password='password')
        u2 = User(email='otheruser@example.org', password='notpassword')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('otherotheruser@example.net')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'otheruser@example.org')

    def test_duplicate_email_change_token(self):
        u1 = User(email='user@example.com', password='password')
        u2 = User(email='otheruser@example.org', password='notpassword')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('user@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'otheruser@example.org')

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='user@example.com', password='password')
        self.assertTrue(u.can(Permission.GENERAL))
        self.assertFalse(u.can(Permission.ADMINISTER))

    def test_make_administrator(self):
        Role.insert_roles()
        u = User(email='user@example.com', password='password')
        self.assertFalse(u.can(Permission.ADMINISTER))
        u.role = Role.query.filter_by(
            permissions=Permission.ADMINISTER).first()
        self.assertTrue(u.can(Permission.ADMINISTER))

    def test_administrator(self):
        Role.insert_roles()
        r = Role.query.filter_by(permissions=Permission.ADMINISTER).first()
        u = User(email='user@example.com', password='password', role=r)
        self.assertTrue(u.can(Permission.ADMINISTER))
        self.assertTrue(u.can(Permission.GENERAL))
        self.assertTrue(u.is_admin())

    def test_anonymous(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.GENERAL))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])
