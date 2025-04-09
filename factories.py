import factory
import factory.fuzzy
import random
import os
from datetime import timedelta, date
from django.utils import timezone
from django.core.files.base import ContentFile
from faker import Faker

# Import models
from freelancia_back_end.models import (
    User, Skill, Project, Proposal, BlackListedToken, 
    Speciality, Certificate
)
from report.models import ReportUser, ReportContract
from portfolio.models import Portfolio, PortfolioImage
from reviews.models import Review
from contract.models import Contract  

# Create multi-language Faker instances
fake_en = Faker('en_US')
fake_ar = Faker('ar_EG')

# Helper function to mix Arabic and English content
def mix_langs(en_func, ar_func, ar_prob=0.3):
    """Mix English and Arabic content with probability ar_prob of using Arabic"""
    return ar_func() if random.random() < ar_prob else en_func()

# Helper function for placeholder images
def get_placeholder_image(width=800, height=600):
    """Create a simple placeholder image as ContentFile"""
    from PIL import Image, ImageDraw
    import io
    
    # Create a new image with a random background color
    color = (
        random.randint(100, 240),
        random.randint(100, 240),
        random.randint(100, 240)
    )
    image = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(image)
    
    # Draw some random shapes
    for _ in range(5):
        shape_color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        x1 = random.randint(0, width-100)
        y1 = random.randint(0, height-100)
        x2 = x1 + random.randint(50, 100)
        y2 = y1 + random.randint(50, 100)
        draw.rectangle([x1, y1, x2, y2], fill=shape_color)
    
    # Convert the image to a ContentFile
    image_io = io.BytesIO()
    image.save(image_io, format='JPEG')
    image_file = ContentFile(image_io.getvalue(), name=f"placeholder_{random.randint(1000, 9999)}.jpg")
    return image_file

# Define factories
class SkillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Skill
        django_get_or_create = ('skill',)
    
    skill = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.job().split('/')[0].strip(),
            lambda: fake_ar.job().split('/')[0].strip()
        )
    )

class SpecialityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Speciality
        django_get_or_create = ('title',)
    
    title = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.job(),
            lambda: fake_ar.job()
        )
    )
    description = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.paragraph(nb_sentences=3),
            lambda: fake_ar.paragraph(nb_sentences=3)
        )
    )

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"{fake_en.user_name()[:250]}_{n}")
    first_name = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.first_name(),
            lambda: fake_ar.first_name()
        )
    )
    last_name = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.last_name(),
            lambda: fake_ar.last_name()
        )
    )
    email = factory.LazyAttribute(lambda o: f"{o.username}@{fake_en.domain_name()}")
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    birth_date = factory.LazyFunction(lambda: fake_en.date_of_birth(minimum_age=18, maximum_age=70))
    address = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.address(),
            lambda: fake_ar.address()
        )
    )
    postal_code = factory.LazyFunction(lambda: fake_en.postcode())
    description = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.paragraph(nb_sentences=5),
            lambda: fake_ar.paragraph(nb_sentences=5)
        )
    )
    user_balance = factory.LazyFunction(lambda: random.uniform(0, 10000))
    image = factory.LazyFunction(lambda: get_placeholder_image())
    phone = factory.LazyFunction(lambda: fake_en.phone_number()[:20])
    rate = factory.LazyFunction(lambda: round(random.uniform(1, 5), 2))
    total_user_rated = factory.LazyFunction(lambda: random.randint(0, 100))
    role = factory.fuzzy.FuzzyChoice([User.RoleChoices.client, User.RoleChoices.freelancer, User.RoleChoices.admin])
    speciality = factory.SubFactory(SpecialityFactory)
    is_active = True

    @factory.post_generation
    def skills(self, create, extracted, **kwargs):
        if not create:
            return
        
        # Add between 3-7 random skills to each user
        if not extracted:
            extracted = random.sample(list(Skill.objects.all()), random.randint(3, min(7, Skill.objects.count())))
        
        for skill in extracted:
            self.skills.add(skill)

