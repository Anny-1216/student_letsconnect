import random # Added import for random
from app import create_app, db
# from app.models import User # Moved down

# Define the new standard list of branches
VALID_BRANCHES = [
    "Computer Engineering",
    "Information Technology",
    "Electronics & Telecommunication Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Artificial Intelligence & Machine Learning (AIML)",
    "Artificial Intelligence & Data Science (AIDS)",
    "Electronics & Computer Engineering (ECE)",
    "Internet of Things (IOT)"
]

# DEFAULT_BRANCH = "Civil Engineering" # No longer needed for random assignment
# BRANCH_MAPPING = { ... } # No longer needed for random assignment

def update_branches():
    app = create_app()
    with app.app_context():
        from app.models import User
        users = User.find_all()
        updated_count = 0
        print("Starting random branch assignment process...")

        if not VALID_BRANCHES:
            print("Error: VALID_BRANCHES list is empty. Cannot assign branches.")
            return

        for user in users:
            original_branch = getattr(user, 'branch', None)
            # Randomly select a new branch from the valid list
            new_branch = random.choice(VALID_BRANCHES)
            
            print(f"User '{user.username}' (ID: {user.id}): Current branch '{original_branch}'. Assigning new random branch: '{new_branch}'.")
            user.branch = new_branch
            user.save()
            updated_count += 1

        if updated_count > 0:
            print(f"Successfully updated branches for {updated_count} users with random assignments.")
        else:
            print("No users found to update or an error occurred.")
        print("Random branch assignment process finished.")

if __name__ == '__main__':
    update_branches()
