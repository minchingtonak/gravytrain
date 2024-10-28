variable "N8N_AUTH_USER" {
  type = string
}

variable "N8N_AUTH_PASSWORD" {
  type = string
}

variable "N8N_DOMAIN" {
  type = string
}

variable "N8N_SUBPATH" {
  type = string
}

variable "N8N_CRON_TIMEZONE" {
  type = string
}

variable "N8N_TLS_EMAIL" {
  type = string
}

resource "docker_container" "n8n" {
  name = "n8n"
  image = "n8nio/n8n:0.222.1"
  depends_on = [ docker_container.caddy ]
  restart = "always"
  ports {
    internal = 9898
    external = 9898
    ip = "127.0.0.1"
  }
  volumes {
    host_path = "/home/akmin/workspace/gravytrain/deployments/n8n/data/local_files"
    container_path = "/files"
  }
  volumes {
    host_path = "/home/akmin/workspace/gravytrain/deployments/n8n/data/.n8n"
    container_path = "/home/node/.n8n"
  }
  env = [
    "N8N_BASIC_AUTH_ACTIVE=true",
    "N8N_BASIC_AUTH_USER=${var.N8N_AUTH_USER}",
    "N8N_BASIC_AUTH_PASSWORD=${var.N8N_AUTH_PASSWORD}",
    "N8N_HOST=${var.N8N_DOMAIN}",
    "N8N_PATH=${var.N8N_SUBPATH}/",
    "N8N_PORT=9898",
    "N8N_PROTOCOL=https",
    "NODE_ENV=production",
    "WEBHOOK_URL=https://${var.N8N_DOMAIN}${var.N8N_SUBPATH}/",
    "GENERIC_TIMEZONE=${var.N8N_CRON_TIMEZONE}",
    "EXECUTIONS_DATA_SAVE_ON_ERROR=all",
    "EXECUTIONS_DATA_SAVE_ON_SUCCESS=none",
    "EXECUTIONS_DATA_PRUNE=true",
    "EXECUTIONS_DATA_MAX_AGE=336",
    "EXECUTIONS_DATA_PRUNE_MAX_COUNT=50000",
  ]
  networks_advanced {
    name = "caddy"
  }
  labels {
    label = "caddy"
    value = "https://${var.N8N_DOMAIN}:443"
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
    value = "${var.N8N_TLS_EMAIL}"
  }
  labels {
    label = "caddy.2_redir"
    value = "${var.N8N_SUBPATH} ${var.N8N_SUBPATH}/ permanent"
  }
  labels {
    label = "caddy.3_handle_path"
    value = "${var.N8N_SUBPATH}/*"
  }
  labels {
    label = "caddy.3_handle_path.reverse_proxy"
    value = "n8n:9898"
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

