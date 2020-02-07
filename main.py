import os
import organization
from parser import Parser
from injector import Injector,Commit
from github_client import GithubClient
from gitlab_client import GitlabClient
# import gevent

def get_github_commits(project):
    commits = Parser.parse_commits(client.getProjectCommits(project),format="github")
    for j in commits:
        j.project = i.path
    Injector(password=os.environ['FELLOW_PASSWORD']).insert_data(commits)
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

# injector.db_test()
# injector.db_commit()
get_github_projects()
# if os.environ['GIT_SERVER'] == "github":
#     get_github_projects()

# if os.environ['GIT_SERVER'] == "gitlab":
#     get_gitlab_projects()

# g = [gevent.spawn(get, url) for url in urls]
# gevent.joinall(g)