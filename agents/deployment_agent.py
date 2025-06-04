import os
import time
from utils.github_utils import create_github_repo, commit_and_push_changes
from utils.load_env import load_env_file  # ✅ Use the custom env loader

class DeploymentAgent:
    def __init__(self):
        # Load environment variables from .env
        env_vars = load_env_file()


        # Repo details
        ts = int(time.time())
        self.repo_name = f"xalt-chatbot-repo-{ts}"
        self.github_repo_url = None

    def deploy_now(self) -> str:
        # 1️⃣ Create GitHub repo
        print("[1/2] Creating GitHub repository…")
        self.github_repo_url = create_github_repo(self.repo_name)
        print(f"[✅] GitHub repo created: {self.github_repo_url}")

        # 2️⃣ Push code to GitHub
        print("[2/2] Pushing project files to GitHub…")
        commit_and_push_changes(self.github_repo_url, self.repo_name)
        print("[✅] Code pushed to GitHub")


        return self.github_repo_url

