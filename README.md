# GitHub Repository Transfer Tool

A Python script to automate the transfer of GitHub repositories between accounts.

## Configuration

1. Create a GitHub Personal Access Token:
   - Go to GitHub Settings > Developer Settings > Personal Access Tokens
   - Generate a new token with `repo` scope
   - Copy the token

2. Update the configuration in `transfer.py`:
```python
config = Config(
    github_token="your_github_token",
    old_owner="source_account",
    new_owner="destination_account"
)
```

## CSV Format

Create a CSV file named `github_repos.csv` with a single column:
- `repo_name`: Name of the repository to transfer

Example:
```csv
repo_name
test-repo-1
test-repo-2
test-repo-3
```

## Usage

Run the script:
```bash
python transfer.py
```