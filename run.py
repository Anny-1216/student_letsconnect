import eventlet
eventlet.monkey_patch() # MUST be called before other imports like Flask, SocketIO, etc.

from app import create_app, socketio
from app.models import User # Import User model
from app import db # Import db instance for direct interaction if needed by User.save()
import click
from flask.cli import with_appcontext

app = create_app()

fake_profiles_data = [
    {"username": "TechGuruTom", "email": "tom@example.com", "role": "senior", "branch": "Computer", "year": 4, "bio": "Expert in AI and ML."},
    {"username": "CodeQueenCleo", "email": "cleo@example.com", "role": "senior", "branch": "Electronics", "year": 3, "bio": "Loves embedded systems."},
    {"username": "MechMasterMike", "email": "mike@example.com", "role": "senior", "branch": "Mechanical", "year": 4, "bio": "Passionate about robotics."},
    {"username": "CivilStarSara", "email": "sara@example.com", "role": "senior", "branch": "Civil", "year": 3, "bio": "Building the future, one structure at a time."},
    {"username": "ChemWhizChloe", "email": "chloe@example.com", "role": "senior", "branch": "Chemical", "year": 4, "bio": "Innovating with chemical processes."},
    {"username": "EagerLearnerLeo", "email": "leo@example.com", "role": "junior", "branch": "Computer", "year": 1, "bio": "Excited to learn coding!"},
    {"username": "NewbieNora", "email": "nora@example.com", "role": "junior", "branch": "Electronics", "year": 2, "bio": "Exploring the world of circuits."},
    {"username": "AspiringAndy", "email": "andy@example.com", "role": "junior", "branch": "Mechanical", "year": 1, "bio": "Wants to build cool machines."},
    {"username": "BuilderBen", "email": "ben@example.com", "role": "junior", "branch": "Civil", "year": 2, "bio": "Interested in sustainable infrastructure."},
    {"username": "ReactiveRiley", "email": "riley@example.com", "role": "junior", "branch": "Chemical", "year": 1, "bio": "Fascinated by reactions."}
]

@click.command('create-fakes')
@with_appcontext
def create_fakes_command():
    """Creates 10 fake user profiles."""
    existing_usernames = {u.username for u in User.find_all()}
    existing_emails = {u.email for u in User.find_all()}
    count = 0
    for profile_data in fake_profiles_data:
        if profile_data["username"] in existing_usernames:
            print(f'Username {profile_data["username"]} already exists. Skipping.')
            continue
        if profile_data["email"] in existing_emails:
            print(f'Email {profile_data["email"]} already exists. Skipping.')
            continue

        user = User(
            username=profile_data["username"],
            email=profile_data["email"],
            role=profile_data["role"],
            branch=profile_data["branch"],
            year=profile_data["year"],
            bio=profile_data["bio"]
        )
        user.set_password("password123")  # Set a common password for all fakes
        user.save()
        count += 1
        print(f'Created profile for {profile_data["username"]}')
    
    if count > 0:
        print(f"Successfully created {count} new fake profiles.")
    else:
        print("No new fake profiles were created. They might already exist.")

app.cli.add_command(create_fakes_command)

if __name__ == '__main__':
    # Use eventlet for running the SocketIO app
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)