from django.test import TestCase , Client
from freelancia_back_end.models import User
from freelancia_back_end.models import Project
from freelancia_back_end.models import Skill


# Create your tests here.
class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            username='abdalla',
            password='password1',
            first_name='Abdalla',
            last_name='Abo El-Magd',
            email='abdalla@freelancia.com',
            role=User.RoleChoices.freelancer
            )
        self.assertEqual(user.username, 'abdalla')
        self.assertEqual(user.email, 'abdalla@freelancia.com')
        self.assertNotEqual(user.password, 'password1')
        self.assertEqual(user.first_name, 'Abdalla')
        self.assertEqual(user.last_name, 'Abo El-Magd')
        self.assertEqual(user.role, User.RoleChoices.freelancer)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.__str__(), 'abdalla')
        self.assertEqual(user.name, 'Abdalla Abo El-Magd')

    def test_superuser_creation(self):
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@freelancia.com',
            password='admin',
            first_name='Admin',
            last_name='Admin',
        )
        self.assertEqual(superuser.username, 'admin')
        self.assertEqual(superuser.email, 'admin@freelancia.com')
        self.assertNotEqual(superuser.password, 'admin')
        self.assertEqual(superuser.first_name, 'Admin')
        self.assertEqual(superuser.last_name, 'Admin')
        self.assertEqual(superuser.role, User.RoleChoices.admin)
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.__str__(), 'admin')
        self.assertEqual(superuser.name, 'Admin Admin')
        
    def test_user_creation_without_username(self):
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                username='',
                password='password1',
                first_name='Abdalla',
                last_name='Abo El-Magd',
                email='abdalla@freelancia.com',
                role=User.RoleChoices.freelancer
                )
        self.assertEqual(str(context.exception), "The given username must be set")

    def test_user_creation_without_email(self):
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                username='abdalla',
                password='password1',
                first_name='Abdalla',
                last_name='Abo El-Magd',
                email='',
                role=User.RoleChoices.freelancer
                )
        self.assertEqual(str(context.exception), "The given email must be set")

    def test_user_creation_without_password(self):
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                username='abdalla',
                password='',
                first_name='Abdalla',
                last_name='Abo El-Magd',
                email='abdalla@freelancia.com',
                role=User.RoleChoices.freelancer
                )
        self.assertEqual(str(context.exception), "The given password must be set")

    def test_user_creation_without_first_name(self):
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                username='abdalla',
                password='password1',
                first_name='',
                last_name='Abo El-Magd',
                email='abdalla@freelancia.com',
                role=User.RoleChoices.freelancer
            )
        self.assertEqual(str(context.exception), "The given first name must be set")

    def test_user_creation_without_last_name(self):
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                username='abdalla',
                password='password1',
                first_name='Abdalla',
                last_name='',
                email='abdalla@freelancia.com',
                role=User.RoleChoices.freelancer
            )
        self.assertEqual(str(context.exception), "The given last name must be set")
    
    def test_user_creation_without_role(self):
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                username='abdalla',
                password='password1',
                first_name='Abdalla',
                last_name='Abo El-Magd',
                email='abdalla@freelancia.com'
            )
        self.assertEqual(str(context.exception), "The given role must be set")

    def test_create_user_admin(self):
        user = User.objects.create_user(
            username='admin',
            password='admin',
            first_name='Admin',
            last_name='Admin',
            email='abdalla@freelancia.com',
            role=User.RoleChoices.admin
            )
        self.assertEqual(user.username, 'admin')
        self.assertEqual(user.role, User.RoleChoices.admin)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    