def load_dot_env(env_file: str = '.env'):
    """Load .env file."""
    with open(env_file) as f:
        import os

        for line in f:
            # If begings with # or is empty, skip
            if line.startswith("#") or line == "\n":
                continue
            key, value = line.strip().split("=")
            if key not in os.environ:
                print(f"Setting environment variable: {key}=****")
                os.environ[key] = value