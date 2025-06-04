import subprocess
import time

def create_render_service(service_name, repo_url):
    """
    Creates a new Render web service using the Render CLI.

    Args:
        service_name (str): The name of the Render service.
        repo_url (str): The GitHub repository URL.

    Returns:
        bool: True if service was created successfully, False otherwise.
    """
    print(f"Creating Render service: {service_name}")

    command = [
        "render", "services", "create",
        "--name", service_name,
        "--type", "web",
        "--env", "python",
        "--region", "oregon",
        "--repo", repo_url,
        "--branch", "main",
        "--buildCommand", "pip install -r requirements.txt",
        "--startCommand", "streamlit run app.py --server.port $PORT"
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print("Error creating Render service:\n", result.stderr)
        return False

    print("Render service created successfully.")
    return True


def get_render_url(service_name):
    """
    Fetches the public URL of a Render service by listing services.

    Args:
        service_name (str): The name of the service.

    Returns:
        str or None: The public URL if found, else None.
    """
    result = subprocess.run(["render", "services", "list"], capture_output=True, text=True)

    if result.returncode != 0:
        print("Error listing Render services:\n", result.stderr)
        return None

    for line in result.stdout.splitlines():
        if service_name in line:
            parts = line.split()
            for part in parts:
                if part.startswith("https://"):
                    return part  # Return the first URL found

    print(f"Service '{service_name}' not found or URL not parsed correctly.")
    return None
