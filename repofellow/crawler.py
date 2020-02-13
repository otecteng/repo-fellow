import logging
import datetime
from repofellow.github_client import GithubClient
from repofellow.gitlab_client import GitlabClient
from repofellow.parser import Parser

class Crawler:
    def __init__(self,site,injector = None):
        self.site = site
        self.client = Crawler.create_client(site)
        self.injector = injector

    def import_projects(self):
        data = self.client.get_projects()
        projects = Parser.parse_projects(data,self.site.server_type)
        for i in projects:
            i.site = self.site.iid
        self.injector.insert_data(projects)
        return projects

    def import_commits(self,projects = None):
        if projects is None or projects.rstrip()=="" or projects == "*":
            import_projects = self.injector.get_projects(self.site.iid)
        else:
            import_projects = self.injector.get_projects(ids = projects.split(";"))

        for i in import_projects:
            project = i.path
            logging.info("update project commits:{}".format(project))
            last_commit = self.injector.get_project_last_commit(project)
            if last_commit is not None:
                commits = self.client.getProjectCommits(i, since = last_commit.created_at + datetime.timedelta(seconds=1))
            else:
                commits = self.client.getProjectCommits(i)
            logging.info("{} new commit number {}".format(project,len(commits)))
            new_commits = Parser.parse_commits(commits,format=self.site.server_type,project = project)
            self.injector.insert_data(new_commits)

    @staticmethod
    def create_client(site):
        if site.server_type == "github":
            return GithubClient(site.url,site.token)
        if site.server_type == "gitlab":
            return GitlabClient(site.url,site.token)
        return None

