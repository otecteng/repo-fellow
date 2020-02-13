from repofellow.injector import Project,Commit,CommitFile,Event,Developer

class Parser:
    @staticmethod
    def parse_commits(data,format="github", project = None):
        if format == "gitee":
            return list(map(lambda x:Commit.from_gitee(x),data))
        elif format == "gitlab":
            return list(map(lambda x:Commit.from_gitlab(x,project = project),data))
        else:
            return list(map(lambda x:Commit.from_github(x,project = project),data))

    @staticmethod
    def parse_events(data,format="github"):
        if format == "gitee":
            return list(map(lambda x:Event.from_gitee(x),data))
        elif format == "gitlab":
            return list(map(lambda x:Event.from_gitlab(x),data))
        else:
            return list(map(lambda x:Event.from_github(x),data))

    @staticmethod
    def parse_projects(data,format="github"):
        if format == "gitee":
            return list(map(lambda x:Project.from_gitee(x),data))
        elif format == "gitlab":
            return list(map(lambda x:Project.from_gitlab(x),data))
        else:
            return list(map(lambda x:Project.from_github(x),data))

    @staticmethod
    def parse_users(data,format="github"):
        if format == "gitee":
            return list(map(lambda x:Developer.from_gitee(x),data))
        elif format == "gitlab":
            return list(map(lambda x:Developer.from_gitlab(x),data))
        else:
            return list(map(lambda x:Developer.from_github(x),data))

