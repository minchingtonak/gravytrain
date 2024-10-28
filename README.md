system to associate a stack or stacks to a specific host, with the host defined by tf code for a vps
- could have script out put be structured like:
```
output/ # output is organized into deployments
    global.tf # contains shared infra (ssh keys) (TODO see if this is necessary)
    |-windhelm/
        |-server.tf # contains the resources to deploy a vps behind a firewall
        |-terraform.tfvars.json # can deploy locally using env file, either for testing or as a same-system deployment
        |-stacks/ # contains all stacks associated with this host
            |-windmill.tf
            |-traefik.tf
    |-riften/
        |-server.tf
        |-terraform.tfvars.json
        |-stacks/
            |-obsidian.tf
            |-traefik.tf # can include a stack in multiple hosts, useful for common containers (traefik, watchtower, etc)
```

the big idea

- can create a new host by adding tf code for the infra for it (vps, firewall)
- can create a new stack by adding compose file for containers
- can associate stacks with hosts somehow (better to mark the stack or the host?)
- can run a script to generate tf code for stacks, copy server & stack code into deployment folders, merge env vars per-host
- can use cli to test things locally before deploying in semaphore:
    - deploy/destroy the server infra
    - deploy/destroy all or a subset of stacks locally
    - deploy/destroy all or a subset of stacks to the deployed server (see if there's a way to read a tf output var from the server resource for this)
- can commit the output folder for each deployment after testing
- can deploy the infra using semaphore
- can use ansible to set up server through semaphore
- can deploy the stacks to the server using semaphore



need to see if i can set up tf state file storage in a minio container in the semaphore stack
