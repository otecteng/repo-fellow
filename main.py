"""repo crawler via command-line.

Usage:
    repo-fellow project <command> [<args>]
    repo-fellow user <command> [<args>]
    repo-fellow commit <command> [<args>]
    repo-fellow event <command> [<args>]
    repo-fellow db <command> [<args>]
    repo-fellow pr <command> [<args>]

Options: 
    -h,--help        

Example:
    repo-fellow projects remote owner
    repo-fellow projects list
    repo-fellow projects import
    repo-fellow commit update *
    repo-fellow commit update project_x
"""
import os
import datetime
import logging
from docopt import docopt
from crawler import Crawler
from injector import Injector,Commit
from parser import Parser
from repo_mysql import RepoMySQL
if __name__ == '__main__':
    logging.basicConfig(filename = "log/fellow.log", level = logging.INFO, format = "%(asctime)s %(message)s", filemode='a')
    logger = logging.getLogger()    
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    arguments = docopt(__doc__, version = 'Repo Fellow')
    server, site, token = os.environ['GIT_SERVER'], os.environ['GIT_SITE'], os.environ['GIT_TOKEN']
    db_user, db_password, db = os.environ['FELLOW_USER'] or "repo", os.environ['FELLOW_PASSWORD'] or "fellow", os.environ['FELLOW_DB'] or "repo_fellow"
    command = arguments["<command>"]
    injector = Injector(db_user = db_user, db_password = db_password,database = db)
    if arguments["project"]:
        if command == "list":
            for i in injector.get_projects():
                logging.info(i)
        if command == "import":
            data = Crawler.create_client(server,site,token).getProjects()
            injector.insert_data(Parser.parse_projects(data))
            print("[INFO] total imported projects {}".format(len(data)))
        if command == "remote":
            commits = Crawler.create_client(server,site,token).getAllProjectCommitsCount(arguments["<args>"])
            for i in commits:
                if i["ref"]:
                    print("{}:{}".format(i["name"],i["ref"]["target"]["history"]["totalCount"]))
                else:
                    print("[ERROR]: {} has none history record".format(i["name"]))

    if arguments["user"]:
        if command == "import":
            data = Crawler.create_client(server,site,token).get_users()
            injector.insert_data(Parser.parse_users(data))
            print("[INFO] total imported users {}".format(len(data)))

    if arguments["pr"]:
        if command == "import":
            project = arguments["<args>"]
            data = Crawler.create_client(server,site,token).get_pull_requests(project)
            injector.insert_data(Parser.parse_pulls(data))
            print("[INFO] total imported pulls {}".format(len(data)))

    if arguments["commit"]:
        if command == "update":
            injector = Injector(db_user = db_user, db_password = db_password,database = db)
            print("{}{}".format(db_user,db_password))
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
                Injector(db_user = db_user, db_password = db_password,database = db).insert_data(new_commits)
                
    if arguments["db"]:
        if command == "init":
            RepoMySQL().init_db(os.environ['DB_PASSWORD'])
