import logging
import time
import datetime
from gevent import monkey; monkey.patch_all()
import gevent
from repofellow.github_client import GithubClient
from repofellow.gitlab_client import GitlabClient
from repofellow.parser import Parser
from repofellow.injector import Project,Developer,Tag,Release
from repofellow.decorator import log_time

class Crawler:
    @staticmethod
    def create_client(site):
        if site.server_type == "github":
            return GithubClient(site.url,site.token)
        if site.server_type == "gitlab":
            return GitlabClient(site.url,site.token)
        return None


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
    def update_projects(self,projects = None):
        if projects is None:
            projects = self.injector.get_projects(site = self.site.iid)

        for paged_objs in self.page_objects(projects,100):
            data = self.execute_parallel(self.get_project,paged_objs)
            [Project.from_github(data[i],i) for i in data]    
        self.injector.db_commit()

    def get_project_statistic(self,project):
        return (project,self.client.get_project_statistic(project))

    @log_time
    def statistic_projects(self,projects = None):
        if projects is None:
            projects = self.injector.get_projects(site = self.site.iid)

        for paged_objs in self.page_objects(projects,100):
            data = self.execute_parallel(self.get_project_statistic,paged_objs)
            [Project.statistic_github(data[i],i) for i in data]    
        self.injector.db_commit()

    def updated_project_commits(self,project):
        return (project,self.client.get_commit_pages(project))

    @log_time
    def commits_projects(self,projects = None):
        if projects is None:
            projects = self.injector.get_projects(site = self.site.iid)
        for paged_objs in self.page_objects(projects,100):
            data = self.execute_parallel(self.updated_project_commits,paged_objs)
            for project in data:
                project.commits = data[project] * self.client.recordsPerPage
        self.injector.db_commit()
        
    @log_time
    def import_commits(self,projects = None,limit = None):
        if projects is None:
            projects = self.injector.get_projects(site = self.site.iid)
        # logging.info("total projects to update:{}".format(len(import_projects)))
        for i in projects:
            last_commit = self.injector.get_project_last_commit(i.path)
            if last_commit is not None:
                commits = self.client.getProjectCommits(i, since = last_commit.created_at + datetime.timedelta(seconds=1),limit = limit)
            else:
                commits = self.client.getProjectCommits(i,limit = limit)
            logging.info("{} new commit number {}".format(i.path,len(commits)))
            new_commits = Parser.parse_commits(commits,format=self.site.server_type,project = i.path)
            self.injector.insert_data(new_commits)

    @log_time
    def get_tags(self,projects = None, with_commits = False):
        if projects is None:
            projects = self.injector.get_projects(site = self.site.iid)
        # logging.info("total projects to update:{}".format(len(import_projects)))
        commits = []
        for i in projects:
            tags = self.client.get_tags(i)
            logging.info("{} new tag number {}".format(i.path,len(tags)))
            tags = Parser.json_to_db(tags,Tag,site = self.site)
            for x in tags:
                x.project_oid = i.oid
                if with_commits:
                    commits.append((i.path,x.commit))
                    # commit_data = self.client.get_commit(i.path,x.commit)
                    # commit = Parser.parse_commits([commit_data],format=self.site.server_type,project = i.path)
                    # self.injector.insert_data(commit)
            self.injector.insert_data(tags)
            logging.info("check your tags for duplicated commits")

    @log_time
    def import_releases(self,projects = None):
        if projects is None:
            projects = self.injector.get_projects(site = self.site.iid)
        # logging.info("total projects to update:{}".format(len(import_projects)))
        ret = []
        for i in projects:
            data = self.client.get_releases(i)
            logging.info("{} new release number {}".format(i.path,len(data)))
            data = Parser.json_to_db(data,Release,site = self.site)
            for j in data:
                j.project = i.path
                j.project_oid = i.oid
                ret = ret + data
        self.injector.insert_data(ret)
        return ret

    @log_time
    def import_users(self):
        data = self.client.get_users()
        users = Parser.json_to_db(data,Developer,format = self.site.server_type, site = self.site)
        self.injector.insert_data(users)
        return users

