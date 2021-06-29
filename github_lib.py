import requests
import yaml
from yaml.loader import SafeLoader

def list_repository_collaborators(user, token, org, repo, affiliation='all'):
    #doc: https://docs.github.com/en/rest/reference/repos#list-repository-collaborators
    query_url = f"https://api.github.com/repos/{org}/{repo}/collaborators"

    headers = {
        'accept': 'application/vnd.github.v3+json'
    }
    
    per_page = 100
    response_len = per_page
    return_var = list()

    page = 0
    response_len = per_page
    while response_len == per_page:
        page += 1
        response = requests.get(
            query_url,
            headers=headers,
            params={
                'per_page': per_page,
                'page': page,
                'affiliation': affiliation
            },
            auth=(user, token)
        )
        
        print(response.status_code)
        
        if response.status_code == 404:
            raise Exception(response)
        
        response_json = response.json()
        return_var += response_json
        response_len = len(response_json)
    
    return return_var


def put_permission(user, token, org, repo, target_user, new_permission):
    #doc: https://docs.github.com/en/rest/reference/repos#add-a-repository-collaborator
    query_url = f"https://api.github.com/repos/{org}/{repo}/collaborators/{target_user}"
    headers = { 'accept': 'application/vnd.github.v3+json' }
    data = { 'permission': new_permission }

    response = requests.put(
        query_url,
        headers=headers,
        json=data,
        auth=(user, token)
    )
    
    return response


def get_dryrun_status(file):
    with open(file) as f:
        config = yaml.load(f, Loader=SafeLoader)
        return config["dryrun"]



def invite_collaborator(user, token, org, repo, target_user, new_permission):
    #doc: https://docs.github.com/en/rest/reference/repos#add-a-repository-collaborator
    put_permission(user, token, org, repo, target_user, new_permission)
    
    
def remove_collaborator(user, token, org, repo, target_user):
    query_url = f"https://api.github.com/repos/{org}/{repo}/collaborators/{target_user}"
    headers = { 'accept': 'application/vnd.github.v3+json' }

    response = requests.delete(
        query_url,
        headers=headers,
        auth=(user, token)
    )
    
    return response
    

def get_userrights_from_repogroup(repogroup, usergroups):
    # just the order of strenght, higher index = higher priority ~ overwrites lower rank if user has two or more
    ranks = ["pull", "push", "admin"]
    userpermission = {}
    
    for config_usergroup in usergroups:
        usergroup = list(config_usergroup.keys())[0]
        users = list(config_usergroup.values())[0]
        for assigned_usergroup in repogroup["assigned-user-groups"]:
            assigned_usergroup_name = list(assigned_usergroup.keys())[0]
            assigned_usergroup_permission = list(assigned_usergroup.values())[0]
            if usergroup == assigned_usergroup_name:

                for user in users:
                    if user not in userpermission:
                        userpermission[user] = assigned_usergroup_permission
                    else:
                        if ranks.index(userpermission[user]) < ranks.index(assigned_usergroup_permission):
                            userpermission[user] = assigned_usergroup_permission
    return userpermission


def list_config_repo_permissions(file):
    with open(file) as f:
      config = yaml.load(f, Loader=SafeLoader)
      repogroups_permissions = []
      repo_permissions = {}

      for repogroup in config["repository-groups"]:
        repogroup_name = repogroup["repository-group"]
        repogroup_permissions = get_userrights_from_repogroup(repogroup, config["user-groups"])

        repogroups_permissions += [{
          "name": repogroup_name,
          "permissions": repogroup_permissions
        }]

        for repo in repogroup["repositories"]:
          for user, permission in repogroup_permissions.items():

            ranks = ["pull", "push", "admin"]
            if repo not in repo_permissions:
              repo_permissions[repo] = {}
            if user not in repo_permissions[repo]:
              repo_permissions[repo][user] = permission
            if ranks.index(repo_permissions[repo][user]) < ranks.index(permission):
              repo_permissions[repo][user] = permission
            
    return repo_permissions