class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project
    
    owner_id = factory.SubFactory(UserFactory, role=User.RoleChoices.client)
    project_name = factory.LazyFunction(
        lambda: mix_langs(
            lambda: f"{fake_en.job()} Project",
            lambda: f"مشروع {fake_ar.job()}"
        )
    )
    project_description = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.paragraph(nb_sentences=5),
            lambda: fake_ar.paragraph(nb_sentences=5)
        )
    )
    suggested_budget = factory.LazyFunction(lambda: random.uniform(100, 5000))
    project_state = factory.fuzzy.FuzzyChoice([choice[0] for choice in Project.StatusChoices.choices])
    expected_deadline = factory.LazyFunction(lambda: random.randint(1, 60))  # Days

    @factory.post_generation
    def skills(self, create, extracted, **kwargs):
        if not create:
            return
        
        # Add between 2-5 random skills to each project
        if not extracted:
            extracted = random.sample(list(Skill.objects.all()), random.randint(2, min(5, Skill.objects.count())))
        
        for skill in extracted:
            self.skills.add(skill)

class ProposalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Proposal
    
    price = factory.LazyAttribute(lambda o: random.uniform(
        o.project.suggested_budget * 0.7, 
        o.project.suggested_budget * 1.3
    ))
    propose_text = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.paragraph(nb_sentences=3),
            lambda: fake_ar.paragraph(nb_sentences=3)
        )
    )
    deadline = factory.LazyAttribute(lambda o: random.randint(
        max(1, o.project.expected_deadline - 5), 
        o.project.expected_deadline + 5
    ))
    # Assumption: attachment would be a PDF or document - placeholder
    project = factory.SubFactory(ProjectFactory)
    user = factory.SubFactory(UserFactory, role=User.RoleChoices.freelancer)

class CertificateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Certificate
    
    title = factory.LazyFunction(
        lambda: mix_langs(
            lambda: f"{fake_en.word().capitalize()} {fake_en.word().capitalize()} Certificate",
            lambda: f"شهادة {fake_ar.word()} {fake_ar.word()}"
        )
    )
    description = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.paragraph(nb_sentences=2),
            lambda: fake_ar.paragraph(nb_sentences=2)
        )
    )
    issued_by = factory.LazyFunction(
        lambda: mix_langs(
            lambda: f"{fake_en.company()}",
            lambda: f"{fake_ar.company()}"
        )
    )
    issued_date = factory.LazyFunction(
        lambda: fake_en.date_between(
            start_date=date.today() - timedelta(days=1825),  # ~5 years ago
            end_date=date.today()
        )
    )
    user = factory.SubFactory(UserFactory, role=User.RoleChoices.freelancer)
    image = factory.LazyFunction(lambda: get_placeholder_image())

class ContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contract
    
    contract_terms = factory.Faker('paragraph', nb_sentences=3)
    deadline = factory.LazyAttribute(lambda o: random.randint(1, 30))  # مدة العقد باليوم
    budget = factory.LazyAttribute(lambda o: random.randint(500, 5000))  # تحديد ميزانية العقد
    freelancer = factory.SubFactory(UserFactory, role=User.RoleChoices.freelancer)
    client = factory.SubFactory(UserFactory, role=User.RoleChoices.client)
    project = factory.SubFactory(ProjectFactory)
    contract_state = factory.fuzzy.FuzzyChoice([choice[0] for choice in Contract.StatusChoices.choices])  # حالة العقد



class PortfolioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Portfolio
    
    user = factory.SubFactory(UserFactory, role=User.RoleChoices.freelancer)
    title = factory.LazyFunction(
        lambda: mix_langs(
            lambda: f"{fake_en.catch_phrase()}",
            lambda: f"{fake_ar.catch_phrase()}"
        )
    )
    description = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.paragraph(nb_sentences=4),
            lambda: fake_ar.paragraph(nb_sentences=4)
        )
    )
    main_image = factory.LazyFunction(lambda: get_placeholder_image())

class PortfolioImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PortfolioImage
    
    portfolio = factory.SubFactory(PortfolioFactory)
    image = factory.LazyFunction(lambda: get_placeholder_image())

