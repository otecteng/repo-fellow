Repo data collector and inspector

1.install dependency  

2.setting env  
export GIT_SITE = "https://xxx"  

export GIT_TOKEN = "xxx"  

export GIT_SERVER = "github"  

3.execute crawl projects  
python3 main.py project list

base on gitlab data (simple), mapping github data to gitlab 

events:
    gitlab = target + action 
    github = type + action
gitlab target list:issue,milestone,merge_request,note,project,snippet,user
gitlab action list:created,updated,closed,reopened,pushed,commented,merged,joined,left,destroyed,expired

github type list:CheckRunEvent,CheckSuiteEvent,CommitCommentEvent,ContentReferenceEvent,CreateEvent,DeleteEvent,DeployKeyEvent,DeploymentEvent,DeploymentStatusEvent,DownloadEvent,FollowEvent,ForkEvent,ForkApplyEvent,GitHubAppAuthorizationEvent,GistEvent,GollumEvent,InstallationEvent,InstallationRepositoriesEvent,IssueCommentEvent,IssuesEvent,LabelEvent,MarketplacePurchaseEvent,MemberEvent,MembershipEvent,MetaEvent,MilestoneEvent,OrganizationEvent,OrgBlockEvent,PackageEvent,PageBuildEvent,ProjectCardEvent,ProjectColumnEvent,ProjectEvent,PublicEvent,PullRequestEvent,PullRequestReviewEvent,PullRequestReviewCommentEvent,PushEvent,ReleaseEvent,RepositoryDispatchEvent,RepositoryEvent,RepositoryImportEvent,RepositoryVulnerabilityAlertEvent,SecurityAdvisoryEvent,SponsorshipEvent,StarEvent,StatusEvent,TeamEvent,TeamAddEvent,WatchEvent
github action:...

