import yaml
import sys
import os
import re
import json
import glob
from typing import Any, Dict, List, Match, Tuple, Union

def stringify(value: Any) -> str:
    return str(value).lower() if isinstance(value, bool) else str(value)

def find_env_vars(value: Any) -> Union[Match[str], None]:
    return re.findall(r'(\$\{([a-zA-Z0-9_-]+)\})', stringify(value))

def prefix_env_vars(value: Any) -> Union[Match[str], None]:
    copy = stringify(value)
    matches = find_env_vars(copy)
    for with_braces, var_name in matches:
        copy = copy.replace(with_braces, f"${{var.{var_name}}}")
    return copy

def convert_networks_to_hcl(networks: Dict[str, Dict[str, Any]]) -> str:
    hcl = ""
    for network_name, network_config in map(lambda name: (name[0], {} if not name[1] else name[1]), networks.items()):
        # don't include external networks since they are assumed to already exist
        if "external" in network_config and network_config["external"] == True:
            continue

        hcl += f'resource "docker_network" "{network_name}" {{\n'
        hcl += f'  name = "{network_name}"\n'

        if "driver" in network_config:
            hcl += f'  driver = "{network_config["driver"]}"\n'

        if "internal" in network_config:
            hcl += f'  internal = {"true" if network_config["internal"] else "false"}\n'

        if "ipv6" in network_config:
            hcl += f'  ipv6 = {"true" if network_config["ipv6"] else "false"}\n'

        if "attachable" in network_config:
            hcl += f'  attachable = {"true" if network_config["attachable"] else "false"}\n'

        if "options" in network_config:
            hcl += '  options = {\n'
            for opt_key, opt_value in network_config["options"].items():
                hcl += f'    "{opt_key}" = "{opt_value}"\n'
            hcl += '  }\n'

        if "ipam" in network_config:
            ipam = network_config["ipam"]
            if "driver" in ipam:
                hcl += f'  ipam_driver = "{ipam["driver"]}"\n'

            if "config" in ipam:
                for config in ipam["config"]:
                    hcl += '  ipam_config {\n'
                    for key, value in config.items():
                        hcl += f'    {key} = "{value}"\n'
                    hcl += '  }\n'

        hcl += '}\n\n'
    return hcl

def convert_to_hcl(package_name: str, service_name: str, service_config: Dict[str, Any]) -> str:
    hcl = f'resource "docker_container" "{service_name}" {{\n'
    hcl += f'  name = "{service_name}"\n'
    hcl += f'  image = "{service_config["image"]}"\n'
    if service_name != "caddy":
        hcl += "  depends_on = [ docker_container.caddy ]\n"

    if "restart" in service_config:
        hcl += f'  restart = "{service_config["restart"]}"\n'

    if "ports" in service_config:
        for port in service_config["ports"]:
            parts = port.split(':')
            if len(parts) == 2:
                hcl += f'  ports {{\n    internal = {parts[1]}\n    external = {parts[0]}\n  }}\n'
            else:
                hcl += f'  ports {{\n    internal = {parts[2]}\n    external = {parts[1]}\n    ip = "{parts[0]}"\n  }}\n'

    if "volumes" in service_config:
        for volume in service_config["volumes"]:
            parts = volume.split(":")
            is_path = "/" in parts[0] or "." in parts[0]
            hcl += f'  volumes {{\n    {"host_path" if is_path else "volume_name"} = "{os.path.abspath(os.path.join("deployments", package_name, parts[0])) if is_path else parts[0]}"\n    container_path = "{os.path.abspath(parts[1])}"\n'
            if len(parts) == 3:
                hcl += f'    read_only = {"true" if parts[2] == "ro" else "false"}\n'
            hcl += "  }\n"

    if "environment" in service_config:
        hcl += "  env = [\n"
        for env_var, env_value in service_config["environment"].items():
            hcl += f'    "{env_var}={prefix_env_vars(env_value)}",\n'
        hcl += "  ]\n"

    if "networks" in service_config:
        for network in service_config["networks"]:
            hcl += f'  networks_advanced {{\n    name = "{network}"\n  }}\n'

    if "labels" in service_config:
        for name, value in service_config['labels'].items():
            hcl += f'  labels {{\n    label = "{name}"\n    value = "{prefix_env_vars(value)}"\n  }}\n'

    hcl += '}\n\n'
    return hcl

def convert_compose_file(input_file):
    if not os.path.isfile(input_file):
        print(f"File {input_file} not found")
        sys.exit(1)

    with open(input_file, "r") as file:
        docker_compose = yaml.safe_load(file)

    folder_name_match = re.match(r'.*deployments/(.*)/docker-compose\..+', input_file)
    package_name = folder_name_match.group(1)
    output_file = f'{package_name}.tf'

    should_deploy = docker_compose.get("deploy", True)
    if not should_deploy:
        if os.path.isfile(output_file):
            os.remove(output_file)
        print(f"Skipped compose file with deploy=false: {input_file}")
        return {}

    services = docker_compose.get("services", {})
    networks = docker_compose.get("networks", {})

    hcl_output = ""

    dangling_env_vars = {}
    for service_name, service_config in services.items():
        for key in ['environment', 'labels']:
            if key in service_config:
                for env_value in service_config[key].values():
                    matches = find_env_vars(env_value)
                    if matches:
                        for _, var_name in matches:
                            if var_name not in dangling_env_vars:
                                hcl_output += f'variable "{var_name}" {{\n  type = string\n}}\n\n'
                            dangling_env_vars[var_name] = "FIXME"

    hcl_output += convert_networks_to_hcl(networks)

    for service_name, service_config in services.items():
        hcl_output += convert_to_hcl(package_name, service_name, service_config)

    with open(output_file, "w") as file:
        file.write(hcl_output)

    print(f"Successfully converted {input_file} to {output_file}")
    return dangling_env_vars

def get_compose_files():
    if not os.path.exists('./deployments'):
        print('deployments directory not found')
        sys.exit(1)

    extensions = ['yml', 'yaml']
    return [file for ext in extensions for file in glob.glob(f'./deployments/*/docker-compose.{ext}')]

def main():
    files = get_compose_files()

    dangling_env_vars = {}
    for compose_file in files:
        file_dangling_vars = convert_compose_file(compose_file)
        dangling_env_vars.update(file_dangling_vars)

    # don't nuke previous env var values when regenerating
    if os.path.isfile('terraform.tfvars.json'):
        with open('terraform.tfvars.json', 'r') as file:
            content = json.load(file)
            for env_var in content.keys():
                if env_var in dangling_env_vars:
                    dangling_env_vars[env_var] = content[env_var]

    with open("terraform.tfvars.json", "w") as file:
        json.dump(dangling_env_vars, file, indent=4)

    print("Wrote terraform.tfvars.json")

if __name__ == "__main__":
    main()
