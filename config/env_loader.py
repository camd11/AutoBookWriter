import os
import logging
from pathlib import Path

def load_env_file(env_file='.env'):
    """
    Load environment variables from a .env file
    
    Args:
        env_file (str): Path to the .env file
        
    Returns:
        bool: True if the .env file was loaded successfully, False otherwise
    """
    env_path = Path(env_file)
    
    if not env_path.exists():
        logging.warning(f".env file not found at {env_path.absolute()}. Using existing environment variables.")
        return False
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            # Parse key-value pairs
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                # Set environment variable if not already set
                if key not in os.environ:
                    os.environ[key] = value
                    logging.debug(f"Set environment variable: {key}")
    
    return True

def ensure_env_loaded():
    """
    Ensure environment variables are loaded from .env file
    """
    # Try to load from .env file
    env_loaded = load_env_file()
    
    # Check if required environment variables are set
    required_vars = ['OPENROUTER_API_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        missing_vars_str = ', '.join(missing_vars)
        if not env_loaded:
            logging.error(
                f"Missing required environment variables: {missing_vars_str}. "
                f"Please create a .env file or set them manually."
            )
            print(f"""
ERROR: Missing required environment variables: {missing_vars_str}

Please set up your environment variables by either:
1. Creating a .env file (recommended):
   cp .env.example .env
   Then edit .env with your actual API keys

2. Setting environment variables manually:
   export OPENROUTER_API_KEY=your_api_key_here

For more information, see the README.md file.
""")
        else:
            logging.error(
                f"Missing required environment variables: {missing_vars_str}. "
                f"Please check your .env file."
            )
    
    return not missing_vars
