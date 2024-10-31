import sys
import os
import re
from typing import Any, Dict, List, Match, TextIO, Union
import yaml

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

def convert_to_hcl(output_folder_path: str, service_name: str, service_config: Dict[str, Any]) -> str:
    hcl = f'resource "docker_container" "{service_name}" {{\n'
    hcl += f'  name = "{service_name}"\n'
    hcl += f'  image = "{service_config["image"]}"\n'

    if "command" in service_config:
        hcl += f'  command = ["{service_config["command"]}"]\n'

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
            hcl += f'  volumes {{\n    {"host_path" if is_path else "volume_name"} = "{os.path.abspath(os.path.join(output_folder_path, parts[0])) if is_path else parts[0]}"\n    container_path = "{os.path.abspath(parts[1])}"\n'
            if len(parts) == 3:
                hcl += f'    read_only = {"true" if parts[2] == "ro" else "false"}\n'
            hcl += "  }\n"

    if "environment" in service_config:
        hcl += "  env = [\n"
        for env_var, env_value in map(lambda v: v.split('='), service_config["environment"]) if isinstance(service_config["environment"], list) else service_config["environment"].items():
            hcl += f'    "{env_var}={prefix_env_vars(env_value)}",\n'
        hcl += "  ]\n"

    if "networks" in service_config:
        for network in service_config["networks"]:
            hcl += f'  networks_advanced {{\n    name = "{network}"\n  }}\n'

    if "network_mode" in service_config:
        hcl += f'  network_mode = "{service_config["network_mode"]}"\n'

    if "labels" in service_config:
        for name, value in map(lambda v: v.split('='), service_config["labels"]) if isinstance(service_config["labels"], list) else service_config["labels"].items():
            hcl += f'  labels {{\n    label = "{name}"\n    value = "{prefix_env_vars(value)}"\n  }}\n'

    hcl += '}\n\n'
    return hcl

def convert_compose_file(docker_compose: Any, output_folder_path: str):
    services = docker_compose.get("services", {})
    networks = docker_compose.get("networks", {})

    hcl_output = ""

    dangling_env_vars = {}
    for service_name, service_config in services.items():
        for key in ['environment', 'labels', 'volumes']:
            if key in service_config:
                env_values =  service_config[key] if isinstance(service_config[key], list) else service_config[key].values()
                for env_value in env_values:
                    matches = find_env_vars(env_value)
                    if matches:
                        for _, var_name in matches:
                            if var_name not in dangling_env_vars:
                                hcl_output += f'variable "{var_name}" {{\n  type = string\n}}\n\n'
                            dangling_env_vars[var_name] = "FIXME"

    hcl_output += convert_networks_to_hcl(networks)

    for service_name, service_config in services.items():
        hcl_output += convert_to_hcl(output_folder_path, service_name, service_config)

    return hcl_output

def main(argv: List[str], stdin: TextIO, stdout: TextIO):
    if len(argv) != 2:
        print('usage: python translate.py OUTPUT_DIR < COMPOSE_FILE_PATH > TF_FILE_PATH')
        sys.exit(1)

    output_folder_path = argv[1]

    # read compose file content from stdin
    compose_file = yaml.safe_load(stdin.read())

    tf_code = convert_compose_file(compose_file, output_folder_path)

    stdout.write(tf_code)

if __name__ == "__main__":
    # print to stderr by default, reserve stdout specifically for program output
    original_stdout = sys.stdout
    sys.stdout = sys.stderr
    main(sys.argv, sys.stdin, original_stdout)
