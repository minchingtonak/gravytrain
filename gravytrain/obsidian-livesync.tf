variable "OBSIDIAN_LIVESYNC_USER" {
  type = string
}

variable "OBSIDIAN_LIVESYNC_PASSWORD" {
  type = string
}

variable "OBSIDIAN_LIVESYNC_HOST" {
  type = string
}

variable "OBSIDIAN_LIVESYNC_TLS_EMAIL" {
  type = string
}

variable "OBSIDIAN_LIVESYNC_SUBPATH" {
  type = string
}

resource "docker_container" "couchdb" {
  name = "couchdb"
  image = "couchdb"
  depends_on = [ docker_container.caddy ]
  restart = "always"
  ports {
    internal = 5984
    external = 5984
    ip = "127.0.0.1"
  }
  volumes {
    host_path = "/home/akmin/workspace/gravytrain/deployments/obsidian-livesync/data/couchdb"
    container_path = "/opt/couchdb/data"
  }
  volumes {
    host_path = "/home/akmin/workspace/gravytrain/deployments/obsidian-livesync/local.ini"
    container_path = "/opt/couchdb/etc/local.ini"
  }
  env = [
    "COUCHDB_USER=${var.OBSIDIAN_LIVESYNC_USER}",
    "COUCHDB_PASSWORD=${var.OBSIDIAN_LIVESYNC_PASSWORD}",
  ]
  networks_advanced {
    name = "caddy"
  }
  labels {
    label = "caddy"
    value = "https://${var.OBSIDIAN_LIVESYNC_HOST}:443"
  }
  labels {
    label = "caddy.0_log.level"
    value = "INFO"
  }
  labels {
    label = "caddy.0_log.output"
    value = "file /data/caddy.log"
  }
  labels {
    label = "caddy.0_log.output.0_roll_size"
    value = "10MB"
  }
  labels {
    label = "caddy.0_log.output.1_roll_keep"
    value = "10"
  }
  labels {
    label = "caddy.1_tls"
    value = "${var.OBSIDIAN_LIVESYNC_TLS_EMAIL}"
  }
  labels {
    label = "caddy.2_redir"
    value = "${var.OBSIDIAN_LIVESYNC_SUBPATH} ${var.OBSIDIAN_LIVESYNC_SUBPATH}/ permanent"
  }
  labels {
    label = "caddy.3_handle_path"
    value = "${var.OBSIDIAN_LIVESYNC_SUBPATH}/*"
  }
  labels {
    label = "caddy.3_handle_path.reverse_proxy"
    value = "couchdb:5984"
  }
  labels {
    label = "caddy.4_handle.respond"
    value = "AccessDenied 403"
  }
  labels {
    label = "caddy.4_handle.respond.close"
    value = "{{\"\"}}"
  }
}

