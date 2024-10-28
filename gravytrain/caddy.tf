resource "docker_container" "caddy" {
  name = "caddy"
  image = "lucaslorentz/caddy-docker-proxy:ci-alpine"
  restart = "unless-stopped"
  ports {
    internal = 80
    external = 80
  }
  ports {
    internal = 443
    external = 443
  }
  volumes {
    host_path = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }
  volumes {
    host_path = "/home/akmin/workspace/gravytrain/deployments/caddy/data/config"
    container_path = "/config"
  }
  volumes {
    host_path = "/home/akmin/workspace/gravytrain/deployments/caddy/data/data"
    container_path = "/data"
  }
  volumes {
    host_path = "/home/akmin/workspace/gravytrain/deployments/caddy/caddy.logrotate"
    container_path = "/etc/logrotate.d/caddy"
    read_only = true
  }
  env = [
    "CADDY_INGRESS_NETWORKS=caddy",
  ]
  networks_advanced {
    name = "caddy"
  }
}

