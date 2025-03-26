from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from freelancia_back_end.models import Project, User, Skill

class ProjectModelTest(TestCase):
    def setUp(self):
        # test for user kda 3la el ma4y 
        self.user = User.objects.create_user(
            username='project_owner',
            password='password123',
            email='owner@freelancia.com',
            first_name='Test',
            last_name='User',
            role=User.RoleChoices.client
        )
        
        # تعديل اسم الحقل ليتوافق مع نموذج Skill
        self.skill1 = Skill.objects.create(skill='Python')
        self.skill2 = Skill.objects.create(skill='Django')

    def test_project_creation_with_valid_data(self):
        project = Project.objects.create(
            owner_id=self.user,
            project_name='Test Project',
            project_description='A test project description',
            suggested_budget=Decimal('1000.00'),
            expected_deadline=30
        )
        project.skills.add(self.skill1, self.skill2)

        self.assertEqual(project.project_name, 'Test Project')
        self.assertEqual(project.project_description, 'A test project description')
        self.assertEqual(project.owner_id, self.user)
        self.assertEqual(project.suggested_budget, Decimal('1000.00'))
        self.assertEqual(project.expected_deadline, 30)
        self.assertEqual(project.project_state, Project.StatusChoices.open)
        self.assertEqual(project.skills.count(), 2)
        self.assertIn(self.skill1, project.skills.all())
        self.assertIn(self.skill2, project.skills.all())

    def test_project_string_representation(self):
        project = Project.objects.create(
            owner_id=self.user,
            project_name='Test Project',
            project_description='Description',
            suggested_budget=Decimal('1000.00'),
            expected_deadline=30
        )
        self.assertEqual(str(project), 'Test Project')

    def test_project_state_transitions(self):
        project = Project.objects.create(
            owner_id=self.user,
            project_name='State Test Project',
            project_description='Description',
            suggested_budget=Decimal('1000.00'),
            expected_deadline=30
        )
        
        # el transitions
        self.assertEqual(project.project_state, Project.StatusChoices.open)
        
        project.project_state = Project.StatusChoices.ongoing
        project.save()
        self.assertEqual(project.project_state, Project.StatusChoices.ongoing)
        
        project.project_state = Project.StatusChoices.finished
        project.save()
        self.assertEqual(project.project_state, Project.StatusChoices.finished)

    def test_project_with_invalid_budget(self):
        project = Project.objects.create(
            owner_id=self.user,
            project_name='Invalid Budget Project',
            project_description='Description',
            suggested_budget=Decimal('-100.00'), # negative test
            expected_deadline=30
        )
        self.assertTrue(project.suggested_budget < 0)

    def test_project_with_invalid_deadline(self):
        project = Project.objects.create(
            owner_id=self.user,
            project_name='Invalid Deadline Project',
            project_description='Description',
            suggested_budget=Decimal('1000.00'),
            expected_deadline=-1  # negative deadline
        )
        self.assertTrue(project.expected_deadline < 0)

    def test_project_creation_timestamps(self):
        project = Project.objects.create(
            owner_id=self.user,
            project_name='Timestamp Test Project',
            project_description='Description',
            suggested_budget=Decimal('1000.00'),
            expected_deadline=30
        )
        
        self.assertIsNotNone(project.created_at)
        self.assertIsNotNone(project.updated_at)
        
        # test on updated at 
        original_updated_at = project.updated_at
        project.project_name = 'Updated Project Name'
        project.save()
        self.assertNotEqual(project.updated_at, original_updated_at)

    def test_project_skills_management(self):
        project = Project.objects.create(
            owner_id=self.user,
            project_name='Skills Test Project',
            project_description='Description',
            suggested_budget=Decimal('1000.00'),
            expected_deadline=30
        )
        
        #skills test add , remove , clear

        # test adding skills
        project.skills.add(self.skill1)
        self.assertEqual(project.skills.count(), 1)
        
        # test adding multiple skills
        project.skills.add(self.skill2)
        self.assertEqual(project.skills.count(), 2)
        
        # test removing skills
        project.skills.remove(self.skill1)
        self.assertEqual(project.skills.count(), 1)
        self.assertNotIn(self.skill1, project.skills.all())
        
        # test clearing all skills
        project.skills.clear()
        self.assertEqual(project.skills.count(), 0)