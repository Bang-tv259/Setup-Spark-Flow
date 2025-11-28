# Setup server


## 0, Save image (Optional)
```bash
mkdir -p ./docker_image && for img in $(docker images --format "{{.Repository}}:{{.Tag}} {{.Size}}" | grep '^my-' | sort -k2 -h | awk '{print $1}'); do docker save "$img" | gzip > "./docker_image/${img//[:\/]/_}.tar.gz"; done
```

## 1, Load image
```bash
for f in docker_image/*.tar.gz; do gunzip -c "$f" | docker load; done
```

## 2, Run services
```bash
cd services

docker compose up -d
```

## 3, Check services

- Airflow: http://localhost:8083 (airflow / airflow123)
- Gitlab: http://localhost:9084 or http://gitlab:9084 (root / gitlab123)
- Jupyter: http://localhost:8888
- Minio: http://localhost:9991
- Spark-UI: http://localhost:8880

## 4, SSH port to browser (Optional)
```bash
ssh -L 8083:localhost:8083 <your-name>@<your-ip>

ssh -L 9084:localhost:9084 <your-name>@<your-ip>

ssh -L 8888:localhost:8888 <your-name>@<your-ip>

ssh -L 8880:localhost:8880 <your-name>@<your-ip>
```