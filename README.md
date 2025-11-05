# Cafeteria Management System

A Flask-based web application for managing cafeteria operations including menu management, orders, and inventory tracking.

## Features (Planned)
- 📋 Menu Management
- 🛒 Order Processing
- 👥 User Management
- 📊 Sales Reports
- 🔔 Real-time Notifications

## Current Status
✅ Basic Flask application structure  
✅ Initial menu endpoints  
✅ Unit tests with Pytest  
⏳ CI/CD pipeline (In Progress)  
⏳ Docker containerization (Planned)  
⏳ Cloud deployment (Planned)

## Project Structure
```
cafeteria-management-system/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── migrations/                 # Database migrations
│   ├── versions/               # Migration version files
│   └── alembic.ini             # Alembic configuration
├── src/
│   ├── app.py                  # Main Flask application
│   ├── models.py               # SQLAlchemy models
│   └── config.py               # Configuration settings
├── tests/
│   └── test_app.py             # Unit tests
├── instance/                   # Database files (gitignored)
├── venv/                       # Virtual environment (gitignored)
├── .dockerignore               # Docker ignore rules
├── .env                        # Environment variables (gitignored)
├── .gitignore                  # Git ignore rules
├── Dockerfile                  # Docker container configuration
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```
## 🛠️ Tech Stack

Backend: Flask 3.0
Database: SQLAlchemy + SQLite (dev), PostgreSQL (production ready)
Migrations: Flask-Migrate (Alembic)
Testing: Pytest
CI/CD: GitHub Actions
Containerization: Docker
Deployment: Render (planned)

## Setup Instructions

### Prerequisites
- Python 3.10+
- pip
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/hermione06/cafeteria-management-system.git
cd cafeteria-management-system
```

2. Create and activate virtual environment:
```bash
python -m venv .venv # python3 -m venv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
### Set up environment variables:

```bash
# Create .env file (already in .gitignore)
   cp .env.example .env  # Or create manually
```
#### Add to .env:
FLASK_APP=src/app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

### Initialize the database:

```bash
# Create instance directory
   mkdir -p instance

   # Initialize migrations (if not done)
   flask db init

   # Create migration
   flask db migrate -m "Initial migration"

   # Apply migrations
   flask db upgrade

   # OR simply create tables directly
   python -c "import sys; sys.path.insert(0, 'src'); from app import app, db; app.app_context().push(); db.create_all(); print('✅ Tables created!')"
```

If there is issue related to this:
```bash
# 1. Delete the database
rm -f instance/cafeteria_dev.db

# 2. Delete migration versions (keep migrations folder and env.py)
rm -f migrations/versions/*.py

# 3. Create fresh initial migration
flask db migrate -m "Initial migration with authentication"

# 4. Apply migration
flask db upgrade
```

### Running the Application
Local Development (without Docker):

```bash
python src/app.py
```

With Docker (Development Mode):
```bash
# Build the image
docker build -t cafeteria-management-app:latest .

# Run the container
docker run --rm -p 5000:5000 cafeteria-management-app:latest
```

With Docker (Production Mode):
```bash
# Run with production config
docker run --rm -p 5000:5000 -e FLASK_ENV=production cafeteria-management-app:latest

# With persistent data storage
docker run --rm -p 5000:5000 \
  -e FLASK_ENV=production \
  -v cafeteria-data:/app/instance \
  cafeteria-management-app:latest
```

The application will be available at `http://localhost:5000`

### Running Tests

```bash
pytest
```

For verbose output:
```bash
pytest -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Homepage |
| GET | `/health` | Health check |
| GET | `/menu` | Get all menu items |
| GET | `/menu/<id>` | Get specific menu item |

## For Testing, Refer to Postman Link: 
https://app.getpostman.com/join-team?invite_code=b4e138937dcf46feb30542e57dc7e753b1cbb14a7ee90d6f368c6ba5fcb15723&target_code=3ed5366b77e93ca5703f89941a0075bb


## Development Roadmap

### Phase 1: Foundation (Current)
- [x] Basic Flask application
- [x] Initial API endpoints
- [x] Unit tests setup
- [x] CI pipeline with GitHub Actions

### Phase 2: Core Features
- [ ] Database integration
- [ ] Order management
- [ ] User authentication

### Phase 3: Deployment
- [ ] Docker containerization
- [ ] CD pipeline
- [ ] Cloud deployment on Render
- [ ] Monitoring and logging

## 👨‍💻 Team Members

Asiman Ismayilova 
Rashid Huseynov
Tamilla Iskandarova
Ali Gasimov

## Contributing
This is an educational project. Feel free to fork and experiment!

## License
MIT License

## Contact
Your Name - your.email@example.com