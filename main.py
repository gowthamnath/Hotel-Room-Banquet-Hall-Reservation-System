import subprocess
import sys
import os

# Function to get the current script directory
def get_project_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

def launch_app():
    """
    The entry point logic:
    1. Check if a session exists (user is already logged in).
    2. If session exists, launch the Landing Screen.
    3. If no session, launch the Login Screen.
    """
    session_file = get_project_path("session.txt")
    login_script = get_project_path("login_screen.py")
    landing_script = get_project_path("landing_screen.py")

    # Check for existing session
    if os.path.exists(session_file):
        print(" Session detected. Redirecting to Landing Screen....")
        subprocess.Popen([sys.executable, landing_script])
    else:
        print("No active session. Launching Login Screen ")
        subprocess.Popen([sys.executable, login_script])

if __name__ == "__main__":
    launch_app()