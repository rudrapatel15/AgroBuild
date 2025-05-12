import os
import getpass
import subprocess

def setup_windows_task():
    try:
        # Get current user
        current_user = getpass.getuser()
        
        # Get Python path (Windows compatible)
        python_path = os.path.join(os.path.dirname(os.sys.executable), "python.exe")
        if not os.path.exists(python_path):
            python_path = os.path.join(os.environ["PYTHON_HOME"], "python.exe") if "PYTHON_HOME" in os.environ else None
        
        # Get manage.py path
        manage_path = os.path.join(os.getcwd(), "manage.py")
        log_path = os.path.join(os.getcwd(), "watering_reminder.log")

        # Verify paths exist
        if not all([python_path, os.path.exists(python_path), os.path.exists(manage_path)]):
            raise FileNotFoundError("Could not find Python or manage.py")

        # PROPERLY ESCAPE PATHS WITH SPACES
        python_path_escaped = f'"{python_path}"'
        manage_path_escaped = f'"{manage_path}"'

        # Create the task (using proper escaping)
        command = [
            'schtasks', '/create',
            '/sc', 'daily',
            '/tn', 'AgroBuild_Watering_Reminder',
            '/tr', f'{python_path_escaped} {manage_path_escaped} check_watering',
            '/st', '06:00',
            '/ru', current_user
        ]

        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Task creation failed: {result.stderr}")
        
        print("✅ Successfully created scheduled task")
        print(f"Task will run daily at 6 AM using: {python_path}")
        print(f"Logs will be written to: {log_path}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Run VS Code/PyCharm as Administrator")
        print("2. Check these paths exist:")
        print(f"   Python: {python_path}")
        print(f"   manage.py: {manage_path}")
        print("3. Try this manual command:")
        print(f'   schtasks /create /sc daily /tn "AgroBuild_Watering_Reminder" /tr "\"{python_path}\" \"{manage_path}\" check_watering" /st 06:00 /ru {current_user}')

if __name__ == "__main__":
    setup_windows_task()