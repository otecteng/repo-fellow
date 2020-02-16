import logging
import time
import datetime
from gevent import monkey; monkey.patch_all()
import gevent
from repofellow.github_client import GithubClient
from repofellow.gitlab_client import GitlabClient
from repofellow.parser import Parser
from repofellow.injector import Project,Developer,Tag
from repofellow.decorator import log_time

class Crawler:
    def __init__(self,site,injector = None):
        self.site = site
        self.client = Crawler.create_client(site)
        self.injector = injector

    def page_objects(self, objects, per_page ):
        pages, m = divmod(len(objects), per_page)
        if m > 0: pages = pages + 1
        ret = []
        for i in range(pages):
           ret.append(objects[i * per_page:(i+1)*per_page])
        return ret
    
    def execute_parallel(self,func,objects):
        ret = {}
        g = [gevent.spawn(func, i) for i in objects]
        gevent.joinall(g)
        for _,r in enumerate(g):
            ret[r.value[0]] = r.value[1]
        return ret

    def import_projects(self,private = False):
        data = self.client.get_projects(private = private)
        projects = Parser.parse_projects(data,self.site.server_type)
        for i in projects:
            i.site = self.site.iid
        self.injector.insert_data(projects)
        return projects

    def get_project(self,project):
        return (project,self.client.get_project(project))

    @log_time
    def update_projects(self,since = None):
        projects_all = list(self.injector.get_projects(site = self.site.iid, since = since))
        for projects in self.page_objects(projects_all,100):
            data = self.execute_parallel(self.get_project,projects)
            [Project.from_github(data[i],i) for i in data]    
        self.injector.db_commit()

    def get_project_statistic(self,project):
        return (project,self.client.get_project_statistic(project))

    @log_time
    def statistic_projects(self,since = None):
        projects_all = list(self.injector.get_projects(site = self.site.iid, since = since))
        for projects in self.page_objects(projects_all,100):
            data = self.execute_parallel(self.get_project_statistic,projects)
            [Project.statistic_github(data[i],i) for i in data]    
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

    @log_time
    def get_tags(self,projects = None):
        if projects is None:
            projects = self.injector.get_projects(site = self.site.iid)
        # logging.info("total projects to update:{}".format(len(import_projects)))
        for i in projects:
            tags = self.client.get_tags(i)
            logging.info("{} new tag number {}".format(i.path,len(tags)))
            tags = Parser.json_to_db(tags,Tag,site = self.site)
            for x in tags:
                x.project_oid = i.oid
            self.injector.insert_data(tags)

    @log_time
    def import_users(self):
        data = self.client.get_users()
        users = Parser.json_to_db(data,Developer,format = self.site.server_type, site = self.site)
        self.injector.insert_data(users)
        return users

    @staticmethod
    def create_client(site):
        if site.server_type == "github":
            return GithubClient(site.url,site.token)
        if site.server_type == "gitlab":
            return GitlabClient(site.url,site.token)
        return None

