# Spark-Flow — Local Development Environment

![License](https://img.shields.io/badge/License-MIT-green) ![Python](https://img.shields.io/badge/python-3.12.9-blue)

This repository provides a local development stack for Spark-based workflows: Airflow, Spark (UI, History), MinIO, GitLab, and Jupyter. The stack is containerized and managed with Docker Compose.

## Prerequisites

- Docker & Docker Compose (compatible with your Docker Engine)
- Recommended: WSL2 / Git Bash / bash-compatible shell on Windows
- Python 3.12.9 (for local tooling)
- PySpark 3.5.7
- Airflow 2.10.5
- Jupyter (for notebook work)

Default ports used:
- Airflow: 8083
- Jupyter: 8888
- Spark UI: 8880
- Spark History: 18080
- GitLab: 9084
- MinIO: 9991

## Quick start

1) (Optional) Save local Docker images
- Bash:
```bash
mkdir -p ./docker_image
for img in $(docker images --format "{{.Repository}}:{{.Tag}} {{.Size}}" | grep '^my-' | sort -k2 -h | awk '{print $1}'); do
  docker save "$img" | gzip > "./docker_image/${img//[:\/]/_}.tar.gz"
done
```
- PowerShell:
```powershell
New-Item -ItemType Directory -Force -Path docker_image
docker images --format "{{.Repository}}:{{.Tag}} {{.Size}}" | Select-String '^my-' | ForEach-Object {
  $img = ($_ -split '\s+')[0]
  docker save $img | gzip > ("docker_image/" + ($img -replace '[:/]', '_') + ".tar.gz")
}
```

2) Load saved images (if any)
- Bash:
```bash
for f in docker_image/*.tar.gz; do gunzip -c "$f" | docker load; done
```
- PowerShell:
```powershell
Get-ChildItem docker_image\*.tar.gz | ForEach-Object {
  & gzip -dc $_.FullName | docker load
}
```

3) Start services
```bash
cd services
docker compose up -d
```

4) Verify services / access UIs

- Airflow: http://localhost:8083  
  - Default: username `airflow` / password `airflow123`

- GitLab: http://localhost:9084 or http://gitlab:9084  
  - Default admin: `root` / `G!tLbS#cret2025`  
  - If login fails, create/admin user inside the container:
  ```bash
  docker exec -it gitlab gitlab-rails runner 'user = Users::CreateService.new(nil, {username: "gitlab", name: "Administrator", email: "gitlab@example.com", password: "G!tLbS#cret2025", skip_confirmation: true}).execute; user.update(admin: true)'
  ```

- Jupyter: http://localhost:8888  
  - Check container logs for the access token or open the URL with the token provided by the container logs => Token: "dev".

- MinIO: http://localhost:9991  
  - Default: `minio` / `minio123`

- Spark UI: http://localhost:8880

- Spark History: http://localhost:18080


## Useful commands

- Stop stack:
```bash
cd services
docker compose down
```
- View logs:
```bash
cd services
docker compose logs -f
```
- Rebuild a service:
```bash
docker compose build <service-name> && docker compose up -d <service-name>
```

## SSH port forwarding (optional)
Forward container ports from a remote host to local machine:
```bash
ssh -L 8899:localhost:8888 -L 8083:localhost:8083 -L 8880:localhost:8880 -L 18080:localhost:18080 -L 9084:localhost:9084 -L 9991:localhost:9991 root@<remote-host>
```

## Troubleshooting

- If a service fails to start, check `docker compose logs -f <service>` for details.
- On Windows, use WSL2 or Git Bash for Bash scripts. PowerShell snippets are provided above.
- If ports are already in use, stop conflicting services or change port mappings in `services/docker-compose.yml`.

## Security & customization

- Change default passwords before exposing services to a network.
- Configure persistent volumes and secrets in `services/docker-compose.yml` and `.env` files as needed.

If you need further adjustments (port changes, additional services, or CI integration instructions), specify requirements and environment details.