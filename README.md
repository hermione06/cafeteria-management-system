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
│   └── workflows/       # CI/CD workflows
├── src/
│   └── app.py          # Main Flask application
├── tests/
│   └── test_app.py     # Unit tests
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
└── README.md          # Project documentation
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- pip
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/cafeteria-management-system.git
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

### Running the Application

```bash
python src/app.py
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

## Development Roadmap

### Phase 1: Foundation (Current)
- [x] Basic Flask application
- [x] Initial API endpoints
- [x] Unit tests setup
- [ ] CI pipeline with GitHub Actions

### Phase 2: Core Features
- [ ] Database integration
- [ ] Order management
- [ ] User authentication

### Phase 3: Deployment
- [ ] Docker containerization
- [ ] CD pipeline
- [ ] Cloud deployment on Render
- [ ] Monitoring and logging

## Contributing
This is an educational project. Feel free to fork and experiment!

## License
MIT License

## Contact
Your Name - your.email@example.com