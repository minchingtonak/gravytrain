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
- can use cli to test things locally before deploying:
    - deploy/destroy the server infra
    - deploy/destroy all or a subset of stacks locally
    - deploy/destroy all or a subset of stacks to the deployed server (see if there's a way to read a tf output var from the server resource for this)
<!-- - can commit the output folder for each deployment after testing -->
<!-- - can deploy the infra using semaphore -->
- can use ansible to set up server (possibly via semaphore)
- can use ansible to deploy host via gravytrain
<!-- - can deploy the stacks to the server using semaphore -->


pros of cloning entire repo for deployment
- local dev experience mirrors deployment experience (same commands, same files)
- can generate only the required deployment on the server itself

cons of cloning
- need to install deps on remote before deploy (bun, then `bun install`)
    - can fix with a script or something like `gravy init` after cloning
- more files than necessary are cloned onto the server

pros of copying over deployment folder
- can just copy deployment-related files over and nothing else

cons of copying
- need to make sure that the volume paths for stacks that are generated locally match the deployment path (bad)
    - can fix by copying over hosts, stacks, and scripts, then generating the single deployment
    - then, still need to install deps (`gravy init`)

pros of copying over hosts, stacks, and scripts, then generating the single deployment
- no need to have to worry about volume paths
- no need to clone the entire repo

cons of ^
- requires init step to install deps (gravy init) (and actually ansible should install bun & python, gravy init should just run bun install)


need to see if i can set up tf state file storage in a minio container in the semaphore stack
