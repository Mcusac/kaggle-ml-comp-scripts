"""Main CLI entry point for ML Competition Framework."""

from path_bootstrap import prepend_framework_paths

prepend_framework_paths()

import os
import sys
import warnings
import argparse

from run_helpers import (
    get_framework_subparser_skips,
    get_handler_context_builder,
    load_contest_handlers,
    preload_contest_registrations,
    resolve_contest,
    setup_logging_and_environment,
)
from level_1 import setup_framework_subparsers
from level_0 import dispatch_command, get_logger
from layers.layer_1_competition.level_0_infra.level_1 import get_command_handlers

logger = get_logger(__name__)

# CRITICAL: Set PyTorch CUDA allocator config BEFORE importing PyTorch
# This must be done before any PyTorch imports to take effect
# expandable_segments helps reduce memory fragmentation and OOM errors
os.environ.setdefault('PYTORCH_CUDA_ALLOC_CONF', 'expandable_segments:True')

# Configure Python debugger to work with frozen modules (Python 3.11+)
# This is proper configuration, not suppression - tells debugger we understand the limitation
os.environ.setdefault('PYDEVD_DISABLE_FILE_VALIDATION', '1')


# TODO: Consider moving error logic to error handling package.
# Suppress harmless errors from stderr (protobuf/HuggingFace compatibility issues)
# MessageFactory.GetPrototype AttributeError is harmless and occurs when loading HuggingFace models
# with certain protobuf versions - it's a known compatibility issue that doesn't affect functionality
class FilteredStderr:
    """Filter stderr to suppress harmless compatibility errors."""
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
    
    def write(self, message):
        # Filter out MessageFactory.GetPrototype AttributeError messages (protobuf/HF compatibility)
        if 'MessageFactory' in message and 'GetPrototype' in message:
            return  # Suppress this harmless error
        self.original_stderr.write(message)
    
    def flush(self):
        self.original_stderr.flush()

# Replace stderr with filtered version to suppress MessageFactory errors
sys.stderr = FilteredStderr(sys.stderr)

# Note: Pydantic warnings are expected and intermittent - they come from dependencies
# (likely HuggingFace transformers) and are harmless. We keep the filter minimal
# to avoid hiding vital warnings from our own code.
# Filter UnsupportedFieldAttributeWarning from pydantic (comes from dependency usage of Field())
# This warning occurs when dependencies use Field() with attributes that don't apply in their context
warnings.filterwarnings('ignore', category=UserWarning, module='pydantic._internal._generate_schema')
# Also catch by message pattern in case it's emitted differently
warnings.filterwarnings('ignore', message='.*UnsupportedFieldAttributeWarning.*')
warnings.filterwarnings('ignore', message='.*repr.*attribute.*Field.*function.*')
warnings.filterwarnings('ignore', message='.*frozen.*attribute.*Field.*function.*')

def main() -> int:
    """Main entry point."""

    # 1) Early parse: --version, --contest only (so we can resolve contest before building full parser)
    early_parser = argparse.ArgumentParser()
    early_parser.add_argument('--version', action='store_true', help='Show version and exit')
    early_parser.add_argument('--contest', type=str, help='Contest name (e.g., csiro, cafa)')
    args_early, _ = early_parser.parse_known_args()
    if args_early.version:
        print('ML Competition Framework 0.1.0')
        return 0

    candidate_slug = (args_early.contest or "").strip().lower() or os.environ.get(
        "KAGGLE_COMP_CONTEST", ""
    ).strip().lower()
    preload_contest_registrations(candidate_slug=candidate_slug or None)

    # 2) Resolve contest (arg, env, or auto-detect)
    contest_name = resolve_contest(args_early.contest)

    # 3) Build main parser: framework subparsers + contest subparsers
    parser = argparse.ArgumentParser(
        description="ML Competition Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--contest',
        type=str,
        help='Contest name (e.g., csiro, cafa). Auto-detected if not provided.'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    framework_skips = get_framework_subparser_skips(contest_name)
    setup_framework_subparsers(
        subparsers,
        ["vision", "tabular"],
        ["simple_average", "weighted_average", "mean"],
        skip_commands=framework_skips,
    )

    # Contest subparsers (only for the resolved contest)
    contest_handlers = load_contest_handlers(contest_name, subparsers)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    # TODO: potentially replace this function with the ones from logging and system packages.
    setup_logging_and_environment(args)

    try:
        builder = get_handler_context_builder(contest_name)
        framework_handlers = get_command_handlers(builder)
        # Contest wins for any command name also registered in contest_handlers (e.g. RNA3D train/submit).
        # TODO: Move this merge into a layer_1 infra helper (explicit handler precedence) instead of
        # coupling run.py to dispatch_command's primary-first order.
        for cmd in contest_handlers:
            framework_handlers.pop(cmd, None)
        dispatch_command(
            args.command,
            args,
            primary_handlers=framework_handlers,
            fallback_handlers=contest_handlers,
        )
        return 0
    except Exception as e:
        logger.error(f"Command '{args.command}' failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
