import csv
import time
import logging
import requests
from typing import Dict, List
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Config:
    github_token: str
    old_owner: str
    new_owner: str


class GitHubTransfer:
    def __init__(self, config: Config):
        self.config = config
        self.headers = {
            "Authorization": f"token {config.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.base_url = "https://api.github.com"

    def validate_config(self) -> bool:
        if not all(
            [self.config.github_token, self.config.old_owner, self.config.new_owner]
        ):
            logger.error(
                "Missing required configuration: token, old_owner, or new_owner"
            )
            return False
        return True

    def transfer_repo(self, repo_name: str) -> bool:
        url = f"{self.base_url}/repos/{self.config.old_owner}/{repo_name}/transfer"
        payload = {"new_owner": self.config.new_owner}

        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=30)
            resp.raise_for_status()
            logger.info(f"{repo_name} transfer initiated successfully")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"{repo_name} transfer failed: {str(e)}")
            if hasattr(e.response, "json"):
                logger.error(f"Details: {e.response.json()}")
            return False

    def process_repositories(self, csv_path: str) -> Dict[str, List[str]]:
        if not Path(csv_path).exists():
            logger.error(f"CSV file not found: {csv_path}")
            return {"success": [], "failed": []}

        results = {"success": [], "failed": []}

        try:
            with open(csv_path, "r") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    repo_name = row.get("repo_name")
                    if not repo_name:
                        continue

                    logger.info(f"Processing {repo_name}")
                    if self.transfer_repo(repo_name):
                        results["success"].append(repo_name)
                    else:
                        results["failed"].append(repo_name)

                    time.sleep(2)

        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            return results

        return results


def main():
    config = Config(github_token="", old_owner="", new_owner="")

    transfer = GitHubTransfer(config)

    if not transfer.validate_config():
        return

    results = transfer.process_repositories("github_repos.csv")

    logger.info("Transfer Summary:")
    logger.info(f"Successfully transferred: {len(results['success'])} repositories")
    logger.info(f"Failed transfers: {len(results['failed'])} repositories")

    if results["failed"]:
        logger.info("Failed repositories:")
        for repo in results["failed"]:
            logger.info(f"- {repo}")


if __name__ == "__main__":
    main()
