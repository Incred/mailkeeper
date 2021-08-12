# mailkeeper
  Django (+ python scripts integrated to postfix MTA) application which allows to track inbound and outbound emails,
store them in database, process inbound email.
It handles receiving, processing and parsing inbound email then POST it to
applicationserver using webhook.

## Deploy

- Use ansible playbook to deploy the app (in ansible directory)
- create *group_vars/all* local variables file (replacing paths with your own):
```
    project_name: "mailkeeper"
    local_project_path: "/home/user123/project/mailkeeper/"
    local_tmp_path: "/tmp/"
```
- create dev environment (if needed) directory with inventory file:
```
 *environments/dev/*
 *environments/dev/hosts.yml* - inventory file
 *environments/dev/group_vars/all_servers* - env variables
```

- to upload the project to server (host srv2 in the example) run:
`ansible-playbook push-code.yml -K --user <username>`
