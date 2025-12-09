from __future__ import annotations

import sys
import json
import time
import logging
import pathlib

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DataHubRestEmitter
from datahub.metadata.schema_classes import (
    OwnerClass,
    DomainsClass,
    DateTypeClass,
    OwnershipClass,
    AuditStampClass,
    GlobalTagsClass,
    NumberTypeClass,
    StringTypeClass,
    BooleanTypeClass,
    OtherSchemaClass,
    SchemaFieldClass,
    BrowsePathsV2Class,
    GlossaryTermsClass,
    DatasetProfileClass,
    SchemaMetadataClass,
    TagAssociationClass,
    BrowsePathEntryClass,
    DatasetPropertiesClass,
    DatasetFieldProfileClass,
    SchemaFieldDataTypeClass,
    EditableSchemaMetadataClass,
    EditableSchemaFieldInfoClass,
    GlossaryTermAssociationClass,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def load_metadata_from_json(fp: str) -> dict | None:
    if not pathlib.Path(fp).exists():
        logger.error("File not found: %s", fp)
        return None
    with pathlib.Path(fp).open(encoding="utf-8") as f:
        return json.load(f)


def emit(emitter: DataHubRestEmitter, urn: str, aspect: object) -> None:
    mcp = MetadataChangeProposalWrapper(entityUrn=urn, aspect=aspect)
    emitter.emit(mcp)


def update_metadata_from_json(gms_server: str, json_file_path: str) -> None:  # noqa: C901, PLR0914
    data = load_metadata_from_json(json_file_path)
    if not data:
        return

    dataset_urn = data["dataset_urn"]
    emitter = DataHubRestEmitter(gms_server=gms_server)
    now = int(time.time() * 1000)

    # ============================
    # 1. Dataset Documentation
    # ============================
    documentation = data.get("documentation")
    last_updated_time = data.get("lastUpdated", int(time.time() * 1000))
    props_aspect = DatasetPropertiesClass(
        description=documentation,
        lastModified=AuditStampClass(
            time=last_updated_time, actor="urn:li:corpuser:etl_process"
        ),
    )

    emit(emitter, dataset_urn, props_aspect)

    # ============================
    # 2. Owners
    # ============================
    owners = data.get("owners", [])
    if owners:
        owner_list = [OwnerClass(owner=o["owner"], type=o["type"]) for o in owners]
        ownership = OwnershipClass(owners=owner_list)
        emit(emitter, dataset_urn, ownership)

    # ============================
    # 3. Domain
    # ============================
    if data.get("domain"):
        domains = DomainsClass(domains=[data["domain"]])
        emit(emitter, dataset_urn, domains)

    # ============================
    # 4. Dataset-level Tags
    # ============================
    if data.get("dataset_tags"):
        tag_asso = [TagAssociationClass(tag=t) for t in data["dataset_tags"]]
        gtags = GlobalTagsClass(tags=tag_asso)
        emit(emitter, dataset_urn, gtags)

    # ============================
    # 5. Dataset-level Glossary Terms
    # ============================
    if data.get("dataset_terms"):
        term_asso = [GlossaryTermAssociationClass(urn=t) for t in data["dataset_terms"]]
        gterms = GlossaryTermsClass(
            terms=term_asso,
            auditStamp=AuditStampClass(time=now, actor="urn:li:corpuser:data_admin"),
        )
        emit(emitter, dataset_urn, gterms)

    # ============================
    # 6a. Column-level Metadata
    # ============================
    cols = data.get("columns", [])
    field_infos = []

    for col in cols:
        cname = col["name"]
        desc = col.get("description")
        tags = col.get("tags", [])
        terms = col.get("terms", [])

        gtags = None
        if tags:
            gtags = GlobalTagsClass(tags=[TagAssociationClass(tag=t) for t in tags])

        gterms = None
        if terms:
            gterms = GlossaryTermsClass(
                terms=[GlossaryTermAssociationClass(urn=t) for t in terms],
                auditStamp=AuditStampClass(time=now, actor="urn:li:corpuser:data_admin"),
            )

        field_infos.append(
            EditableSchemaFieldInfoClass(
                fieldPath=cname,
                description=desc,
                globalTags=gtags,
                glossaryTerms=gterms,
            )
        )

    schema_md = EditableSchemaMetadataClass(
        editableSchemaFieldInfo=field_infos,
        created=AuditStampClass(time=now, actor="urn:li:corpuser:data_admin"),
    )

    emit(emitter, dataset_urn, schema_md)

    # ============================
    # 6b. Column Type SchemaMetadata
    # ============================

    def map_type(t: str) -> object:
        t = t.lower()
        if t in {"string", "varchar", "text"}:
            return StringTypeClass()
        if t in {"int", "bigint", "float", "double", "number", "numeric"}:
            return NumberTypeClass()
        if t in {"bool", "boolean"}:
            return BooleanTypeClass()
        if t in ("date"):
            return DateTypeClass()
        return StringTypeClass()

    schema_fields = [
        SchemaFieldClass(
            fieldPath=col["name"],
            type=SchemaFieldDataTypeClass(type=map_type(col.get("type", ""))),
            nativeDataType=col.get("type", ""),
            description=col.get("description", ""),
        )
        for col in cols
    ]

    schema_metadata = SchemaMetadataClass(
        schemaName="main",
        platform="urn:li:dataPlatform:hive",
        version=0,
        hash="",
        platformSchema=OtherSchemaClass(rawSchema=""),
        fields=schema_fields,
    )

    emit(emitter, dataset_urn, schema_metadata)

    # ============================
    # 7. Dataset Profile (Stats)
    # ============================
    profile = data.get("dataset_profile")
    if profile:
        column_profiles = [
            DatasetFieldProfileClass(
                fieldPath=col.get("fieldPath"),
                uniqueCount=col.get("uniqueCount"),
                uniqueProportion=col.get("uniqueProportion"),
                nullCount=col.get("nullCount"),
                nullProportion=col.get("nullProportion"),
                min=col.get("min"),
                max=col.get("max"),
                mean=col.get("mean"),
                median=col.get("median"),
                stdev=col.get("stdev"),
                quantiles=col.get("quantiles"),
                distinctValueFrequencies=col.get("distinctValueFrequencies"),
                histogram=col.get("histogram"),
                sampleValues=col.get("sampleValues"),
            )
            for col in profile.get("columnProfiles", [])
        ]

        ds_profile = DatasetProfileClass(
            timestampMillis=profile.get("timestampMillis"),
            rowCount=profile.get("rowCount"),
            columnCount=profile.get("columnCount"),
            sizeInBytes=profile.get("sizeInBytes"),
            fieldProfiles=column_profiles,
        )

        emit(emitter, dataset_urn, ds_profile)

    # ============================
    # 8. Browse Paths
    # ============================
    path_str = data.get("browse_path")
    browse_path_entries = [BrowsePathEntryClass(id=name) for name in path_str.split("/")]
    browse_paths_v2_aspect = BrowsePathsV2Class(path=browse_path_entries)
    emit(emitter, dataset_urn, browse_paths_v2_aspect)


if __name__ == "__main__":
    GMS_SERVER = "http://localhost:8080"
    JSON_FILE_PATHS = [
        "./src/import_by_json/json_data/table_a_metadata.json",
        "./src/import_by_json/json_data/table_b_metadata.json",
        "./src/import_by_json/json_data/table_c_metadata.json",
        "./src/import_by_json/json_data/all_report_metadata.json",
    ]

    for JSON_FILE_PATH in JSON_FILE_PATHS:
        logger.info("Starting metadata update from JSON: %s", JSON_FILE_PATH)
        update_metadata_from_json(GMS_SERVER, JSON_FILE_PATH)
        logger.info("Metadata update completed.")
