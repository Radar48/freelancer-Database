
from app import create_app, db
from app.models import User, Platform, Category, IncomeEntry
from datetime import date
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()

    user_exists = User.query.filter_by(email='lucy@example.com').first()
    platforms_exist = Platform.query.first()
    categories_exist = Category.query.first()

    if True:
        # Create platforms
        for name, desc in [("Fiverr", "Freelance gigs"), ("Upwork", "Freelancing jobs"), ("Other", "Other")]:
            if not Platform.query.filter_by(name=name).first():
                db.session.add(Platform(name=name, description=desc))
        db.session.commit()

        # Create categories
        for name, desc in [("Writing", "Content writing"),
                           ("Web Development", "Graphic and UI/UX design"),
                           ("Other", "Other tasks")]:
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name, description=desc))
        db.session.commit()

        # Fetch platforms and categories
        fiverr = Platform.query.filter_by(name="Fiverr").first()
        upwork = Platform.query.filter_by(name="Upwork").first()
        writing = Category.query.filter_by(name="Writing").first()
        web_dev = Category.query.filter_by(name="Web Development").first()
        other = Category.query.filter_by(name="Other").first()
        other_platform = Platform.query.filter_by(name="Other").first()

        # Create user
        user1 = User(
            email='lucy@example.com',
            username='lucy',
            password_hash=generate_password_hash('password'),
            currency='USD'
        )

        entries = [
            IncomeEntry(user=user1, platform=fiverr, category=writing, amount=150.0, date=date(2024, 5, 10)),
            IncomeEntry(user=user1, platform=upwork, category=web_dev, amount=300.0, date=date(2024, 6, 1)),
            IncomeEntry(user=user1, platform=other_platform, category=other, amount=180.0, date=date(2024, 6, 15))
        ]
    
        db.session.add(user1)
        db.session.add_all(entries)
        db.session.commit()
        print("✅ Sample data added!")
    
    else:
        print("⚠️ Sample user or data already exists — skipping seed.")