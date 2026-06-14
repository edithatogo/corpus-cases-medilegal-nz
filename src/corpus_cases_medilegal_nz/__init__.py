"""New Zealand Medical-Legal Corpus ingestion and sync pipeline."""

from corpus_cases_medilegal_nz.config_models import (
    FetchConfig,
    HdcPipelineConfig,
    PipelineConfig,
    PipelineDetails,
    load_pipeline_config,
)
from corpus_cases_medilegal_nz.sources import (
    SOURCE_REGISTRY,
    SourceAdapter,
    get_adapter,
    get_source_ids,
)

__all__ = [
    "SOURCE_REGISTRY",
    "FetchConfig",
    "HdcPipelineConfig",
    "PipelineConfig",
    "PipelineDetails",
    "SourceAdapter",
    "get_adapter",
    "get_source_ids",
    "load_pipeline_config",
]