class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review
    
    message = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.paragraph(nb_sentences=2),
            lambda: fake_ar.paragraph(nb_sentences=2)
        )
    )
    rate = factory.LazyFunction(lambda: random.randint(1, 5))
    user_reviewr = factory.SubFactory(UserFactory, role=User.RoleChoices.client)
    user_reviewed = factory.SubFactory(UserFactory, role=User.RoleChoices.freelancer)
    project = factory.SubFactory(ProjectFactory)

class ReportUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReportUser
    
    title = factory.LazyFunction(
        lambda: mix_langs(
            lambda: f"Report: {fake_en.sentence(nb_words=5)}",
            lambda: f"بلاغ: {fake_ar.sentence(nb_words=5)}"
        )
    )
    description = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.paragraph(nb_sentences=3),
            lambda: fake_ar.paragraph(nb_sentences=3)
        )
    )
    status = factory.fuzzy.FuzzyChoice([choice[0] for choice in ReportUser.StatusChoices.choices])
    user = factory.SubFactory(UserFactory)  # Reported user
    reporter = factory.SubFactory(UserFactory)  # Reporting user
    
    @factory.lazy_attribute
    def resolved_notes(self):
        if self.status in [ReportUser.StatusChoices.RESOLVED, ReportUser.StatusChoices.IGNORED]:
            return mix_langs(
                lambda: fake_en.paragraph(nb_sentences=2),
                lambda: fake_ar.paragraph(nb_sentences=2)
            )
        return None
    
    @factory.lazy_attribute
    def resolution_reason(self):
        if self.status in [ReportUser.StatusChoices.RESOLVED, ReportUser.StatusChoices.IGNORED]:
            return random.choice([choice[0] for choice in ReportUser.ResolutionReason.choices])
        return None
    
    @factory.lazy_attribute
    def resolved_by(self):
        if self.status in [ReportUser.StatusChoices.RESOLVED, ReportUser.StatusChoices.IGNORED]:
            return UserFactory(role=User.RoleChoices.admin)
        return None
    
    @factory.lazy_attribute
    def resolved_at(self):
        if self.status in [ReportUser.StatusChoices.RESOLVED, ReportUser.StatusChoices.IGNORED]:
            return timezone.now() - timedelta(days=random.randint(1, 10))
        return None

class ReportContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReportContract
    
    title = factory.LazyFunction(
        lambda: mix_langs(
            lambda: f"Contract Report: {fake_en.sentence(nb_words=5)}",
            lambda: f"بلاغ عقد: {fake_ar.sentence(nb_words=5)}"
        )
    )
    description = factory.LazyFunction(
        lambda: mix_langs(
            lambda: fake_en.paragraph(nb_sentences=3),
            lambda: fake_ar.paragraph(nb_sentences=3)
        )
    )
    status = factory.fuzzy.FuzzyChoice([choice[0] for choice in ReportContract.StatusChoices.choices])
    contract = factory.SubFactory(ContractFactory)
    reporter = factory.SubFactory(UserFactory)
    
    @factory.lazy_attribute
    def resolved_notes(self):
        if self.status in [ReportContract.StatusChoices.RESOLVED, ReportContract.StatusChoices.IGNORED]:
            return mix_langs(
                lambda: fake_en.paragraph(nb_sentences=2),
                lambda: fake_ar.paragraph(nb_sentences=2)
            )
        return None
    
    @factory.lazy_attribute
    def resolution_reason(self):
        if self.status in [ReportContract.StatusChoices.RESOLVED, ReportContract.StatusChoices.IGNORED]:
            return random.choice([choice[0] for choice in ReportContract.ResolutionReason.choices])
        return None
    
    @factory.lazy_attribute
    def resolved_by(self):
        if self.status in [ReportContract.StatusChoices.RESOLVED, ReportContract.StatusChoices.IGNORED]:
            return UserFactory(role=User.RoleChoices.admin)
        return None
    
    @factory.lazy_attribute
    def resolved_at(self):
        if self.status in [ReportContract.StatusChoices.RESOLVED, ReportContract.StatusChoices.IGNORED]:
            return timezone.now() - timedelta(days=random.randint(1, 10))
        return None

class BlackListedTokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BlackListedToken
    
    token = factory.LazyFunction(lambda: fake_en.sha256())
    user = factory.SubFactory(UserFactory)
