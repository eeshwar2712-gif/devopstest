# Stage 4: Infrastructure as Code. Terraform creates the same stack locally via Docker,
# so you learn plan/apply/destroy and state without needing a cloud account.
# Prereq: `docker build -t devops-app:local ./app` first.
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  # On Windows with Docker Desktop, uncomment:
  # host = "npipe:////.//pipe//docker_engine"
}

variable "app_port" {
  type    = number
  default = 5001
}

resource "docker_network" "app" {
  name = "devops-net"
}

resource "docker_image" "redis" {
  name         = "redis:7-alpine"
  keep_locally = true # don't delete the image on destroy (Compose also uses it)
}

resource "docker_container" "redis" {
  name  = "tf-redis"
  image = docker_image.redis.image_id
  networks_advanced {
    name    = docker_network.app.name
    aliases = ["redis"]
  }
}

resource "docker_container" "web" {
  name  = "tf-web"
  image = "devops-app:local"
  env   = ["REDIS_HOST=redis", "APP_VERSION=terraform"]
  ports {
    internal = 5000
    external = var.app_port
  }
  networks_advanced {
    name = docker_network.app.name
  }
  depends_on = [docker_container.redis]
}

output "url" {
  value = "http://localhost:${var.app_port}"
}
