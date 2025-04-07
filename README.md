# Freelancia - Backend API

Freelancia is a platform connecting freelancers and clients, allowing for project posting, bidding, and management of freelance work.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Contributors](#contributors)
- [License](#license)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Docker Configuration](#docker-configuration)

## Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)
- PostgreSQL (or your database of choice)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Freelancia-Back-End.git
   cd Freelancia-Back-End
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file in the project root and add:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   DATABASE_URL=your_database_connection_string
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

After installation, the API will be available at `http://localhost:8000/` or the configured port.

### Authentication

The API uses token-based authentication. To obtain a token:

```bash
curl -X POST http://localhost:8000/api/auth/token/ -d "username=yourusername&password=yourpassword"
```

For authenticated requests, include the token in your headers:

```bash
Authorization: Bearer your_token_here
```

## API Endpoints

### Users
- `GET /api/users/` - List all users
- `POST /api/users/` - Create a new user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user details
- `DELETE /api/users/{id}/` - Delete a user

### Projects
- `GET /api/projects/` - List all projects
- `POST /api/projects/` - Create a new project
- `GET /api/projects/{id}/` - Get project details
- `PUT /api/projects/{id}/` - Update project details
- `DELETE /api/projects/{id}/` - Delete a project

### Bids
- `GET /api/bids/` - List all bids
- `POST /api/bids/` - Create a new bid
- `GET /api/bids/{id}/` - Get bid details
- `PUT /api/bids/{id}/` - Update bid details
- `DELETE /api/bids/{id}/` - Delete a bid

### Reviews
- `GET /api/reviews/` - List all reviews
- `POST /api/reviews/` - Create a new review
- `GET /api/reviews/{id}/` - Get review details
- `PUT /api/reviews/{id}/` - Update review details
- `DELETE /api/reviews/{id}/` - Delete a review

## Project Structure
The project is organized as follows:
```
Freelancia-Back-End/
├── manage.py
├── requirements.txt
├── .env
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── projects/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── bids/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests.py
│   └── reviews/
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       ├── urls.py
│       └── tests.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── static/
    └── ...
```

## Technologies Used
- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker (optional for containerization)
- Gunicorn (for production WSGI server)
- Nginx (optional for reverse proxy)
- Celery (optional for asynchronous tasks)
- Redis (optional for task queue)

## Contributors
- [Your Name](https://github.com/yourusername)
- [Contributor Name](https://github.com/contributorusername)

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Deployment
To deploy the application:
1. Set up a production environment (e.g., using Docker or a cloud provider).
2. Configure environment variables for production.
3. Use Gunicorn as the WSGI server and optionally Nginx as a reverse proxy.
4. Run migrations and collect static files:
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```
5. Start the application.

## Troubleshooting
- **Database connection issues**: Ensure the `DATABASE_URL` in `.env` is correct and the database server is running.
- **Static files not loading**: Run `python manage.py collectstatic` and ensure the static files directory is correctly configured.
- **Authentication errors**: Verify the token and ensure the user credentials are correct.
- **Server errors**: Check the logs for detailed error messages and debug accordingly.

## Docker Configuration

To run the application using Docker, use the following `docker-compose.yml` file:

```yaml
version: '3'
services:
  web:
    build: .
    command: gunicorn freelancia.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_DB=freelancia

volumes:
  postgres_data:
```

