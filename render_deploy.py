import requests
import time
import os
import uuid

def get_owner_id(render_api_key):
    """Fetch the ownerID needed for Render service creation."""
    headers = {
        "Authorization": f"Bearer {render_api_key}",
        "Accept": "application/json"
    }
    response = requests.get("https://api.render.com/v1/owners", headers=headers)
    response.raise_for_status()
    owners = response.json()

    print("Owners response from Render API:", owners)  # Debug print

    if not owners:
        raise Exception("No owners found for this Render API key.")
    
    first_owner = owners[0]

    if "owner" not in first_owner or "id" not in first_owner["owner"]:
        raise Exception("Owner data missing 'id' field.")
    
    return first_owner["owner"]["id"]



def create_web_service(github_repo, service_name, render_api_key, owner_id):
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {render_api_key}",
        "content-type": "application/json"
    }

    payload = {
        "type": "web_service",
        "name": service_name,
        "ownerId": owner_id,
        "repo": github_repo,
        "branch": "main",
        "plan": "free",
        "region": "oregon",
        "serviceDetails": {
        "env": "python",
        "envSpecificDetails": {
            "pythonVersion": "3.11" ,
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "streamlit run frontend.py --server.port $PORT"
        }
    }
        
    }

    response = requests.post("https://api.render.com/v1/services", json=payload, headers=headers)
    data = response.json()
    print("Create service response:", data)

    if response.status_code != 201:
        raise Exception(f"Service creation failed: {data.get('message', 'Unknown error')}")

    return data["id"]

def wait_for_deployment(service_id, render_api_key, timeout=300):
    headers = {"accept": "application/json", "authorization": f"Bearer {render_api_key}"}
    url = f"https://api.render.com/v1/services/{service_id}/deploys"

    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data and data[0]['deploy']['status'] == "live":
            return True
        time.sleep(10)
    return False

def get_public_url(service_id, render_api_key):
    headers = {"accept": "application/json", "authorization": f"Bearer {render_api_key}"}
    url = f"https://api.render.com/v1/services/{service_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["service"]["url"]  # Correct field for public URL

def deploy_to_render(github_repo_url, render_api_key=None):
    """Wrapper to deploy a GitHub repo to Render and return the live URL."""
    if render_api_key is None:
        render_api_key = os.getenv("RENDER_API_KEY")
    if not render_api_key:
        raise Exception("RENDER_API_KEY not provided or missing in environment.")

    # Get owner ID first
    owner_id = get_owner_id(render_api_key)

    # Generate a unique service name
    service_name = f"chatbot-{uuid.uuid4().hex[:6]}"

    service_id = create_web_service(github_repo_url, service_name, render_api_key, owner_id)
    success = wait_for_deployment(service_id, render_api_key)

    if not success:
        raise Exception("Deployment timed out or failed.")

    return get_public_url(service_id, render_api_key)
