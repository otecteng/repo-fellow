import json
import organization
from crawler_client import CrawlerClient
import json

class GitlabClient(CrawlerClient):
    def __init__(self,site,token,data_path = "./data"):
        super(GitlabClient, self).__init__(site,token,data_path)
        self.session.headers.update({"PRIVATE-TOKEN":"{}".format(self.token)})
    
    def getProjects(self,limit = None):
        return self.getResource("/api/v4/projects?",limit = limit)

    def getProjectCommits(self,path,limit = None):
        return self.getResource("/api/v4/projects/{}/repository/commits?".format(path),limit = limit)

    def getCommit(self,project,commit):
        return self.getSingleResource("/api/v4/projects/{}/repository/commits/{}".format(project,commit))

    def get_users(self,since = ""):
        return self.getResource("/api/v4/users?")

    def get_pull_requests(self,project,state = "all"):
        return self.getResource("/api/v4/projects/{}/merge_requests?&state={}".format(project,state))

    def get_tags(self,project):
        return self.getResource("/api/v4/projects/{}/repository/tags?".format(project))

    def get_releases(self,project):
        return self.getResource("/api/v4/projects/{}/releases?".format(project))


