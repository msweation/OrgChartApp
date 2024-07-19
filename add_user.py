# add_user.py
from app import create_app
from app.models import db, User

app = create_app()

with app.app_context():
    # Create a new user
    username = "test"
    password = "test"
    
    # Check if the user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print("User already exists.")
    else:
        # Create a new user and set the password
        user = User(username=username)
        user.set_password(password)

        # Add the user to the session and commit
        db.session.add(user)
        db.session.commit()

        print(f"User {username} added with password {password}")
