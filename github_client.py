import json
import organization
import json
from crawler_client import CrawlerClient

class GithubClient(CrawlerClient):
    def __init__(self,site,token,data_path = "./data"):
        super(GithubClient, self).__init__(site,token,data_path)
        self.session.headers.update({"Authorization":"Bearer {}".format(self.token)})

    def gqResource(self,query):
        first,afer = "",""
        self.session.headers.update({"Content-Type":"application/json"})
        reponse = self.session.post(self.site + "/api/graphql",json = {"query":query})
        return reponse.json()
    
    def getProjects(self,start_from = None,limit = None, last = None):
        return self.getResource("/api/v3/user/repos?sort=created", start_from, limit ,  last)

    def getProjectCommits(self, path, limit = None, since = None):
        owner,name = path.split("/")
# {repository (owner:"",name: "") {ref(qualifiedName: "master") {target {
#                     ... on Commit { history(first: 100) { edges { node { 
#                         author{ name } oid authoredDate message }} }}   }}}
# }
        if since:
            return self.getResource("/api/v3/repos/{}/{}/commits?since={}".format(owner,name,since.strftime("%Y-%m-%dT%H:%M:%SZ")),limit = limit)
        else:
            return self.getResource("/api/v3/repos/{}/{}/commits?".format(owner,name),limit = limit)

    def getCommit(self,project,commit):
        return self.getSingleResource("/api/v3/repos/{}/commits/{}".format(project,commit))


