resource "hcloud_firewall" "windhelm-firewall" {
  name = "windhelm-firewall"
  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "22"
    source_ips = [
      "0.0.0.0/0",
      "::/0"
    ]
  }
  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "80"
    source_ips = [
      "0.0.0.0/0",
      "::/0"
    ]
  }
  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "443"
    source_ips = [
      "0.0.0.0/0",
      "::/0"
    ]
  }
}

# resource "hcloud_ssh_key" "windhelm-ssh-key" {
#   name       = "windhelm-ssh-key"
#   public_key = file("~/.ssh/hetzner_ed25519.pub")
# }

resource "hcloud_server" "windhelm" {
  name         = "windhelm"
  location     = "hil"
  server_type  = "cpx11"
  image        = "docker-ce"
  firewall_ids = [hcloud_firewall.windhelm-firewall.id]
  ssh_keys     = ["hetzner-WITCH"]
}
