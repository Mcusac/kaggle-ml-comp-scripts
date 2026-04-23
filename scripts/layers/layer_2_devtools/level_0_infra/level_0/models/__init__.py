"""Auto-generated package exports."""


from .audit_models import (
    FileReport,
    Violation,
)

from .dead_symbol_config import DeadSymbolConfig
from .dead_file_config import DeadFileConfig

from .precheck_json_contract import (
    ALLOWED_PRECHECK_STATUSES,
    PRECHECK_STATUS_OK,
    PRECHECK_STATUS_SKIPPED_MACHINE,
    is_machine_precheck_ok,
    validate_precheck_json,
)

from .symbol_models import (
    SymbolDefinition,
    SymbolKind,
)

from .symbol_reference_models import SymbolReference

__all__ = [
    "ALLOWED_PRECHECK_STATUSES",
    "DeadFileConfig",
    "DeadSymbolConfig",
    "FileReport",
    "PRECHECK_STATUS_OK",
    "PRECHECK_STATUS_SKIPPED_MACHINE",
    "SymbolDefinition",
    "SymbolKind",
    "SymbolReference",
    "Violation",
    "is_machine_precheck_ok",
    "validate_precheck_json",
]
