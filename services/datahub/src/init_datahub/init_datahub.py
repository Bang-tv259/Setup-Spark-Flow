from __future__ import annotations

import sys
import logging

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DataHubRestEmitter
from datahub.metadata.schema_classes import (
    TagPropertiesClass,
    DomainPropertiesClass,
    GlossaryTermInfoClass,
    DataProductPropertiesClass,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)
logging.getLogger("datahub").setLevel(logging.INFO)


def send_to_datahub(emitter: DataHubRestEmitter, urn: str, aspect: object) -> None:
    try:
        mcp = MetadataChangeProposalWrapper(entityUrn=urn, aspect=aspect)
        emitter.emit(mcp)
        logger.info("Created/Updated: %s", urn)
    except Exception:
        logger.exception("Error creating %s", urn)


def main() -> None:
    gms_server = "http://localhost:8080"

    emitter = DataHubRestEmitter(gms_server=gms_server)

    # Create Domain
    domain_urn = "urn:li:domain:Telecom"
    domain_props = DomainPropertiesClass(
        name="Telecom Domain",
        description="Telecom-related data (SMS, Voice, Data, etc.)",
    )

    send_to_datahub(emitter, domain_urn, domain_props)

    # Create Glossary Terms
    terms_to_create = [
        ("urn:li:glossaryTerm:PII", "PII", "Personally identifiable information"),
        ("urn:li:glossaryTerm:RawData", "Raw Data", "Unprocessed raw data"),
        ("urn:li:glossaryTerm:Public", "Public Data", "Unprocessed public data"),
        (
            "urn:li:glossaryTerm:PersonalData",
            "Personal Data",
            "Data related to an individual's identity",
        ),
        (
            "urn:li:glossaryTerm:Finance",
            "Finance",
            "Data related to financial transactions",
        ),
        ("urn:li:glossaryTerm:Revenue", "Revenue", "Income generated from operations"),
    ]

    for urn, name, definition in terms_to_create:
        props = GlossaryTermInfoClass(
            name=name,
            definition=definition,
            termSource="INTERNAL",
        )
        send_to_datahub(emitter, urn, props)

    # Create Tags
    tags_to_create = [
        ("urn:li:tag:PII", "PII Tag", "Tag for Personally Identifiable Information"),
        ("urn:li:tag:Identifier", "Identifier", "Unique identifier for an entity"),
        ("urn:li:tag:Metric", "Metric", "Quantitative assessment metric"),
        ("urn:li:tag:KPI", "KPI", "Key Performance Indicator"),
    ]

    for urn, name, description in tags_to_create:
        props = TagPropertiesClass(name=name, description=description)
        send_to_datahub(emitter, urn, props)

    # Create Data Product
    dp_urn = "urn:li:dataProduct:TelcoReports"
    dp_props = DataProductPropertiesClass(
        name="Telco Reports",
        description="Aggregated reporting data product",
    )
    send_to_datahub(emitter, dp_urn, dp_props)


if __name__ == "__main__":
    main()
