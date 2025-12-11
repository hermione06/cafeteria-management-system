"""
Database initialization script
Run this to create all tables and optionally seed sample data
"""

from app import app, db
from models import User, MenuItem, Order, OrderItem, Announcement

def init_database():
    """Initialize database tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")

def seed_sample_menu():
    """Add sample menu items"""
    with app.app_context():
        # Check if menu already has items
        if MenuItem.query.first():
            print("Menu items already exist. Skipping seed.")
            return
        
        print("Adding sample menu items...")
        
        sample_items = [
            # Beverages
            MenuItem(
                name='Espresso',
                description='Strong Italian coffee shot',
                price=2.50,
                category='beverages',
                is_available=True,
                stock_quantity=100
            ),
            MenuItem(
                name='Cappuccino',
                description='Espresso with steamed milk and foam',
                price=3.50,
                category='beverages',
                is_available=True,
                stock_quantity=100
            ),
            MenuItem(
                name='Latte',
                description='Espresso with steamed milk',
                price=3.75,
                category='beverages',
                is_available=True,
                stock_quantity=100
            ),
            MenuItem(
                name='Iced Tea',
                description='Refreshing cold brewed tea',
                price=2.00,
                category='beverages',
                is_available=True,
                stock_quantity=50
            ),
            
            # Food
            MenuItem(
                name='Club Sandwich',
                description='Triple-decker with turkey, bacon, lettuce, and tomato',
                price=7.50,
                category='food',
                is_available=True,
                stock_quantity=30
            ),
            MenuItem(
                name='Caesar Salad',
                description='Romaine lettuce with Caesar dressing and croutons',
                price=6.50,
                category='food',
                is_available=True,
                stock_quantity=25
            ),
            MenuItem(
                name='Margherita Pizza',
                description='Fresh tomato, mozzarella, and basil',
                price=8.00,
                category='food',
                is_available=True,
                stock_quantity=20
            ),
            MenuItem(
                name='Chicken Wrap',
                description='Grilled chicken with vegetables in a tortilla',
                price=6.00,
                category='food',
                is_available=True,
                stock_quantity=35
            ),
            
            # Snacks
            MenuItem(
                name='French Fries',
                description='Crispy golden fries',
                price=3.00,
                category='snacks',
                is_available=True,
                stock_quantity=50
            ),
            MenuItem(
                name='Onion Rings',
                description='Crispy battered onion rings',
                price=3.50,
                category='snacks',
                is_available=True,
                stock_quantity=40
            ),
            MenuItem(
                name='Chicken Wings',
                description='Spicy buffalo wings',
                price=5.50,
                category='snacks',
                is_available=True,
                stock_quantity=30
            ),
            
            # Desserts
            MenuItem(
                name='Chocolate Cake',
                description='Rich chocolate layer cake',
                price=4.50,
                category='desserts',
                is_available=True,
                stock_quantity=15
            ),
            MenuItem(
                name='Cheesecake',
                description='New York style cheesecake',
                price=5.00,
                category='desserts',
                is_available=True,
                stock_quantity=12
            ),
            MenuItem(
                name='Ice Cream Sundae',
                description='Vanilla ice cream with toppings',
                price=3.50,
                category='desserts',
                is_available=True,
                stock_quantity=20
            ),
            MenuItem(
                name='Apple Pie',
                description='Classic homemade apple pie',
                price=4.00,
                category='desserts',
                is_available=True,
                stock_quantity=10
            ),
        ]
        
        db.session.add_all(sample_items)
        db.session.commit()
        
        print(f"✓ Added {len(sample_items)} sample menu items!")

def create_admin_user():
    """Create default admin user"""
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists. Skipping.")
            return
        
        print("Creating admin user...")
        
        admin = User(
            username='admin',
            email='admin@cafehub.com',
            role='admin',
            is_active=True,
            is_verified=True
        )
        admin.set_password('admin123')  # Change this in production!
        
        db.session.add(admin)
        db.session.commit()
        
        print("✓ Admin user created!")
        print("  Username: admin")
        print("  Password: admin123")
        print("  ⚠️  CHANGE THIS PASSWORD IN PRODUCTION!")

def main():
    """Main initialization function"""
    print("=" * 50)
    print("CafeHub Database Initialization")
    print("=" * 50)
    
    # Step 1: Create tables
    init_database()
    
    # Step 2: Create admin user
    create_admin_user()
    
    # Step 3: Seed sample menu
    seed_sample_menu()
    
    print("=" * 50)
    print("✓ Database initialization complete!")
    print("=" * 50)

if __name__ == '__main__':
    main()