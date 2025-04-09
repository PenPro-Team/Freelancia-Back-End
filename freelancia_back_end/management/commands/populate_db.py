import os
import django
import sys
import random
from django.db import IntegrityError
from django.core.management.base import BaseCommand

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelancia.settings')  # Replace with your project settings
django.setup()

# Import factories
from factories import (
    SkillFactory, SpecialityFactory, UserFactory, ProjectFactory, 
    ProposalFactory, CertificateFactory, ContractFactory, PortfolioFactory,
    PortfolioImageFactory, ReviewFactory, ReportUserFactory, ReportContractFactory,
    BlackListedTokenFactory
)
from freelancia_back_end.models import User, Skill, Project, Proposal

def run():
    """Populate the database with realistic test data"""
    print("Starting database population...")
    
    # Create static skills (these should be created first as they're used by other models)
    static_skills = ['ReactJS', 'Python', 'JS', 'HTML/CSS']
    for skill_name in static_skills:
        try:
            SkillFactory(skill=skill_name)  # Use SkillFactory to create the static skills
        except IntegrityError:
            # Skip duplicates
            pass
    print("✓ Static skills created")
    
    # Create random skills
    skills_count = 30
    print(f"Creating {skills_count} random skills...")
    for _ in range(skills_count):
        try:
            SkillFactory()
        except IntegrityError:
            # Skip duplicates
            pass
    print("✓ Random skills created")
    
    # Create specialities
    specialities_count = 15
    print(f"Creating {specialities_count} specialities...")
    for _ in range(specialities_count):
        try:
            SpecialityFactory()
        except IntegrityError:
            # Skip duplicates
            pass
    print("✓ Specialities created")
    
    # Create users with different roles
    print("Creating users...")
    admin_count = 1
    client_count = 20
    freelancer_count = 50
    
    print(f"  - Creating {admin_count} admin users...")
    for _ in range(admin_count):
        UserFactory(role=User.RoleChoices.admin)
    
    print(f"  - Creating {client_count} client users...")
    clients = []
    for _ in range(client_count):
        clients.append(UserFactory(role=User.RoleChoices.client))
    
    print(f"  - Creating {freelancer_count} freelancer users...")
    freelancers = []
    for _ in range(freelancer_count):
        freelancers.append(UserFactory(role=User.RoleChoices.freelancer))
    print("✓ Users created")
    
    # Create certificates for freelancers
    print("Creating certificates for freelancers...")
    for freelancer in freelancers:
        cert_count = random.randint(0, 3)  # 0-3 certificates per freelancer
        for _ in range(cert_count):
            try:
                CertificateFactory(user=freelancer)
            except IntegrityError:
                # Skip duplicates
                pass
    print("✓ Certificates created")
    
    # Create projects
    projects_count = 40
    print(f"Creating {projects_count} projects...")
    projects = []
    for _ in range(projects_count):
        # Select a random client
        client = random.choice(clients)
        projects.append(ProjectFactory(owner_id=client))
    print("✓ Projects created")
    
    # Create proposals
    print("Creating proposals...")
    for project in projects:
        # Decide how many proposals for this project (0-5)
        proposal_count = random.randint(0, 5)
        
        # Select random freelancers for this project
        selected_freelancers = random.sample(
            freelancers, 
            min(proposal_count, len(freelancers))
        )
        
        for freelancer in selected_freelancers:
            try:
                ProposalFactory(project=project, user=freelancer)
            except IntegrityError:
                # Skip duplicates (due to unique_together constraint)
                pass
    print("✓ Proposals created")
    
    # Create contracts (assuming some proposals were accepted)
    contracts_count = min(30, len(projects))
    print(f"Creating {contracts_count} contracts...")
    contracts = []
    
    # Select random projects
    selected_projects = random.sample(projects, contracts_count)
    
    for project in selected_projects:
        # Try to find an existing proposal for this project
        proposals = Proposal.objects.filter(project=project)
        
        if proposals.exists():
            # Select a random proposal
            proposal = random.choice(proposals)
            contracts.append(ContractFactory(
                client=project.owner_id,
                freelancer=proposal.user,
                project=project,
                #price=proposal.price
            ))
        else:
            # If no proposals, create a contract with a random freelancer
            contracts.append(ContractFactory(
                client=project.owner_id,
                freelancer=random.choice(freelancers),
                project=project
            ))
    print("✓ Contracts created")
    
    # Create portfolios for freelancers
    print("Creating portfolios for freelancers...")
    for freelancer in freelancers:
        # 70% chance of having at least one portfolio
        if random.random() < 0.7:
            # Create 1-3 portfolios per freelancer
            portfolio_count = random.randint(1, 3)
            
            for _ in range(portfolio_count):
                portfolio = PortfolioFactory(user=freelancer)
                
                # Add 1-5 additional images to each portfolio
                image_count = random.randint(1, 5)
                for _ in range(image_count):
                    PortfolioImageFactory(portfolio=portfolio)
    print("✓ Portfolios created")
    
    # Create reviews
    print("Creating reviews...")
    for contract in contracts:
        # 80% chance of having a review from client to freelancer
        if random.random() < 0.8:
            try:
                ReviewFactory(
                    user_reviewr=contract.client,
                    user_reviewed=contract.freelancer,
                    project=contract.project
                )
            except IntegrityError:
                # Skip duplicates
                pass
        
        # 60% chance of having a review from freelancer to client
        if random.random() < 0.6:
            try:
                ReviewFactory(
                    user_reviewr=contract.freelancer,
                    user_reviewed=contract.client,
                    project=contract.project
                )
            except IntegrityError:
                # Skip duplicates
                pass
    print("✓ Reviews created")
    
    # Create reports (some users and contracts get reported)
    user_reports_count = 10
    contract_reports_count = 8
    
    print(f"Creating {user_reports_count} user reports...")
    for _ in range(user_reports_count):
        # Ensure reporter and reported user are different
        all_users = list(User.objects.all())
        reporter = random.choice(all_users)
        reported = random.choice([u for u in all_users if u != reporter])
        
        ReportUserFactory(user=reported, reporter=reporter)
    print("✓ User reports created")
    
    print(f"Creating {contract_reports_count} contract reports...")
    for _ in range(contract_reports_count):
        contract = random.choice(contracts)
        # Reporter can be any user but let's avoid the contract participants
        potential_reporters = [u for u in User.objects.all() 
                             if u != contract.client and u != contract.freelancer]
        
        if potential_reporters:
            reporter = random.choice(potential_reporters)
            ReportContractFactory(contract=contract, reporter=reporter)
    print("✓ Contract reports created")
    
    # Create some blacklisted tokens (for users who logged out)
    token_count = 15
    print(f"Creating {token_count} blacklisted tokens...")
    for _ in range(token_count):
        BlackListedTokenFactory()
    print("✓ Blacklisted tokens created")
    
    print("\nDatabase population completed successfully!")
    print(f"""
Summary:
- {Skill.objects.count()} skills
- {User.objects.filter(role=User.RoleChoices.admin).count()} admin users
- {User.objects.filter(role=User.RoleChoices.client).count()} client users
- {User.objects.filter(role=User.RoleChoices.freelancer).count()} freelancer users
- {Project.objects.count()} projects
- {Proposal.objects.count()} proposals
- {len(contracts)} contracts
    """)

if __name__ == "__main__":
    run()

# Also create a management command for easier use
class Command(BaseCommand):
    help = 'Populate the database with realistic test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing data before creating new test data',
        )

    def handle(self, *args, **kwargs):
        if kwargs['reset']:
            self.stdout.write(self.style.WARNING('Deleting existing data...'))
            # Add your delete operations here if needed
            # Be careful with this!
        
        run()
        self.stdout.write(self.style.SUCCESS('Successfully populated the database!'))
