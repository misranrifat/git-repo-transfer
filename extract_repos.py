import requests
import csv
import logging

class GitHubRepoExtractor:
    """
    Extracts public and private repositories for a given GitHub username.
    If a token is provided and matches the username, private repos are included.
    """
    def __init__(self, username, token=None, output_file='github_repos.csv'):
        self.username = username
        self.token = token
        self.output_file = output_file
        self.headers = {}
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_authenticated_username(self):
        """Return the username associated with the provided token, or None."""
        if not self.token:
            return None
        resp = requests.get('https://api.github.com/user', headers=self.headers)
        if resp.status_code == 200:
            return resp.json().get('login', None)
        self.logger.error(f"Failed to authenticate with provided token: {resp.status_code} {resp.text}")
        return None

    def fetch_repos(self):
        """Fetch all repositories (public and private if possible) for the user."""
        repos = []
        page = 1

        # Determine correct endpoint
        authenticated_username = self.get_authenticated_username()
        if authenticated_username and authenticated_username.lower() == self.username.lower():
            url_base = 'https://api.github.com/user/repos'
            self.logger.info("Fetching public and private repositories for the authenticated user.")
        else:
            url_base = f'https://api.github.com/users/{self.username}/repos'
            self.logger.info("Fetching public repositories for the user.")

        while True:
            params = {'per_page': 100, 'page': page}
            response = requests.get(url_base, headers=self.headers, params=params)
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch repos: {response.status_code} {response.text}")
                break
            data = response.json()
            if not data:
                break
            repos.extend(data)
            self.logger.debug(f"Fetched page {page} with {len(data)} repos.")
            page += 1

        self.logger.info(f"Total repositories fetched: {len(repos)}")
        return repos

    def save_to_csv(self, repos):
        """Save repository names to a CSV file."""
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['repo_name'])
            for repo in repos:
                writer.writerow([repo['full_name']])
        self.logger.info(f"Saved {len(repos)} repositories to {self.output_file}")

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    username = "your_github_username"
    token = "your_github_personal_access_token"
    output_file = 'github_repos.csv'

    extractor = GitHubRepoExtractor(username, token, output_file)
    repos = extractor.fetch_repos()
    extractor.save_to_csv(repos)

if __name__ == "__main__":
    main()
