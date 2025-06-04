# utils/load_env.py
import os
from dotenv import load_dotenv

def load_env_file(env_path=".env"):
    print("[🔐] Loading environment variables from .env...")
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        print("[✅] .env file loaded successfully.")
    else:
        print("[⚠️] .env file not found. Skipping load.")

    return {
        "COHERE_API_KEY": os.getenv("COHERE_API_KEY"),
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
         "RENDER_API_KEY": os.getenv("RENDER_API_KEY"),
    }