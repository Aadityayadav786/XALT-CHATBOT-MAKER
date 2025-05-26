# utils/github_utils.py

import requests
import os
import subprocess
import shutil

def create_github_repo(repo_name):
    token = os.getenv("GITHUB_TOKEN")
    username = os.getenv("GITHUB_USERNAME")

    if not token or not username:
        raise ValueError("GITHUB_TOKEN or GITHUB_USERNAME not set in .env")

    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "private": False
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print("[✅] GitHub repo created successfully")
        return f"https://github.com/{username}/{repo_name}.git"
    else:
        raise Exception(f"GitHub repo creation failed: {response.json()}")


def commit_and_push_changes(repo_url: str, repo_name="xalt-chatbot-repo"):
    if not os.path.exists(repo_name):
        os.makedirs(repo_name)

    # Files and folders to copy
    files_to_include = [
        "frontend.py", "requirements.txt", ".env", "rag_pipeline.py", "vector_database.py",
        "README.md", "deploy_streamlit_to_railway.py", "Dockerfile", "Procfile", "__init__.py"
    ]
    folders_to_include = ["vectorstore", "agents", "utils", "txt", "templates", "static"]

    # Copy files
    for f in files_to_include:
        if os.path.exists(f):
            shutil.copy(f, repo_name)

    # Copy folders
    for d in folders_to_include:
        if os.path.exists(d):
            if os.path.isdir(d):
                shutil.copytree(d, os.path.join(repo_name, d), dirs_exist_ok=True)
            else:
                shutil.copy(d, os.path.join(repo_name, d))

    # Move into the repo directory
    os.chdir(repo_name)

    # Write .gitignore to exclude .env
    with open(".gitignore", "w") as f:
        f.write(".env\n")

    # Initialize Git and set user identity
    subprocess.run(["git", "init"])
    subprocess.run(["git", "config", "user.name", "Aaditya Yadav"])
    subprocess.run(["git", "config", "user.email", "aaditya@example.com"])  # Replace with your real email

    subprocess.run(["git", "remote", "add", "origin", repo_url])
    subprocess.run(["git", "branch", "-M", "main"])  # Ensures branch is named main

    # Stage everything
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "rm", "--cached", ".env"], stderr=subprocess.DEVNULL)  # Remove .env if accidentally staged

    # Commit and push
    subprocess.run(["git", "commit", "-m", "Initial commit without secrets"])
    subprocess.run(["git", "push", "-u", "origin", "main"])

    print("[✅] Code pushed to GitHub without .env file")
