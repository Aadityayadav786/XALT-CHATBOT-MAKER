from dotenv import load_dotenv
load_dotenv()


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
        raise Exception(f"[❌] GitHub repo creation failed: {response.status_code} {response.json()}")


def run_cmd(cmd, msg=None):
    print(f"[🛠️] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if msg:
        print(f"[✅] {msg}")
    return result.stdout


def commit_and_push_changes(repo_url: str, repo_name="xalt-chatbot-repo"):
    import os
    import shutil
    import subprocess
    from dotenv import load_dotenv
    load_dotenv()

    original_cwd = os.getcwd()
    print(f"[📁] Preparing GitHub repo folder: {repo_name}")

    # Clean or create target repo directory
    if os.path.exists(repo_name):
        shutil.rmtree(repo_name)
    os.makedirs(repo_name)

    files_to_include = [
        "frontend.py", "requirements.txt", ".env", "rag_pipeline.py", "vector_database.py",
        "README.md", "deploy_streamlit_to_railway.py", "Dockerfile", "Procfile", "__init__.py"
    ]
    folders_to_include = ["vectorstore", "agents", "utils", "txt", "templates", "static"]

    # Copy files into the new repo folder
    for f in files_to_include:
        if os.path.exists(f):
            shutil.copy(f, repo_name)

    # Copy folders recursively into the new repo folder
    for d in folders_to_include:
        if os.path.exists(d):
            dst_path = os.path.join(repo_name, d)
            shutil.copytree(d, dst_path, dirs_exist_ok=True)

    # Change directory to the repo folder for git commands
    os.chdir(repo_name)

    # Write a .gitignore to exclude sensitive files like .env
    with open(".gitignore", "w") as f:
        f.write(".env\n")

    try:
        # Initialize Git repo and set user config
        run_cmd(["git", "init"], "Initialized Git repo")
        run_cmd(["git", "config", "user.name", "Aaditya Yadav"])
        run_cmd(["git", "config", "user.email", "aaditya@example.com"])
        run_cmd(["git", "checkout", "-b", "main"], "Created 'main' branch")

        # Embed GitHub token in repo URL for authenticated push
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN not found in environment")
        repo_url_with_token = repo_url.replace("https://", f"https://{token}@")

        run_cmd(["git", "remote", "add", "origin", repo_url_with_token], "Set remote origin with token")

        # Stage all files, remove .env from git tracking, and commit
        run_cmd(["git", "add", "."], "Staged files for commit")
        subprocess.run(["git", "rm", "--cached", ".env"], stderr=subprocess.DEVNULL)
        run_cmd(["git", "commit", "-m", "Initial commit"], "Committed all files")

        # Push to GitHub
        run_cmd(["git", "push", "-u", "origin", "main"], "Pushed to GitHub")
        print("[🚀] Repo deployed to GitHub successfully")

    except subprocess.CalledProcessError as e:
        print(f"[❌] Command failed: {e.cmd}")
        print(f"[❌] Error Output:\n{e.stderr}")
        raise

    finally:
        # Restore original working directory after all git operations
        os.chdir(original_cwd)
