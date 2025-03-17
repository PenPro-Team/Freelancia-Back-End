from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        admin = 'admin'
        client = 'client'
        freelancer = 'freelancer'
        # superadmin = 'superadmin'

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, unique=False)
    last_name = models.CharField(max_length=255, unique=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # Added By A.AboEl-Magd , to referes to Profile Picture
    image = models.ImageField(blank=True, null=True)
    # Added By A.Abo-ElMagd
    phone = models.CharField(max_length=20, null=True, blank=True)
    # Added By A.Abo-ElMagd , These Two Fields are for user review (Updated Every New Review)
    # Added To Make The Retrive of Data Faster
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_user_rated = models.IntegerField(default=0)

    role = models.CharField(max_length=10, choices=RoleChoices.choices)

    groups = models.ManyToManyField(
        Group, related_name='freelancia_user_groups', blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name='freelancia_user_permissions', blank=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'password']

    # This Propertry Made By A.Abo-ElMagd to use it in serialiers
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.role:
            if self.role == self.RoleChoices.admin:
                self.is_staff = True
                self.is_superuser = True
            # elif self.role == self.RoleChoices.superadmin:
            #     self.is_staff = True
            #     self.is_superuser = True
            elif self.role == self.RoleChoices.client:
                self.is_staff = False
                self.is_superuser = False
            elif self.role == self.RoleChoices.freelancer:
                self.is_staff = False
                self.is_superuser = False
                
        if self.is_staff and self.is_superuser:
            self.role = self.RoleChoices.admin

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    skill = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.skill


class Project(models.Model):
    class StatusChoices(models.TextChoices):
        open = 'open'
        ongoing = 'ongoing'
        canceled = 'canceled'
        contract_canceled_and_reopened = 'contract canceled and reopened'
        finished = 'finished'
    id = models.AutoField(primary_key=True)
    owner_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='projects')
    project_name = models.CharField(max_length=255)
    project_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    suggested_budget = models.DecimalField(max_digits=10, decimal_places=2)

    # Renamed From job_state By A.Abo-ElMagd
    project_state = models.CharField(
        max_length=50, choices=StatusChoices.choices, default=StatusChoices.open)
    # An Integer Not Date Edited By A.Abo-ElMagd
    expected_deadline = models.IntegerField()
    # Renamed From required_skills By A.Abo-ElMagd
    skills = models.ManyToManyField(Skill, related_name="projects")

    def __str__(self):
        return self.project_name


class Proposal(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    propose_text = models.TextField()
    # An Integer Not Date Edited By A.Abo-ElMagd
    deadline = models.IntegerField()
    attachment = models.FileField(blank=True, null=True)
    # Edited From erd project_id By A.Abo-ElMagd
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='proposals')
    # Edited From erd user_id By Abo-ElMagd
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='proposals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f'{self.user.username} - {self.project.project_name}'


class BlackListedToken(models.Model):
    token = models.CharField(max_length=500)
    user = models.ForeignKey(
        User, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("token", "user")
