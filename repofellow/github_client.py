import json

import time
import repofellow.organization
import json
from repofellow.crawler_client import CrawlerClient

class GithubClient(CrawlerClient):
    def __init__(self,site,token,data_path = "./data"):
        super(GithubClient, self).__init__(site,token,data_path)
        self.session.headers.update({"Authorization":"Bearer {}".format(self.token)})

    def gqResource(self,query):
        self.session.headers.update({"Content-Type":"application/json"})
        reponse = self.session.post(self.site + "/api/graphql",json = {"query":query})
        return reponse.json()
    
    def getProjects(self,start_from = None,limit = None, last = None):
        return self.getResource("/api/v3/user/repos?sort=created", start_from, limit, last)

    def get_projects(self, start_from = None,limit = None, last = None, public = False):
        # /search/repositories?q="is:public"
        if public:
            return self.getResource("/api/v3/search/repositories?q=is:public", data_path = "items")
        else:
            return self.getResource("/api/v3/user/repos?sort=created", start_from, limit, last)

    def getAllProjectCommitsCount(self, owner, limit = None, since = None):
        query = '''
{
    repositoryOwner (login:"$owner") {
            repositories(first: $recordsPerPage, $after) {
            totalCount
            pageInfo {
                endCursor
                startCursor
            } 
            nodes{
                name
                ref(qualifiedName: "master") {
                    target {
                        ... on Commit {
                            history {
                                totalCount
                            }
                        }   
                    }
                }
            }
        }
    }
}
'''
        ret = []
        page , recordsPerPage , endCursor = 1, "100", None
        while True:
            if endCursor:
                gq_query = query.replace("$owner",owner).replace("$recordsPerPage",recordsPerPage).replace("$after","after:\"{}\"".format(endCursor))
            else:
                gq_query = query.replace("$owner",owner).replace("$recordsPerPage",recordsPerPage).replace("$after","")
            data = self.gqResource(gq_query)
            totalCount = data["data"]["repositoryOwner"]["repositories"]["totalCount"]
            endCursor = data["data"]["repositoryOwner"]["repositories"]["pageInfo"]["endCursor"]
            ret = ret + data["data"]["repositoryOwner"]["repositories"]["nodes"]
            if len(ret) == totalCount:
                break
        return ret

    def getProjectCommits(self, project, limit = None, since = None):
        owner,name = project.path.split("/")
        if since:
            return self.getResource("/api/v3/repos/{}/{}/commits?since={}".format(owner,name,since.strftime("%Y-%m-%dT%H:%M:%SZ")),limit = limit)
        else:
            return self.getResource("/api/v3/repos/{}/{}/commits?".format(owner,name),limit = limit)

    def getCommit(self,project,commit):
        return self.getSingleResource("/api/v3/repos/{}/commits/{}".format(project,commit))

    def get_user_detail(self,login):
        return self.getSingleResource("/api/v3/users/{}".format(login))

    def get_users(self,since = ""):
        ret = []
        while True:
            try:
                data = self.getSingleResource("/api/v3/users?since={}&per_page=100".format(since))
                ret = ret + data
                since = data[-1]["id"]
                if len(data) < 100:
                    break
            except(Exception):
                time.sleep(1)
                continue
        return ret

    def get_pull_requests(self,project,state="all"):
        return self.getResource("/api/v3/repos/{}/pulls?sort=created&state={}".format(project,state))

    def get_tags(self,project):
        return self.getResource("/api/v3/repos/{}/tags".format(project))

    def get_releases(self,project):
        return self.getResource("/api/v3/repos/{}/releases".format(project))
