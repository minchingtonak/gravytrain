
# gravytrain

You bring the compose file. The rest is gravy.

---

## About

gravytrain is a simple way to manage the deployment of multiple dockerized applications on a single host.

## Usage

First, install Terraform

```bash
$ ./install.sh
```

Initialize Terraform

```bash
$ terraform init
```

Then, add compose files in subfolders under `deployments/`

When satisfied with your configuration, generate the Terraform files

```bash
$ ./generate.sh
```

If you're using any environment variables in your compose files, `terraform.tfvars.json` will be automatically created in the project root. This JSON file is where you can supply values for environment variables that your infrastructure can use for deployment/operation. Make sure to supply values for all variables (variables default value is `"FIXME"`).

When you're ready to deploy, run the deploy script and verify that the resources being deployed match your expectations

```bash
$ ./deploy.sh
```
