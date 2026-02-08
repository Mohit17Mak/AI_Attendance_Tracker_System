from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username="admin").first()

    if not admin:
        print("Admin user not found in DB.")
    else:
        admin.password_hash = generate_password_hash("admin123", method="scrypt")
        db.session.commit()
        print("Admin password fixed successfully.")
        print("Login: admin / admin123")
