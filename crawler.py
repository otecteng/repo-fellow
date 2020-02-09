from github_client import GithubClient
from gitlab_client import GitlabClient

class Crawler:
    @staticmethod
    def create_client(server,site,token):
        if server == "github":
            return GithubClient(site,token)
        if server == "gitlab":
            return GitlabClient(site,token)
        return None