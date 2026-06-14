"""Configuration models for the New Zealand Medical-Legal Corpus pipeline."""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, HttpUrl


class PathsConfig(BaseModel):
    """Configuration for paths used in the pipeline."""

    raw_dir: Path
    processed_dir: Path


class ScrapingConfig(BaseModel):
    """Configuration for crawler behavior."""

    page_size: int = Field(gt=0)
    max_pages: int = Field(gt=0)
    user_agent: str
    timeout: int = Field(gt=0)


class ValidationConfig(BaseModel):
    """Configuration for metadata validation rules."""

    required_metadata_fields: list[str]


class FetchConfig(BaseModel):
    """Configuration for HTTP fetching behavior."""

    retry_attempts: int = Field(default=3, ge=0)
    retry_backoff_base_seconds: float = Field(default=1.0, gt=0)
    rate_limit_per_second: float = Field(default=2.0, gt=0)
    request_timeout_seconds: int = Field(default=30, gt=0)
    user_agent: str = Field(default="Mozilla/5.0 (compatible; NZ-Medicolegal-Corpus-Sync/1.0)")


class PipelineDetails(BaseModel):
    """Details of the specific ingestion pipeline."""

    name: str
    description: str
    source_url: HttpUrl
    base_url: HttpUrl
    paths: PathsConfig
    scraping: ScrapingConfig
    validation: ValidationConfig


class PipelineConfig(BaseModel):
    """Root configuration model for the ingestion pipeline."""

    pipeline: PipelineDetails


class HdcPipelineConfig(BaseModel):
    """HDC-specific pipeline configuration with fetch settings."""

    pipeline: PipelineDetails = Field(default_factory=lambda: PipelineDetails(
        name="hdc",
        description="Health and Disability Commissioner (HDC) NZ Decisions Ingestion Pipeline",
        source_url="https://www.hdc.org.nz/decisions/search-decisions/",
        base_url="https://www.hdc.org.nz",
        paths=PathsConfig(raw_dir=Path("data/raw/hdc"), processed_dir=Path("data/processed")),
        scraping=ScrapingConfig(page_size=10, max_pages=5, user_agent="Mozilla/5.0 (compatible; NZ-Medicolegal-Corpus-Sync/1.0)", timeout=30),
        validation=ValidationConfig(required_metadata_fields=["case_id", "date", "title", "commissioner", "citation", "url"]),
    ))
    fetch: FetchConfig = Field(default_factory=FetchConfig)


class SourceConfig(BaseModel):
    """Configuration for a single data source."""

    source_id: str
    name: str
    url: str = ""
    config_path: Path


def load_pipeline_config(config_path: Path | str) -> PipelineConfig:
    """Load and validate pipeline configuration from a YAML file.

    Parameters
    ----------
    config_path : Path or str
        Path to the configuration YAML file.

    Returns
    -------
    PipelineConfig
        Validated configuration model.

    """
    path = Path(config_path)
    if not path.is_file():
        msg = f"Configuration file not found: {path}"
        raise FileNotFoundError(msg)

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return PipelineConfig.model_validate(data)



def load_multi_source_config(source_ids: list[str] | None = None) -> dict[str, PipelineConfig]:
    """Load pipeline configs for multiple sources.

    Parameters
    ----------
    source_ids : list of str, optional
        Source IDs to load. If None, all sources from the registry are loaded.

    Returns
    -------
    dict of str -> PipelineConfig
        Mapping of source ID to loaded config. Sources whose config files are
        missing, have unknown IDs, or fail validation are silently skipped.

    Notes
    -----
    Some sources in the registry are stubs with empty URLs. Their config files
    exist but may fail ``HttpUrl`` validation. Those sources are gracefully
    skipped so that callers only receive fully-validated configurations.

    """
    from corpus_cases_medilegal_nz.sources import SOURCE_REGISTRY

    if source_ids is None:
        source_ids = list(SOURCE_REGISTRY.keys())

    configs: dict[str, PipelineConfig] = {}
    for sid in source_ids:
        if sid not in SOURCE_REGISTRY:
            continue  # skip unknown source IDs
        info = SOURCE_REGISTRY[sid]
        cfg_path = Path(info["config"])
        if not cfg_path.is_file():
            continue  # skip missing config files
        try:
            configs[sid] = load_pipeline_config(cfg_path)
        except Exception:
            continue  # skip configs that fail validation (e.g. empty URLs)
    return configs
