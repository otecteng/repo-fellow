import os
import datetime
import organization
from parser import Parser
from injector import Injector,Commit
from crawler import Crawler
from github_client import GithubClient
from gitlab_client import GitlabClient
# import gevent

def get_commits(project,since = None, limit = None):
    commits = Crawler.create_client(os.environ['GIT_SERVER'],os.environ['GIT_SITE'],os.environ['GIT_TOKEN']).getProjectCommits(project, since = since, limit = limit )
    commits = Parser.parse_commits(commits,format="github")
    for j in commits:
        j.project = project
    # Injector(password = os.environ['FELLOW_PASSWORD']).insert_data(commits)
    return commits

def get_github_commit(commit):
    try:
        commit_info = client.getCommit(commit.project,commit.id)
        commit = Commit.append_count_github(commit,commit_info)
        injector.db_commit()
    except Exception:
        print("[error]:{}:{}".format(commit.project,commit.id))

def get_github_projects():
    projects = GithubClient(os.environ['GIT_SITE'],os.environ['GIT_TOKEN']).getProjects()
    for i in Parser.parse_projects(projects,format = "github"):
        print(i)
    # Injector(password=os.environ['FELLOW_PASSWORD']).insert_data(Parser.parse_projects(projects))

def get_gitlab_projects():
    projects = GitlabClient(os.environ['GIT_SITE'],os.environ['GIT_TOKEN']).getProjects()
    for i in Parser.parse_projects(projects,format = "gitlab"):
        print(i)

# read github project commits count by GraphQL API
commits = Crawler.create_client(os.environ['GIT_SERVER'],os.environ['GIT_SITE'],os.environ['GIT_TOKEN']).getAllProjectCommitsCount("owner")
for i in commits:
    if i["ref"]:
        print("{}:{}".format(i["name"],i["ref"]["target"]["history"]["totalCount"]))
    else:
        print("[ERROR]: {} has none history record".format(i["name"]))

# injector = Injector(password = os.environ['FELLOW_PASSWORD'])
# projects = injector.get_projcets()
# for i in projects:
#     print("update project commits:{}".format(i.path))
#     commit = injector.get_project_last_commit(i.path)
#     if commit is not None:
#         new_commits = get_commits(commit.project,since = commit.created_at + datetime.timedelta(seconds=1))
#     else:
#         new_commits = get_commits(commit.project)
#     print("new records of {} is:{}".format(i.path,len(new_commits)))
#     Injector(password = os.environ['FELLOW_PASSWORD']).insert_data(new_commits)


# g = [gevent.spawn(get, url) for url in urls]
# gevent.joinall(g)