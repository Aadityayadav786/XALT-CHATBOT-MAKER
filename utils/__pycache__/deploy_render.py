import asyncio
from utils.load_env import load_env_file
from utils.render_utils import deploy_to_render  # Updated path if needed

def deploy():
    env_vars = load_env_file()

    print("[🧬] Adding environment variables to Render...")
    for key, value in env_vars.items():
        print(f"[🔐] Setting {key} = {'*' * 8}")  # Obfuscate secret output

    return env_vars

async def main():
    env_vars = deploy()  # Load and print environment setup
    result = await deploy_to_render(env_vars)  # Pass env_vars to Render deploy
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
