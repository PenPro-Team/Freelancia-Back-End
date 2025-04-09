import os
from django.core.management.base import BaseCommand
from freelancia_back_end.models import User
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'Create 10 users (4 clients, 6 freelancers) with rate=5 and predefined images'

    def handle(self, *args, **kwargs):
        # المسار إلى مجلد attachments الذي يحتوي على الصور
        image_folder = 'attachments/media'

        # طباعة المسار الفعلي للمجلد
        print("Looking for images in:", os.path.abspath(image_folder))
        
        # الحصول على قائمة بكل الملفات في المجلد
        image_files = [f for f in os.listdir(image_folder) if f.endswith(('jpg', 'jpeg', 'png'))]
        
        # التأكد من أن هناك 10 صور
        if len(image_files) < 10:
            self.stdout.write(self.style.ERROR('You need at least 10 images in the attachments/ folder'))
            return

        # ترتيب الصور بالاسم (1.jpg, 2.jpg, ...)
        image_files.sort()

        # إنشاء 4 عملاء (clients)
        for i in range(4):
            self.create_user(
                role="client", 
                image_file=image_files[i], 
                rate=5
            )
        
        # إنشاء 6 مستقلين (freelancers)
        for i in range(4, 10):
            self.create_user(
                role="freelancer", 
                image_file=image_files[i], 
                rate=5
            )

    def create_user(self, role, image_file, rate):
        """ Helper function to create users with specific role and image """

        # تعيين الصورة
        image_path = os.path.join('attachments/media', image_file)  # استخدام المسار الصحيح للمجلد
        print(f"Attempting to open image: {image_path}")  # طباعة المسار الذي يحاول فتحه
        with open(image_path, 'rb') as img_file:
            image_data = img_file.read()
            image = ContentFile(image_data, name=image_file)  # تأكد من أن الصورة يتم تحميلها بشكل صحيح
        
        # إنشاء المستخدم مع المعلومات المحددة
        user = User.objects.create(
            username=f'{role}_{image_file}',  # اسم المستخدم سيكون فريدًا
            first_name=f'{role.capitalize()} FirstName',
            last_name=f'{role.capitalize()} LastName',
            email=f'{role}_{image_file}@example.com',
            rate=rate,
            image=image,  # تأكد من أن هذا الحقل يتم تمريره بشكل صحيح
            role=role
        )
        
        self.stdout.write(self.style.SUCCESS(f'User {user.username} created successfully with rate={rate}'))
