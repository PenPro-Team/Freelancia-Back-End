import os
import random
import string
from django.core.management.base import BaseCommand
from freelancia_back_end.models import User
from django.core.files.base import ContentFile
from datetime import datetime

class Command(BaseCommand):
    help = 'Create 10 users (4 clients, 6 freelancers) with rate=5 and predefined images'

    def __init__(self):
        super().__init__()
        self.used_numbers = set() 

    def handle(self, *args, **kwargs):
        image_folder = 'attachments/media'
        image_files = [f for f in os.listdir(image_folder) if f.endswith(('jpg', 'jpeg', 'png'))]
        if len(image_files) < 10:
            self.stdout.write(self.style.ERROR('You need at least 10 images in the attachments/ folder'))
            return
        image_files.sort()
        for i in range(4):
            self.create_user(
                role="client", 
                image_file=image_files[i], 
                rate=5
            )
        for i in range(4, 10):
            self.create_user(
                role="freelancer", 
                image_file=image_files[i], 
                rate=5
            )

    def generate_unique_random_number(self):
        """ توليد رقم عشوائي من 1 إلى 20 بحيث لا يتكرر """
        while True:
            num = random.randint(1, 20)
            if num not in self.used_numbers:
                self.used_numbers.add(num)  
                return num

    def create_user(self, role, image_file, rate):
        """ Helper function to create users with specific role and image """
        image_path = os.path.join('attachments/media', image_file)
        print(f"Attempting to open image: {image_path}")
        with open(image_path, 'rb') as img_file:
            image_data = img_file.read()
            image = ContentFile(image_data, name=image_file)  
        
        unique_random_number = self.generate_unique_random_number()
        username = f'{role}_{unique_random_number}'  # اسم المستخدم سيكون فريدًا باستخدام الرقم العشوائي
        email = f'{role}_{unique_random_number}@example.com'
        user = User.objects.create(
            username=username,
            first_name=f'{role.capitalize()} ',
            last_name=f'{role.capitalize()} ',
            email=email,
            rate=rate,
            image=image,  
            role=role
        )
        

