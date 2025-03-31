# API Key Security Best Practices

This document provides guidelines for handling API keys and sensitive credentials securely in your projects.

## Why API Key Security Matters

API keys are essentially passwords to your services. If leaked:
- Unauthorized users can access your services
- You may incur unexpected charges
- Your rate limits may be exhausted
- Your account could be compromised

## Best Practices

### 1. Never Commit API Keys to Git

- **Use environment variables**: Store API keys in `.env` files that are excluded from git
- **Use `.gitignore`**: Ensure `.env` files and other credential files are in your `.gitignore`
- **Check before committing**: Use tools like `git diff --staged` to review changes before committing

### 2. Use Environment Variables

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access API key
api_key = os.environ.get("OPENROUTER_API_KEY")
```

### 3. Provide Examples Without Real Keys

- Create `.env.example` files with placeholder values
- Document the required environment variables in your README

Example `.env.example`:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 4. Rotate Compromised Keys Immediately

If you accidentally commit an API key:
1. Immediately invalidate/rotate the key in the service provider's dashboard
2. Remove the key from git history (see below)
3. Update your local `.env` file with the new key

### 5. Regularly Scan for Leaked Credentials

- Use the provided `check_for_api_keys.py` script before making your repository public
- Consider setting up pre-commit hooks to prevent committing secrets

### 6. What to Do If You've Already Committed API Keys

If you've already committed API keys to your repository:

1. **Rotate your keys immediately** - Consider any committed key as compromised
2. **For private repositories**: 
   - Use the `prepare_clean_repo.py` script to create a clean export
   - Create a new repository with the clean export
3. **For public repositories**:
   - Create a new repository with a clean export
   - Consider using tools like BFG Repo-Cleaner or git-filter-repo for large repositories

## Tools for Managing Secrets

- **Environment files**: `.env` with `python-dotenv`
- **Secret management services**: AWS Secrets Manager, HashiCorp Vault, etc.
- **CI/CD secrets**: GitHub Secrets, GitLab CI/CD Variables, etc.

## Pre-commit Hooks

Consider setting up pre-commit hooks to prevent committing secrets:

```bash
# Install pre-commit
pip install pre-commit

# Create a .pre-commit-config.yaml file
cat > .pre-commit-config.yaml << EOF
repos:
-   repo: https://github.com/gitleaks/gitleaks
    rev: v8.16.1
    hooks:
    -   id: gitleaks
EOF

# Install the hooks
pre-commit install
```

## Remember

- API keys in git history are still accessible even after you remove them from your code
- Always assume that any key that has been committed is compromised
- When in doubt, rotate your keys
