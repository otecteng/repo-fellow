import json
import repofellow.organization
from repofellow.crawler_client import CrawlerClient
import json

class GitlabClient(CrawlerClient):
    def __init__(self,site,data_path = "./data"):
        super(GitlabClient, self).__init__(site,data_path)
        self.session.headers.update({"PRIVATE-TOKEN":"{}".format(self.token)})
    
    def getProjects(self,limit = None):
        return self.getResource("/api/v4/projects?",limit = limit)

    def get_projects(self, start_from = None, private = False):
        if private:
            return self.getResource("/api/v4/projects?membership=true".format(self.site.user))
        else:
            return self.getResource("/api/v4/projects?")
            

    def get_project_commits(self, project, limit = None, since = None, until_date = None):
        return self.getResource("/api/v4/projects/{}/repository/commits?".format(project.oid),limit = limit)

    def getCommit(self,project,commit):
        return self.getSingleResource("/api/v4/projects/{}/repository/commits/{}".format(project,commit))

    def get_commits(self,project,since = ""):
        return self.getResource("/api/v4/projects/{}/repository/commits?since={}".format(project,since))

    def get_users(self,since = ""):
        return self.getResource("/api/v4/users?")

    def get_pull_requests(self,project,state = "all"):
        return self.getResource("/api/v4/projects/{}/merge_requests?&state={}".format(project.oid,state))

    def get_tags(self,project):
        return self.getResource("/api/v4/projects/{}/repository/tags?".format(project.oid))

    def get_releases(self,project):
        return self.getResource("/api/v4/projects/{}/releases?".format(project.oid))


