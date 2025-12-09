from __future__ import annotations

import sys
import logging

from datahub.ingestion.run.pipeline import Pipeline


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logging.getLogger("datahub").setLevel(logging.INFO)


# Pipeline configuration
config = {
    "source": {
        "type": "s3",
        "config": {
            "platform": "s3",
            "aws_config": {
                "aws_access_key_id": "minio",
                "aws_secret_access_key": "minio123",
                "aws_region": "ap-southeast-1",
                "aws_endpoint_url": "http://localhost:9990",
            },
            "profiling": {"enabled": False},
            "path_specs": [
                {
                    "include": "s3://test/{table}/final_fts/*",
                    "file_types": ["parquet"],
                }
            ],
        },
    },
    "transformers": [
        {
            "type": "simple_add_dataset_ownership",
            "config": {
                "owner_urns": ["urn:li:corpuser:data_admin"],
                "ownership_type": "TECHNICAL_OWNER",
            },
        },
        {
            "type": "simple_add_dataset_domain",
            "config": {
                "domains": ["urn:li:domain:Telecom"],
            },
        },
        {
            "type": "simple_add_dataset_tags",
            "config": {
                "tag_urns": ["urn:li:tag:RawData"],
            },
        },
        {
            "type": "simple_add_dataset_terms",
            "config": {
                "term_urns": ["urn:li:glossaryTerm:Public"],
            },
        },
    ],
    "sink": {
        "type": "datahub-rest",
        "config": {"server": "http://localhost:8080"},
    },
}

if __name__ == "__main__":
    pipeline = Pipeline.create(config)
    pipeline.run()
    pipeline.raise_from_status()
