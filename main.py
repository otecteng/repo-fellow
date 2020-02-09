"""repo crawler via command-line.

Usage:
    repo-fellow project <command> [<args>]
    repo-fellow user <command> [<args>]
    repo-fellow commit <command> [<args>]
    repo-fellow event <command> [<args>]
Options: 
    -h,--help        

Example:
    repo-fellow projects remote owner
    repo-fellow projects list
    repo-fellow commit update *
    repo-fellow commit update project_x
"""
import os
import datetime
from docopt import docopt
from crawler import Crawler
from injector import Injector,Commit
from parser import Parser
if __name__ == '__main__':
    arguments = docopt(__doc__, version='Repo Fellow')
    server, site, token = os.environ['GIT_SERVER'], os.environ['GIT_SITE'], os.environ['GIT_TOKEN']
    db_user, db_password = "repo",os.environ['FELLOW_PASSWORD']
    command = arguments["<command>"]
    if arguments["project"]:
        if command == "list":
            print("not implemented")
        if command == "remote":
            commits = Crawler.create_client(server,site,token).getAllProjectCommitsCount(arguments["<args>"])
            for i in commits:
                if i["ref"]:
                    print("{}:{}".format(i["name"],i["ref"]["target"]["history"]["totalCount"]))
                else:
                    print("[ERROR]: {} has none history record".format(i["name"]))

    if arguments["commit"]:
        if command == "update":
            injector = Injector(password = db_password)
            if arguments["<args>"]:
                projects = [injector.get_project(arguments["<args>"])]
            else:
                projects = injector.get_projects()
            for i in projects:
                project = i.path
                print("update project commits:{}".format(project))
                crawler = Crawler.create_client(server,site,token)
                commit = injector.get_project_last_commit(project)
                if commit is not None:
                    commits = crawler.getProjectCommits(project, since = commit.created_at + datetime.timedelta(seconds=1))
                else:
                    commits = crawler.getProjectCommits(project)
                print("[INFO]:{} new commit number {}".format(project,len(commits)))
                new_commits = Parser.parse_commits(commits,format="github")
                for j in new_commits:
                    j.project = project
                Injector(password = db_password).insert_data(new_commits)
