import json
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class Project(Base):
    __tablename__ = 'project'
    path = Column(String(64),primary_key=True)
    owner = Column(String(64))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self,data):
        self.path = data["path_with_namespace"]
        self.created_at = datetime.datetime.strptime(data["created_at"][:19], "%Y-%m-%dT%H:%M:%S")
        self.updated_at = datetime.datetime.strptime(data["last_activity_at"][:19], "%Y-%m-%dT%H:%M:%S")
        self.owner = data["owner"]["username"]

    def __str__(self):
        return "{}\t{}\t{}".format(self.path,self.created_at,self.updated_at)

    @staticmethod
    def from_github(data):
        # data["commit"]["author"]["date"] = datetime.datetime.strptime(data["commit"]["author"]["date"][:19], "%Y-%m-%dT%H:%M:%S")
        data["path_with_namespace"] = data["full_name"]
        data["last_activity_at"] = data["updated_at"]
        data["owner"]["username"] = data["owner"]["login"]
        return Project(data)

    @staticmethod
    def from_gitlab(data):
        if not "owner" in data:
            print("[INFO]:empty owner {}".format(data["path_with_namespace"]))
            data["owner"] = {"username":""}
        return Project(data)

class CommitFile(Base):
    __tablename__ = 'commit_file'
    iid = Column(Integer, primary_key=True)
    commit_iid = Column(Integer)
    commit_id = Column(String(64))
    id = Column(String(64))
    filename = Column(String(128))
    status = Column(String(64))
    additions = Column(Integer)
    deletions = Column(Integer)
    changes = Column(Integer)
    def __init__(self,data):
        self.path = data["path_with_namespace"]
        self.created_at = datetime.datetime.strptime(data["created_at"][:19], "%Y-%m-%dT%H:%M:%S")
        self.updated_at = datetime.datetime.strptime(data["last_activity_at"][:19], "%Y-%m-%dT%H:%M:%S")
        self.owner = data["owner"]["username"]

class Commit(Base):
    __tablename__ = 'commit'
    iid = Column(Integer, primary_key=True)
    id = Column(String(64))
    project = Column(String(128))
    author_name = Column(String(64))
    author_email = Column(String(64))
    message = Column(String(1024))
    created_at = Column(DateTime)
    additions = Column(Integer)
    deletions = Column(Integer)
    total = Column(Integer)
    issue = Column(String(64))

    def __init__(self,data):
        self.id = data["id"]
        self.message = data["message"].rstrip()
        self.author_name = data["author_name"]
        self.author_email = data["author_email"]
        self.created_at = data["authored_date"]
    
    @staticmethod
    def find_issue(message):
        if message is None:
            return None
        issue = None
        start = message.find('#')
        if  start  < 1 :
            return None
        issue = message[start + 1:]
        pos = issue.find(' ')
        if pos > 1 :
            issue = issue[0:pos]
        pos = issue.find(':')
        if pos > 1 :
            issue = issue[0:pos]
        pos = issue.find('：')
        if pos > 1 :
            issue = issue[0:pos]
        return issue

    def __str__(self):
        return "{}[{}]:{}".format(self.created_at,self.author_email,self.message)

    @staticmethod
    def from_gitee(data):
        # sample: date: 2019-11-24T23:22:06.000+08:00
        data["commit"]["author"]["date"] = datetime.datetime.strptime(data["commit"]["author"]["date"][:19], "%Y-%m-%dT%H:%M:%S")
        author = data["commit"]["author"]
        content = {"author_name":author["name"],"author_email":author["email"],"authored_date":author["date"],"message":data["commit"]["message"]}
        return Commit(content)

    @staticmethod
    def from_gitlab(data):
        # sample: authored_date: 2019-11-24T23:22:06.000+08:00
        data["authored_date"] = datetime.datetime.strptime(data["authored_date"][:19], "%Y-%m-%dT%H:%M:%S")
        return Commit(data)

    @staticmethod
    def from_github(data):
        # sample: "date":"2020-01-10T09:20:07Z"
        data["commit"]["author"]["date"] = datetime.datetime.strptime(data["commit"]["author"]["date"][:19], "%Y-%m-%dT%H:%M:%S")
        author = data["commit"]["author"]
        content = {"id":data["sha"],"author_name":author["name"],"author_email":author["email"],"authored_date":author["date"],"message":data["commit"]["message"][:1000]}
        return Commit(content)

    @staticmethod
    def append_count_github(commit,data):
        commit.additions = data["stats"]["additions"]
        commit.deletions = data["stats"]["deletions"]
        commit.total = data["stats"]["total"]
        return commit

class Event:
    def __init__(self,data):
        self.type = data["action_name"]
        self.author = data["author"]["username"]
        self.project = data["project_id"]
        self.created_at = data["created_at"]
        
    def __str__(self):
        return "{}[{}]:{}({})".format(self.created_at,self.author,self.project,self.type)

    @staticmethod
    def from_github(data):
        data["action_name"] = data["type"]
        if data["type"] == "PushEvent":
            data["action_name"] = "pushed to"
        if data["type"] == "PullRequestEvent":
            data["action_name"] = data["payload"]["action"]

        data["author"]={"username":data["actor"]["login"]}
        data["project_id"] = data["repo"]["name"]
        data["created_at"] = datetime.datetime.strptime(data["created_at"][:19], "%Y-%m-%dT%H:%M:%S")
        return Event(data)

    @staticmethod
    def from_gitlab(data):
        data["created_at"] = datetime.datetime.strptime(data["created_at"][:19], "%Y-%m-%dT%H:%M:%S")
        return Event(data)

class Injector:
    def __init__(self,user = "root", password = "", host = "localhost", database = "repo"):
        self.engine = create_engine("mysql+pymysql://{}:{}@{}:3306/{}?charset=utf8mb4".format(user,password,host,database))
        DBSession = sessionmaker(bind = self.engine)
        self.db_session = DBSession()
    
    def insert_data(self,data):
        for i in data:
            self.db_session.add(i)
        self.db_session.commit()
    
    def get_projcets(self,start_from = None):
        if start_from:
            return self.db_session.query(Project).filter(Project.path >= start_from)
        else:
            return self.db_session.query(Project)

    def get_commits(self,start_from = None):
        if start_from:
            return self.db_session.query(Commit).filter(Commit.iid >= start_from)
        else:
            return self.db_session.query(Commit)

    def db_commit(self):
        self.db_session.commit()
