from __future__ import annotations

import sys
import json
import logging
import pathlib

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.mce_builder import make_dataset_urn, make_schema_field_urn
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    UpstreamClass,
    UpstreamLineageClass,
    FineGrainedLineageClass,
    FineGrainedLineageUpstreamTypeClass,
    FineGrainedLineageDownstreamTypeClass,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main() -> None:
    emitter = DatahubRestEmitter("http://localhost:8080")
    try:
        with pathlib.Path("./src/import_by_json/json_lineage/lineage_metadata.json").open(
            encoding="utf-8"
        ) as f:
            configs = json.load(f)
    except FileNotFoundError:
        logger.exception("File lineage_metadata.json not found.")
        return

    for config in configs:
        up_conf = config["upstream"]
        down_conf = config["downstream"]
        mapping = config.get("column_mapping", {})

        # Create URNs
        upstream_urn = make_dataset_urn(
            up_conf["platform"], up_conf["name"], up_conf["env"]
        )
        downstream_urn = make_dataset_urn(
            down_conf["platform"], down_conf["name"], down_conf["env"]
        )

        logger.info(
            "\nProcessing: %s (Upstream) ---> %s (Downstream)",
            up_conf["name"],
            down_conf["name"],
        )

        # Create FineGrainedLineageClass instances
        fine_grained_lineages = []
        for up_col, down_col in mapping.items():
            up_field_urn = make_schema_field_urn(upstream_urn, up_col)
            down_field_urn = make_schema_field_urn(downstream_urn, down_col)

            fgl = FineGrainedLineageClass(
                upstreamType=FineGrainedLineageUpstreamTypeClass.FIELD_SET,
                upstreams=[up_field_urn],
                downstreamType=FineGrainedLineageDownstreamTypeClass.FIELD,
                downstreams=[down_field_urn],
                confidenceScore=1.0,
            )
            fine_grained_lineages.append(fgl)
            logger.info("  - Map column: %s -> %s", up_col, down_col)

        upstream_class = UpstreamClass(dataset=upstream_urn, type="TRANSFORMED")
        lineage_aspect = UpstreamLineageClass(
            upstreams=[upstream_class], fineGrainedLineages=fine_grained_lineages
        )
        mcp = MetadataChangeProposalWrapper(
            entityUrn=downstream_urn, aspect=lineage_aspect
        )

        # Send MCP đến DataHub
        try:
            emitter.emit(mcp)
            logger.info("Success: Updated lineage for table %s", down_conf["name"])
        except Exception:
            logger.exception("Failed to update %s", down_conf["name"])


if __name__ == "__main__":
    main()
