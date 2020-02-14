import logging
import time
import datetime
from gevent import monkey; monkey.patch_all()
import gevent
from repofellow.github_client import GithubClient
from repofellow.gitlab_client import GitlabClient
from repofellow.parser import Parser
from repofellow.injector import Project

class Crawler:
    def __init__(self,site,injector = None):
        self.site = site
        self.client = Crawler.create_client(site)
        self.injector = injector

    def import_projects(self):
        if self.site.server_type == "github":
            data = self.client.get_projects( viewer= False )
        else:
            data = self.client.get_projects()
        projects = Parser.parse_projects(data,self.site.server_type)
        for i in projects:
            i.site = self.site.iid
        self.injector.insert_data(projects)
        return projects

    def get_project(self,project):
        return (project,self.client.get_project(project))

    #using get detail api    
    def update_projects(self):
        projects = list(self.injector.get_projects())
        per_page = 10
        pages = len(projects)/per_page + len(projects) % per_page
        page, data = 1,{}
        while page < 100:
            g = [gevent.spawn(self.get_project, i) for i in projects[per_page * (page-1):per_page * page]]
            gevent.joinall(g)
            for _,r in enumerate(g):
                data[r.value[0]] = r.value[1]
            page = page + 1
        
        if self.site.server_type == "github":
            for i in data.keys():
                Project.from_github(data[i],i)
        self.injector.db_commit()

    def import_commits(self,projects = None):
        if projects is None or projects.rstrip()=="" or projects == "*":
            import_projects = self.injector.get_projects(site = self.site.iid)
        else:
            import_projects = self.injector.get_projects(ids = projects.split(";"))
        # logging.info("total projects to update:{}".format(len(import_projects)))
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

    def import_users(self):
        if self.site.server_type == "github":
            data = self.client.get_users()
        else:
            data = self.client.get_users()
        users = Parser.parse_users(data,self.site.server_type)
        for i in users:
            i.site = self.site.iid
        print(i)
        self.injector.insert_data(users)
        return users

    @staticmethod
    def create_client(site):
        if site.server_type == "github":
            return GithubClient(site.url,site.token)
        if site.server_type == "gitlab":
            return GitlabClient(site.url,site.token)
        return None

