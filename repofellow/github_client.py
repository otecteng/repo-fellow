import json
import logging
import re
import time
import repofellow.organization
from repofellow.crawler_client import CrawlerClient

class GithubClient(CrawlerClient):
    def __init__(self,site,data_path = "./data"):
        super(GithubClient, self).__init__(site,data_path)
        self.session.headers.update({"Authorization":"Bearer {}".format(self.token)})

    def gqResource(self,query):
        self.session.headers.update({"Content-Type":"application/json"})
        reponse = self.session.post(self.site + "/api/graphql",json = {"query":query})
        return reponse.json()
    
    def getProjects(self,start_from = None,limit = None, last = None):
        return self.getResource("/api/v3/user/repos?sort=created", start_from, limit, last)

    def get_projects(self, start_from = None, private = False):
        if private:
            return self.getResource("/api/v3/user/repos?visibility=private&sort=created", start_from)
        else:
            return self.get_all_repos()
            

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

    def get_project_commits(self, project, limit = None, since = None, until_date = None):
        owner,name = project.path.split("/")
        url = "/api/v3/repos/{}/{}/commits?".format(owner,name)
        if since:
            url = url + "&since=" + since.strftime("%Y-%m-%dT%H:%M:%SZ")
        if until_date:
            url = url + "&until=" + until_date.strftime("%Y-%m-%dT%H:%M:%SZ")                
        return self.getResource(url,limit = limit)

    def get_project_events(self, project, limit = None, since = None, until_date = None):
        owner,name = project.path.split("/")
        url = "/api/v3/repos/{}/{}/events?".format(owner,name)
        return self.getResource(url,limit = limit, recordsPerPage= 30)

    def get_contributors(self,project):
        return self.getResource("/api/v3/repos/{}/contributors?".format(project.path))
        # return self.getResource("/api/v3/repos/{}/collaborators?".format(project.path))        

    def getCommit(self,project,commit):
        ret,_,_ = self.getSingleResource("/api/v3/repos/{}/commits/{}".format(project.path,commit))
        return ret

    def get_last_page(self,rel_last):
        if rel_last is None:
            return 1
        return int(re.split("=|>|",rel_last)[-2])

    def get_commit_pages(self,project):
        _,_,rel_last = self.getSingleResource("/api/v3/repos/{}/commits?per_page={}".format(project.path,self.recordsPerPage))
        return self.get_last_page(rel_last)

    def get_commit(self,project,commit):
        ret,_,_ = self.getSingleResource("/api/v3/repos/{}/commits/{}".format(project,commit))
        return ret

    def get_user_detail(self,user):
        ret,_,_ = self.getSingleResource("/api/v3/users/{}".format(user.username))
        return ret

    def get_user_pages(self,project):
        _,_,rel_last = self.getSingleResource("/api/v3/users?since={}&per_page={}".format(project.path,self.recordsPerPage))
        return get_last_page(rel_last)

    def get_users(self,since = ""):
        ret = []
        while True:
            data,_,_ = self.getSingleResource("/api/v3/users?since={}&per_page=100".format(since))
            ret = ret + data
            if len(data) < 100:
                break
            since = data[-1]["id"]            
        return ret

    def get_all_repos(self,since = "0"):
        ret = []
        while True:
            try:
                data,_,_ = self.getSingleResource("/api/v3/repositories?since={}&per_page=100".format(since))
                ret = ret + data
                since = data[-1]["id"]
                if len(data) < 100:
                    break
            except(Exception):
                time.sleep(1)
                continue
        return ret

    def get_project(self,project):
        ret,_,_ = self.getSingleResource("/api/v3/repositories/{}".format(project.oid))
        return ret

    def get_pull_requests(self,project,state="all"):
        return self.getResource("/api/v3/repos/{}/pulls?sort=created&state={}".format(project.path,state))

    def get_tags(self,project):
        return self.getResource("/api/v3/repos/{}/tags?".format(project.path))

    def get_releases(self,project):
        return self.getResource("/api/v3/repos/{}/releases?".format(project.path))

    def get_branches(self,project):
        return self.getResource("/api/v3/repos/{}/branches?".format(project.path))

    def get_project_statistic(self,project):
        ret,_,_ = self.getSingleResource("/api/v3/repos/{}/stats/participation".format(project.path))
        return ret

    def get_groups(self):
        query = '''
{
  search(query: "type:org", type: USER,first: $recordsPerPage, $after) {
    userCount
    pageInfo {
        endCursor
        startCursor
    }     
    edges {
      node {
        ... on Organization {
          name
          location
          description
          repositories(first: 1){
            totalCount
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
                gq_query = query.replace("$recordsPerPage",recordsPerPage).replace("$after","after:\"{}\"".format(endCursor))
            else:
                gq_query = query.replace("$recordsPerPage",recordsPerPage).replace("$after","")
            # logging.info(gq_query)
            data = self.gqResource(gq_query)
            if "errors" in data:
                logging.error(data["errors"])
                break
            totalCount = data["data"]["search"]["userCount"]
            endCursor = data["data"]["search"]["pageInfo"]["endCursor"]            
            ret = ret + list(map(lambda x: x["node"],data["data"]["search"]["edges"]))
            if endCursor is None or len(ret) == totalCount:
                break
        return ret

    def get_users_gq(self):
        query = '''
{
  search(query: "type:user", type: USER,first: $recordsPerPage, $after) {
    userCount
    pageInfo {
        endCursor
        startCursor
    }     
    edges {
      node {
        ... on User {
          login
          name
          location
          email
          repositories(first: 1){
            totalCount
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
            logging.info("reading page {} perpage {}".format(page,recordsPerPage))
            if endCursor:
                gq_query = query.replace("$recordsPerPage",recordsPerPage).replace("$after","after:\"{}\"".format(endCursor))
            else:
                gq_query = query.replace("$recordsPerPage",recordsPerPage).replace("$after","")
            data = self.gqResource(gq_query)
            if "errors" in data:
                logging.error(data["errors"])
                break
            result = list(map(lambda x: x["node"],data["data"]["search"]["edges"]))
            if len(result) == 0:
                logging.info(gq_query)
                logging.info(data)
                time.sleep(1)
                break

            totalCount = data["data"]["search"]["userCount"]
            endCursor = data["data"]["search"]["pageInfo"]["endCursor"]
            
            logging.info("result count {}".format(len(result)))
            ret = ret + result
            logging.info("totalCount {} data lenth count {}".format(totalCount,len(ret)))
            if len(ret) == totalCount:
                break
            page = page + 1
        return ret