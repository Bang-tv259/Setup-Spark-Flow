# Spark-Flow — Local Development Environment

![License](https://img.shields.io/badge/License-MIT-green) ![Python](https://img.shields.io/badge/python-3.12.9-blue)

This repository provides a local development stack for Spark-based workflows: Airflow, Spark (UI, History), MinIO, GitLab, and Jupyter. The stack is containerized and managed with Docker Compose.

## Components

| Service | Description |
|---------|-------------|
| ![Airflow](https://img.shields.io/badge/Airflow-017CEE?logo=apacheairflow&logoColor=white) | Workflow orchestration |
| ![MinIO](https://img.shields.io/badge/MinIO-C72E49?logo=minio&logoColor=white) | S3-compatible object storage |
| ![Jupyter](https://img.shields.io/badge/Jupyter-F37626?logo=jupyter&logoColor=white) | Notebook environment |
| ![GitLab](https://img.shields.io/badge/GitLab-FC6D26?logo=gitlab&logoColor=white) or ![Gitea](https://img.shields.io/badge/Gitea-609926?logo=gitea&logoColor=white) | Git hosting & CI/CD |
| ![GitLab Runner](https://img.shields.io/badge/GitLab_Runner-FF8800?logo=gitlab&logoColor=white) or ![Gitea Runner](https://img.shields.io/badge/Gitea_Runner-609926?logo=gitea&logoColor=white) | CI/CD Runner |
| ![Redis UI](https://img.shields.io/badge/Redis_UI-DC382D?logo=redis&logoColor=white) | Redis Commander (Web UI for Redis) |
| ![Spark](https://img.shields.io/badge/Spark-E25A1C?logo=apachespark&logoColor=white) | Distributed compute |
| ![PySpark](https://img.shields.io/badge/PySpark-1A4A9E?logo=apache-spark&logoColor=white) | PySpark 3.5.7 for Spark operations |
| ![Spark UI](https://img.shields.io/badge/Spark%20UI-555555?logo=apachespark&logoColor=white) | Monitor Spark jobs |
| ![Spark History](https://img.shields.io/badge/Spark%20History%20Server-555555?logo=apachespark&logoColor=white) | View past job logs |
| ![DataHub](https://img.shields.io/badge/DataHub-0052CC?logo=datahub&logoColor=white) | Metadata platform for datasets and lineage |
| ![PostgreSQL](https://img.shields.io/badge/PostgreSQL_UI-336791?logo=postgresql&logoColor=white) | Database Web UI (pgweb – `sosedoff/pgweb:latest`) |

Default ports used:
- Airflow: 8083
- Jupyter: 8888
- Spark UI: 8880
- Spark History: 18080
- GitLab: 3000
- MinIO: 9991
- Redis UI: 18081
- DataHub: 9002 (Optional)
- Postgres UI: 9081

## Quick start

0) Build Docker images
Before building, review and adjust the Docker image configuration (e.g. `Dockerfile`, environment variables, configuration files) inside each service folder as needed.


Example build image:
```bash
# Gitea
docker build -f ./services/gitea/Dockerfile -t my-gitea:20251217_0900 ./services/gitea/
```

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

You can change `.env` file and `docker-compose` file if needed.
```bash
cd services
docker compose up -d
```

4) Verify services / access UIs

- Airflow: http://localhost:8083  
  - Default: username `airflow` / password `airflow123`

- GitLab: http://localhost:3000 or http://gitlab:3000  
  - Default admin: `root` / `G!tLbS#cret2025`  
  - If login fails, create/admin user inside the container:
  ```bash
  docker exec -it gitlab gitlab-rails runner 'user = Users::CreateService.new(nil, {username: "gitlab", name: "Administrator", email: "gitlab@example.com", password: "G!tLbS#cret2025", skip_confirmation: true}).execute; user.update(admin: true)'
  ```

or You can use Gitea (Fast and Light)
- Gitea: http://localhost:3000

- Jupyter: http://localhost:8888  
  - Check container logs for the access token or open the URL with the token provided by the container logs => Token: "dev".

- MinIO: http://localhost:9991  
  - Default: `minio` / `minio123`

- Spark UI: http://localhost:8880

- Spark History: http://localhost:18080

- Redis UI: http://localhost:18081

- DataHub UI: http://localhost:9002 (Optional)

- Postgres UI: http://localhost:9081

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
ssh -L 8899:localhost:8888 -L 8083:localhost:8083 -L 8880:localhost:8880 -L 18080:localhost:18080 -L 3000:localhost:3000 -L 9991:localhost:9991 -L 9081:localhost:9081 root@<remote-host>
```

## Troubleshooting

- If a service fails to start, check `docker compose logs -f <service>` for details.
- On Windows, use WSL2 or Git Bash for Bash scripts. PowerShell snippets are provided above.
- If ports are already in use, stop conflicting services or change port mappings in `services/docker-compose.yml`.

## Security & customization

- Change default passwords before exposing services to a network.
- Configure persistent volumes and secrets in `services/docker-compose.yml` and `.env` files as needed.

If you need further adjustments (port changes, additional services, or CI integration instructions), specify requirements and environment details.