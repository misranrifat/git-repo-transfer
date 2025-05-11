import requests
import logging
from typing import List, Dict

# ====== USER CONFIGURATION ======
OLD_PERSONAL_ACCESS_TOKEN = "your_old_token_here"
NEW_PERSONAL_ACCESS_TOKEN = "your_new_token_here"
OLD_GITHUB_USERNAME = "your_old_username_here"
NEW_GITHUB_USERNAME = "your_new_username_here"
# =================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GITHUB_API = "https://api.github.com"

class GitHubStarTransfer:
    """
    A class to transfer starred repositories from one GitHub account to another.
    """
    def __init__(self, old_username: str, new_username: str, old_token: str, new_token: str) -> None:
        self.old_username = old_username
        self.new_username = new_username
        self.old_token = old_token
        self.new_token = new_token

    def get_starred_repos(self) -> List[Dict]:
        """
        Fetch all starred repositories for the old account, handling pagination.
        Returns a list of repository dicts.
        """
        starred: List[Dict] = []
        page = 1
        headers = {"Authorization": f"token {self.old_token}", "Accept": "application/vnd.github+json"}
        while True:
            url = f"{GITHUB_API}/users/{self.old_username}/starred?page={page}&per_page=100"
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                resp.raise_for_status()
            except requests.RequestException as e:
                logging.error(f"Failed to fetch stars on page {page}: {e}")
                break
            data = resp.json()
            if not data:
                break
            starred.extend(data)
            page += 1
        return starred

    def star_repo(self, owner: str, repo: str) -> bool:
        """
        Star a repository using the new account's token.
        Returns True if successful, False otherwise.
        """
        url = f"{GITHUB_API}/user/starred/{owner}/{repo}"
        headers = {"Authorization": f"token {self.new_token}", "Accept": "application/vnd.github+json"}
        try:
            resp = requests.put(url, headers=headers, timeout=10)
            if resp.status_code == 204:
                return True
            else:
                logging.error(f"Failed to star {owner}/{repo}: {resp.status_code} {resp.text}")
                return False
        except requests.RequestException as e:
            logging.error(f"Exception while starring {owner}/{repo}: {e}")
            return False

    def transfer_stars(self) -> None:
        """
        Transfer all starred repositories from the old account to the new account.
        """
        logging.info(f"Fetching starred repos for {self.old_username}...")
        starred = self.get_starred_repos()
        logging.info(f"Found {len(starred)} starred repositories.")

        for repo in starred:
            owner = repo['owner']['login']
            name = repo['name']
            logging.info(f"Starring {owner}/{name} as {self.new_username}...")
            success = self.star_repo(owner, name)
            if success:
                logging.info("Success!")
            else:
                logging.error("Failed.")

def main() -> None:
    if not all([OLD_TOKEN, NEW_TOKEN, OLD_USERNAME, NEW_USERNAME]):
        logging.error("Please set OLD_TOKEN, NEW_TOKEN, OLD_USERNAME, and NEW_USERNAME at the top of the script.")
        return
    transfer = GitHubStarTransfer(
        old_username=OLD_USERNAME,
        new_username=NEW_USERNAME,
        old_token=OLD_TOKEN,
        new_token=NEW_TOKEN
    )
    transfer.transfer_stars()

if __name__ == "__main__":
    main()
