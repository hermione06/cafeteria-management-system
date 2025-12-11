# Cafeteria Management System - Backend API

A comprehensive Flask-based REST API for managing a cafeteria system with user authentication, menu management, order processing, and announcements.

## Features

- **Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (User, Staff, Admin)
  - Email verification
  - Password reset functionality
  
- **User Management**
  - User registration and profile management
  - Admin user management
  - User statistics
  
- **Menu Management**
  - CRUD operations for menu items
  - Category-based filtering
  - Availability management
  - Stock tracking
  
- **Order Management**
  - Create and manage orders
  - Order status tracking
  - Payment status management
  - Order history
  
- **Announcements**
  - Create and manage system announcements
  - Priority levels
  - Expiration dates

## Project Structure

```
cafeteria-backend/
├── app.py                      # Application factory and entry point
├── config.py                   # Configuration management
├── models.py                   # Database models
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── routes/
│   ├── __init__.py            # Route registration
│   ├── auth_routes.py         # Authentication endpoints
│   ├── user_routes.py         # User management endpoints
│   ├── menu_routes.py         # Menu management endpoints
│   ├── order_routes.py        # Order management endpoints
│   └── announcement_routes.py # Announcement endpoints
├── utils/
│   ├── decorators.py          # Authorization decorators
│   └── pagination.py          # Pagination helper
└── instance/
    └── cafeteria_dev.db       # SQLite database (created automatically)
```

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd cafeteria-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Run the application**
```bash
python app.py
# Or using Flask CLI:
flask run
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register new user | No |
| POST | `/login` | Login user | No |
| POST | `/logout` | Logout user | Yes |
| POST | `/refresh` | Refresh access token | Yes (Refresh Token) |
| POST | `/verify-email/<token>` | Verify email | No |
| GET | `/me` | Get current user | Yes |
| POST | `/forgot-password` | Request password reset | No |
| POST | `/reset-password/<token>` | Reset password | No |
| POST | `/change-password` | Change password | Yes |

### Users (`/api/users`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Get all users | Admin |
| GET | `/<id>` | Get user by ID | Owner/Admin |
| PUT | `/<id>` | Update user | Owner/Admin |
| DELETE | `/<id>` | Delete user | Admin |
| GET | `/stats` | Get user statistics | Admin |

### Menu (`/api/menu`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Get all menu items | No |
| GET | `/<id>` | Get menu item by ID | No |
| GET | `/categories` | Get all categories | No |
| POST | `/` | Create menu item | Admin |
| PUT | `/<id>` | Update menu item | Staff/Admin |
| DELETE | `/<id>` | Delete menu item | Admin |
| PATCH | `/<id>/availability` | Toggle availability | Staff/Admin |

### Orders (`/api/orders`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Get orders | Yes |
| GET | `/<id>` | Get order by ID | Owner/Staff/Admin |
| POST | `/` | Create order | Yes |
| POST | `/<id>/items` | Add item to order | Owner |
| DELETE | `/<id>/items/<item_id>` | Remove item from order | Owner |
| PATCH | `/<id>/status` | Update order status | Staff/Admin |
| PATCH | `/<id>/payment` | Update payment status | Staff/Admin |
| DELETE | `/<id>` | Delete order | Owner/Admin |

### Announcements (`/api/announcements`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Get active announcements | No |
| GET | `/all` | Get all announcements | Admin |
| GET | `/<id>` | Get announcement by ID | No |
| POST | `/` | Create announcement | Admin |
| PUT | `/<id>` | Update announcement | Admin |
| DELETE | `/<id>` | Delete announcement | Admin |

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. After logging in, you'll receive an access token and a refresh token.

### Using the Access Token

Include the access token in the `Authorization` header:

```
Authorization: Bearer <your-access-token>
```

### Token Lifecycle

- Access tokens expire after 1 hour
- Refresh tokens expire after 30 days
- Use the `/api/auth/refresh` endpoint to get a new access token

## Role-Based Access Control

Three roles are supported:

- **User**: Regular users who can place orders and manage their profile
- **Staff**: Can manage menu items and orders
- **Admin**: Full access to all features including user management

## Query Parameters

### Pagination

Most GET endpoints support pagination:

- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

Example: `/api/menu?page=2&per_page=10`

### Filtering

Menu items:
- `category`: Filter by category
- `available`: Show only available items (true/false)
- `search`: Search by name

Orders:
- `status`: Filter by status
- `is_paid`: Filter by payment status
- `user_id`: Filter by user (admin/staff only)

Users:
- `role`: Filter by role
- `is_active`: Filter by active status
- `search`: Search by username or email

## Error Handling

The API returns consistent error responses:

```json
{
  "error": "Error message here"
}
```

HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 500: Internal Server Error

## Database Models

### User
- Authentication and profile information
- Password hashing with bcrypt
- Email verification and password reset tokens

### MenuItem
- Menu item details
- Category and availability tracking
- Stock quantity management

### Order
- Order tracking and status management
- Payment status
- Special instructions and admin notes

### OrderItem
- Junction table between orders and menu items
- Quantity and unit price at time of order

### Announcement
- System-wide announcements
- Priority levels (low, normal, high)
- Optional expiration dates

## Development

### Database Migrations

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

### Running Tests

```bash
pytest
pytest --cov=. --cov-report=html
```

### Code Formatting

```bash
black .
flake8 .
```

## Production Deployment

1. **Set environment variables**
   - Set `FLASK_ENV=production`
   - Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
   - Configure production database (PostgreSQL recommended)

2. **Use a production server**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. **Enable HTTPS**
   - Use a reverse proxy (nginx, Apache)
   - Configure SSL certificates

4. **Database**
   - Use PostgreSQL or MySQL in production
   - Enable connection pooling
   - Regular backups

5. **Security**
   - Implement rate limiting
   - Set up token blacklisting for logout
   - Configure CORS properly
   - Enable security headers



## Database/Tables
Just run `sqlitebrowser` in terminal.

## Environment Variables

See `.env.example` for all available configuration options.

## License

MIT License

## Support

For issues and questions, please open an issue on the repository.