from django.test import Client, TestCase
from .models import Review
from freelancia_back_end.models import User
from freelancia_back_end.models import Project # Adjust the import according to your project structure

class ReviewsModelTest(TestCase):

    def setUp(self):
        self.reviewer = User.objects.create_user(
            username='ahmed', 
            password='password1',
            email='ahmed@example.com'  
        )
        
        self.reviewed = User.objects.create_user(
            username='mohamed', 
            password='password2',
            email='mohamed@example.com' 
        )
        
        self.project = Project.objects.create(
            project_name='1',
            suggested_budget=1000,
            expected_deadline=10,
            owner_id=self.reviewer
          
        )
    
    def test_view_model(self):
        riview = Review.objects.create(
            message="This is a test message",
            rate=5,
            user_reviewr=self.reviewer,
            user_reviewed=self.reviewed,
            project=self.project
        )

        self.assertEqual(riview.message, "This is a test message")
        self.assertEqual(riview.rate, 5)
        self.assertEqual(riview.__str__(), "ahmed - mohamed - 1")  



class ViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.reviewer = User.objects.create_user(
            username='ahmed', 
            password='password1',
            email='ahmed@example.com'  
        )
        self.reviewed = User.objects.create_user(
            username='mohamed', 
            password='password2',
            email='mohamed@example.com' 
        )
        
        self.project = Project.objects.create(
            project_name='1',
            suggested_budget=1000,
            expected_deadline=10,
            owner_id=self.reviewer
          
        )

    def test_get_reviews(self):
        response = self.client.get(f'/reviews/received/user/{self.reviewer.id}')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'message': 'The user does not have any reviews'})


    def test_get_user_reviwes(self):
        response = self.client.get(f'/reviews/made/user/{self.reviewer.id}')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'message': 'The user does not have any reviews'})

    def test_create_review(self):
        response=self.client.post('/reviews/create',{
            'user_reviewr':self.reviewer.id,
            'user_reviewed':self.reviewed.id,
            'rate':5,
            'project':self.project.id,
            'message':'This is a test message'
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], 'This is a test message')
        self.assertEqual(response.json()['rate'], 5)


    def test_update_review(self):
            review = Review.objects.create(
                message="This is a test message",
                rate=5,
                user_reviewr=self.reviewer,
                user_reviewed=self.reviewed,
                project=self.project
            )

            login_response = self.client.post('/auth-token/', {
                'username': 'ahmed',
                'password': 'password1'
            })
            token = login_response.json()['access']
            
            response = self.client.patch(
                f'/reviews/update/{review.id}',
                {
                    'message': 'This is a test message',
                    'rate': 4
                },
                HTTP_AUTHORIZATION=f'Bearer {token}',
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['rate'], 4)
            self.assertEqual(response.json()['message'], 'This is a test message')

    def test_delete_review(self):
        review = Review.objects.create(
            message="This is a test message",
            rate=5,
            user_reviewr=self.reviewer,
            user_reviewed=self.reviewed,
            project=self.project
        )
        login_response = self.client.post('/auth-token/', {
            'username': 'ahmed',
            'password': 'password1'
        })
        token = login_response.json()['access']
        response = self.client.delete(
            f'/reviews/delete/{review.id}',
            HTTP_AUTHORIZATION=f'Bearer {token}'    
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Review.objects.filter(id=review.id).exists())