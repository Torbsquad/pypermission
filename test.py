import os
import requests
import github_lib

import yaml
from yaml.loader import SafeLoader

#print(github_lib.put_permission("chris-robert", os.environ["TOKEN"], "volkswagen-onehub-services", "vwg.ngwsa.github-issues-test", "permissiondummy", "pull"))

is_dryrun = github_lib.get_dryrun_status('test_config.yml')
target_permissions = github_lib.list_config_repo_permissions('test_config.yml')

for repo, target_permission in target_permissions.items():
  print(f"repository: {repo}")
  print(f"target: {target_permission}")
  org = "volkswagen-onehub-services"
  collaborators = github_lib.list_repository_collaborators("chris-robert", os.environ["TOKEN"], org, repo, "outside")
  existing_users = {}
  print("collaborators: ↓")
  print(collaborators)
  print("collaborators: ↑")
  for coll in collaborators:
    print("coll:")
    print(coll)
    user = coll["login"]
    if coll["permissions"]["pull"]:
      existing_users[user] = "pull"
    if coll["permissions"]["push"]:
      existing_users[user] = "push"
    if coll["permissions"]["admin"]:
      existing_users[user] = "admin"
  print(f"current: {existing_users}")
  
  for target_user, permission in target_permission.items():
    if target_user not in existing_users:
      # invite user
      if is_dryrun:
        print(f"DRYRUN: '{target_user}' does not exist in '{repo}', script would have invited '{target_user}' with '{permission}'")
      else:
        print(f"user '{target_user}' does not exist in '{repo}' and gets an invitation with permission '{permission}'")
        github_lib.put_permission("chris-robert", os.environ["TOKEN"], org, repo, target_user, permission)
    else:
      if existing_users[target_user] != permission:
        # change permission of user
        if is_dryrun:
          print(f"DRYRUN: script would have changed permission of '{target_user}' to '{permission}'")
        else:
          print(f"changing permission of '{target_user}' to '{permission}'")
          github_lib.put_permission("chris-robert", os.environ["TOKEN"], org, repo, target_user, permission)
          
  for existing_user in existing_users.keys():
    if existing_user not in list(target_permission.keys()):
      print(f"DRYRUN: '{repo}' does not need '{existing_user}', script would have removed '{existing_user}'")
        
  '''
     elif existing_users not in target_user:
      # remove user
      if is_dryrun:
        print(f"DRYRUN: '{repo}' does not need '{target_user}', script would have removed '{target_user}'")
      else:
        print("remove script would now be run")
        #github_lib.put_permission("chris-robert", os.environ["TOKEN"], org, repo, target_user, permission)
  '''
  
# Ließ config
# Gehe durch jedes Repository:
#   Evaluiere Rechte für jeden Benutzer in der config __für das eine repository__ (wenn ein benutzer in mehreren usergruppen auftaucht, soll dieser die höchsten rechte haben, der gruppen)
#   Schnapp dir die liste der collaboratoren im repo
#   wenn user in liste fehlt
#      sende invite an fehlende user, initale rechte hinzügen
#   sonst wenn in config fehlt:
#      entferne users die keine rechte im repo mehr haben sollen
#   sonst:
#      ändere die rechte des users
