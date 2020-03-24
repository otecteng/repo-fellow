import json
import logging
import re
import time
import repofellow.organization
from repofellow.crawler_client import CrawlerClient

class GiteeClient(CrawlerClient):
    def __init__(self,site,token,data_path = "./data"):
        super(GiteeClient, self).__init__(site,token,data_path)
        self.session.headers.update({"Authorization":"Bearer {}".format(self.token)})

    def get_projects(self, start_from = None, private = False):
        if private:
            return self.getResource("/api/v5/user/repos?visibility=private&sort=created", start_from)
        else:
            return self.getResource("/api/v5/user/repos?sort=created", start_from)
            
    def get_project_commits(self, project, limit = None, since = None, until_date = None):
        owner,name = project.path.split("/")
        url = "/api/v5/repos/{}/{}/commits?".format(owner,name)
        if since:
            url = url + "&since=" + since.strftime("%Y-%m-%dT%H:%M:%SZ")
        if until_date:
            url = url + "&until=" + until_date.strftime("%Y-%m-%dT%H:%M:%SZ")                
        return self.getResource(url,limit = limit)

    def get_project_events(self, project, limit = None, since = None, until_date = None):
        owner,name = project.path.split("/")
        url = "/api/v5/repos/{}/{}/events?".format(owner,name)
        return self.getResource(url,limit = limit, recordsPerPage= 30)

    def get_contributors(self,project):
        return self.getResource("/api/v5/repos/{}/contributors?".format(project.path))
        # return self.getResource("/api/v5/repos/{}/collaborators?".format(project.path))        

    def getCommit(self,project,commit):
        ret,_,_ = self.getSingleResource("/api/v5/repos/{}/commits/{}".format(project.path,commit))
        return ret

    def get_last_page(self,rel_last):
        if rel_last is None:
            return 1
        return int(re.split("=|>|",rel_last)[-2])

    def get_commit_pages(self,project):
        _,_,rel_last = self.getSingleResource("/api/v5/repos/{}/commits?per_page={}".format(project.path,self.recordsPerPage))
        return self.get_last_page(rel_last)

    def get_commit(self,project,commit):
        ret,_,_ = self.getSingleResource("/api/v5/repos/{}/commits/{}".format(project,commit))
        return ret

    def get_user_detail(self,user):
        ret,_,_ = self.getSingleResource("/api/v5/users/{}".format(user.username))
        return ret

    def get_user_pages(self,project):
        _,_,rel_last = self.getSingleResource("/api/v5/users?since={}&per_page={}".format(project.path,self.recordsPerPage))
        return get_last_page(rel_last)

    def get_users(self,since = ""):
        ret = []
        while True:
            data,_,_ = self.getSingleResource("/api/v5/users?since={}&per_page=100".format(since))
            ret = ret + data
            if len(data) < 100:
                break
            since = data[-1]["id"]            
        return ret

    def get_all_repos(self,since = "0"):
        ret = []
        while True:
            try:
                data,_,_ = self.getSingleResource("/api/v5/repositories?since={}&per_page=100".format(since))
                ret = ret + data
                since = data[-1]["id"]
                if len(data) < 100:
                    break
            except(Exception):
                time.sleep(1)
                continue
        return ret

    def get_project(self,project):
        ret,_,_ = self.getSingleResource("/api/v5/repositories/{}".format(project.oid))
        return ret

    def get_pull_requests(self,project,state="all"):
        return self.getResource("/api/v5/repos/{}/pulls?sort=created&state={}".format(project.path,state))

    def get_tags(self,project):
        return self.getResource("/api/v5/repos/{}/tags?".format(project.path))

    def get_releases(self,project):
        return self.getResource("/api/v5/repos/{}/releases?".format(project.path))

    def get_project_statistic(self,project):
        ret,_,_ = self.getSingleResource("/api/v5/repos/{}/stats/participation".format(project.path))
        return ret

