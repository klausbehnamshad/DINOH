"""oh_eval — evaluation logic for the C²DH Oral History benchmark.

The notebook is the narrative surface; the testable core lives here.
"""

from .metrics import (
    SEGEVAL_AVAILABLE,
    CONTROLLED_FIELDS,
    EXACT_MATCH_FIELDS,
    LIST_FIELDS,
    FREE_TEXT_FIELDS,
    timecode_to_seconds,
    segments_to_masses,
    evaluate_segmentation,
    evaluate_metadata,
)
from .schema import (
    load_schema,
    validate_luxoh_record,
    validate_eval_record,
    validate_corpus,
    contiguity_errors,
)
from .corpus import (
    load_corpus,
    records,
    language_counts,
    validate_corpus_shape,
)
from .reports import (
    write_validation_report,
    write_task1_reports,
    write_task2_reports,
    write_segmentation_latex,
)

__all__ = [
    "SEGEVAL_AVAILABLE",
    "CONTROLLED_FIELDS",
    "EXACT_MATCH_FIELDS",
    "LIST_FIELDS",
    "FREE_TEXT_FIELDS",
    "timecode_to_seconds",
    "segments_to_masses",
    "evaluate_segmentation",
    "evaluate_metadata",
    "load_schema",
    "validate_luxoh_record",
    "validate_eval_record",
    "validate_corpus",
    "contiguity_errors",
    "load_corpus",
    "records",
    "language_counts",
    "validate_corpus_shape",
    "write_validation_report",
    "write_task1_reports",
    "write_task2_reports",
    "write_segmentation_latex",
]

__version__ = "1.1.0"
