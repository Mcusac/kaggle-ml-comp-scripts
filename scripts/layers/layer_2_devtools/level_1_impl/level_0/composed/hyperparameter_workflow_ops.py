"""Hyperparameter analyze + verify workflows (metadata load, stats, recommendations)."""

import json
import statistics
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from layers.layer_0_core.level_4 import load_json, save_json

from layers.layer_2_devtools.level_0_infra.level_0 import (
    extract_tested_values,
    filter_out_existing_combinations,
    find_duplicates_in_metadata,
    generate_combinations,
    get_hyperparameters_for_model,
    load_and_join_metadata,
    load_regression_metadata,
)
from layers.layer_2_devtools.level_0_infra.level_1 import (
    analyze_parameter_trends,
    calculate_parameter_statistics,
    generate_focused_grid_recommendations,
    identify_top_performers,
)

def _normalize_model_type(model_type: str) -> str:
    mt = model_type.lower()
    return "xgboost" if mt == "xgb" else mt


# --- analyze ---


def format_statistics_table(stats: Dict[str, Any]) -> str:
    if "error" in stats:
        return f"  Error: {stats['error']}"

    lines = [f"  Parameter: {stats['parameter']}"]
    lines.append(f"  Unique values: {stats['unique_values']}")
    lines.append(f"  Total records: {stats['total_records']}")

    if stats.get("correlation") is not None:
        lines.append(f"  Correlation: {stats['correlation']:.4f}")

    value_stats = stats.get("value_statistics", {})
    if value_stats:
        lines.append("\n  Value Statistics:")
        for value, v_stats in sorted(
            value_stats.items(), key=lambda x: x[1]["mean"], reverse=True
        )[:5]:
            lines.append(
                f"    {value}: count={v_stats['count']}, mean={v_stats['mean']:.6f}, "
                f"std={v_stats['std']:.6f}"
            )

    return "\n".join(lines)


def format_top_configurations(top_configs: List[Dict[str, Any]], n: int = 10) -> str:
    lines: list[str] = []
    for i, config in enumerate(top_configs[:n], 1):
        cv_score = config.get("cv_score", "N/A")
        variant_id = config.get("variant_id", "N/A")
        lines.append(f"\n{i}. Score: {cv_score:.6f}, Variant: {variant_id}")

        hyperparams = config.get("hyperparameters", {})
        for param in sorted(hyperparams.keys()):
            value = hyperparams.get(param, "N/A")
            lines.append(f"   {param}: {value}")

    return "\n".join(lines)


def _load_and_validate_metadata(
    model_type: str, metadata_dir: Optional[Path]
) -> Tuple[List[Dict[str, Any]], Dict[str, List[Any]]]:
    print(f"Loading metadata for {model_type}...")
    combined_data = load_and_join_metadata(model_type, metadata_dir)

    if not combined_data:
        raise ValueError(f"No combined data found for {model_type}")

    print(f"✅ Loaded {len(combined_data)} configurations")

    print("\nExtracting tested hyperparameter values...")
    metadata = load_regression_metadata(model_type, metadata_dir)
    tested_values = extract_tested_values(metadata, model_type=model_type)
    print(f"✅ Found tested values for {len(tested_values)} parameters")

    return combined_data, tested_values


def _calculate_overall_statistics(combined_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    all_scores = [
        r["cv_score"]
        for r in combined_data
        if r.get("cv_score") is not None
        and not (
            isinstance(r.get("cv_score"), float) and (r["cv_score"] != r["cv_score"])
        )
    ]

    if not all_scores:
        raise ValueError("No valid scores found in combined data")

    return {
        "mean": statistics.mean(all_scores),
        "median": statistics.median(all_scores),
        "std": statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0,
        "min": min(all_scores),
        "max": max(all_scores),
    }


def _generate_json_analysis(
    combined_data: List[Dict[str, Any]],
    tested_values: Dict[str, List[Any]],
    model_type: str,
    top_n: int,
    top_percentile: float,
    expansion_factor: float,
) -> Dict[str, Any]:
    print("\nAnalyzing hyperparameters...")

    param_names = get_hyperparameters_for_model(model_type)
    param_stats: Dict[str, Any] = {}
    param_trends: Dict[str, Any] = {}

    for param_name in param_names:
        param_stats[param_name] = calculate_parameter_statistics(
            combined_data, param_name
        )
        param_trends[param_name] = analyze_parameter_trends(combined_data, param_name)

    top_performers = identify_top_performers(combined_data, top_n=top_n)

    recommendations = generate_focused_grid_recommendations(
        combined_data,
        tested_values,
        model_type=model_type,
        top_percentile=top_percentile,
        expansion_factor=expansion_factor,
    )

    return {
        "parameter_statistics": param_stats,
        "parameter_trends": param_trends,
        "top_performers": top_performers,
        "recommendations": recommendations,
    }


def _print_console_analysis(
    combined_data: List[Dict[str, Any]],
    tested_values: Dict[str, List[Any]],
    model_type: str,
    all_scores: List[float],
    top_n: int,
    top_percentile: float,
    expansion_factor: float,
    output_path: Optional[Path],
) -> None:
    print(f"\n{'=' * 80}")
    print("OVERALL STATISTICS")
    print(f"{'=' * 80}")
    print(f"Total valid results: {len(all_scores)}")
    print(f"Mean:   {statistics.mean(all_scores):.6f}")
    print(f"Median: {statistics.median(all_scores):.6f}")
    print(f"Std:    {statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0:.6f}")
    print(f"Min:    {min(all_scores):.6f}")
    print(f"Max:    {max(all_scores):.6f}")

    print(f"\n{'=' * 80}")
    print("HYPERPARAMETER ANALYSIS")
    print(f"{'=' * 80}")

    param_names = get_hyperparameters_for_model(model_type)
    all_stats: Dict[str, Any] = {}

    for param_name in param_names:
        print(f"\nAnalyzing {param_name}...")
        stats = calculate_parameter_statistics(combined_data, param_name)
        trends = analyze_parameter_trends(combined_data, param_name)

        all_stats[param_name] = stats

        print(format_statistics_table(stats))

        if "error" not in trends:
            print(f"\nTrend Analysis for {param_name}:")
            if trends.get("is_numeric"):
                print(f"  Trend: {trends['trend']} (strength: {trends['trend_strength']:.4f})")
                print(f"  Low value range mean score: {trends['low_value_mean_score']:.6f}")
                print(
                    f"  High value range mean score: {trends['high_value_mean_score']:.6f}"
                )
            else:
                best_value = trends.get("best_value")
                best_score = trends.get("best_value_mean_score", 0)
                print(f"  Best value: {best_value} (mean score: {best_score:.6f})")

    print(f"\n{'=' * 80}")
    print("TOP PERFORMERS")
    print(f"{'=' * 80}")

    top_performers = identify_top_performers(combined_data, top_n=top_n)
    print(format_top_configurations(top_performers, n=top_n))

    print(f"\n{'=' * 80}")
    print("FOCUSED GRID SEARCH RECOMMENDATIONS")
    print(f"{'=' * 80}")

    recommendations = generate_focused_grid_recommendations(
        combined_data,
        tested_values,
        model_type=model_type,
        top_percentile=top_percentile,
        expansion_factor=expansion_factor,
    )

    print(
        f"\nRecommended parameter ranges based on top {top_percentile * 100:.1f}% "
        "performers (NEW values only):"
    )
    for param_name, values in recommendations.items():
        tested_count = len(tested_values.get(param_name, []))
        print(f"\n{param_name}:")
        print(f"  {values}")
        print(f"  ({len(values)} NEW values, excluding {tested_count} tested)")

    if output_path:
        save_json(recommendations, output_path)
        print(f"\n✅ Recommendations saved to: {output_path}")

    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")

    best_score = max(all_scores)
    worst_score = min(all_scores)
    score_range = best_score - worst_score
    median_score = statistics.median(all_scores)

    print(f"\nScore Range: {worst_score:.6f} to {best_score:.6f} (range: {score_range:.6f})")
    print(f"Median Score: {median_score:.6f}")
    print(f"Best Score Improvement over Median: {best_score - median_score:.6f}")

    correlations = {
        param: stats.get("correlation", 0)
        for param, stats in all_stats.items()
        if stats.get("correlation") is not None
    }

    if correlations:
        sorted_correlations = sorted(
            correlations.items(), key=lambda x: abs(x[1]), reverse=True
        )
        print("\nStrongest Parameter Correlations:")
        for param, corr in sorted_correlations[:5]:
            print(f"  {param}: {corr:.4f}")

    print("\n✅ Analysis complete!")


def run_analyze_hyperparameters(
    model_type: str,
    metadata_dir: Optional[Path],
    top_n: int,
    top_percentile: float,
    expansion_factor: float,
    output_path: Optional[Path],
    as_json: bool,
) -> int:
    model_type = _normalize_model_type(model_type)
    try:
        combined_data, tested_values = _load_and_validate_metadata(
            model_type, metadata_dir
        )

        all_scores = [
            r["cv_score"]
            for r in combined_data
            if r.get("cv_score") is not None
            and not (
                isinstance(r.get("cv_score"), float)
                and (r["cv_score"] != r["cv_score"])
            )
        ]
        overall_stats = _calculate_overall_statistics(combined_data)

        results: Dict[str, Any] = {
            "model_type": model_type,
            "total_configurations": len(combined_data),
            "valid_scores": len(all_scores),
            "overall_statistics": overall_stats,
        }

        if as_json:
            analysis_results = _generate_json_analysis(
                combined_data,
                tested_values,
                model_type,
                top_n,
                top_percentile,
                expansion_factor,
            )
            results.update(analysis_results)

            if output_path:
                save_json(results, output_path)
                print(f"\n✅ Full analysis saved to: {output_path}")
            else:
                print(json.dumps(results, indent=2, default=str))

            return 0

        _print_console_analysis(
            combined_data,
            tested_values,
            model_type,
            all_scores,
            top_n,
            top_percentile,
            expansion_factor,
            output_path,
        )

        return 0

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return 1


# --- verify ---


def validate_recommendations(
    recommendations: Dict[str, List[Any]],
    model_type: str = "lgbm",
) -> List[str]:
    errors: list[str] = []
    param_names = get_hyperparameters_for_model(model_type)

    missing_params = set(param_names) - set(recommendations.keys())
    if missing_params:
        errors.append(f"Missing parameters in recommendations: {missing_params}")

    for param, values in recommendations.items():
        if not values:
            errors.append(f"Parameter {param} has empty value list")
        elif not isinstance(values, list):
            errors.append(f"Parameter {param} values must be a list, got {type(values)}")

    invalid_params = set(recommendations.keys()) - set(param_names)
    if invalid_params:
        errors.append(f"Invalid parameter names: {invalid_params}")

    return errors


def check_duplicates_in_recommendations(
    recommendations: Dict[str, List[Any]],
    model_type: str = "lgbm",
) -> Dict[str, Any]:
    from layers.layer_2_devtools.level_0_infra.level_0.hyperparameter.hyperparameter_utils import (
        normalize_hyperparameters,
    )

    combinations = generate_combinations(recommendations)
    signatures: Dict[Any, Any] = {}
    duplicates: list[dict[str, Any]] = []

    for combo in combinations:
        sig = normalize_hyperparameters(combo, model_type=model_type)
        if sig in signatures:
            duplicates.append({"combination": combo, "duplicate_of": signatures[sig]})
        else:
            signatures[sig] = combo

    return {
        "total_combinations": len(combinations),
        "unique_combinations": len(signatures),
        "duplicates": duplicates,
        "has_duplicates": len(duplicates) > 0,
    }


def _load_and_validate_recommendations(
    recommendations_path: Path,
) -> Dict[str, List[Any]]:
    if not recommendations_path.exists():
        raise FileNotFoundError(f"Recommendations file not found: {recommendations_path}")

    recommendations = load_json(recommendations_path)

    if not isinstance(recommendations, dict):
        raise ValueError(f"Recommendations must be a dictionary, got {type(recommendations)}")

    print(f"✅ Loaded recommendations from: {recommendations_path}")
    print(f"   Parameters: {list(recommendations.keys())}")

    return recommendations


def _validate_recommendations_structure(
    recommendations: Dict[str, List[Any]], model_type: str
) -> bool:
    print("\nValidating recommendations structure...")
    validation_errors = validate_recommendations(recommendations, model_type=model_type)

    if validation_errors:
        print("❌ Validation errors found:")
        for error in validation_errors:
            print(f"   - {error}")
        return False

    print("✅ Recommendations structure is valid")
    return True


def _check_recommendation_duplicates(
    recommendations: Dict[str, List[Any]], model_type: str
) -> Dict[str, Any]:
    print("\nChecking for duplicate combinations in recommendations...")
    duplicate_check = check_duplicates_in_recommendations(
        recommendations, model_type=model_type
    )

    if duplicate_check["has_duplicates"]:
        print(f"⚠️  Warning: Found {len(duplicate_check['duplicates'])} duplicate combinations")
        for dup in duplicate_check["duplicates"][:5]:
            print(f"   Duplicate: {dup['combination']}")
    else:
        print(
            f"✅ No duplicates found ({duplicate_check['unique_combinations']} unique combinations)"
        )

    return duplicate_check


def _analyze_metadata(
    metadata: List[Dict[str, Any]], model_type: str
) -> tuple[Dict[str, List[Any]], Dict[tuple, List[Dict[str, Any]]]]:
    print(f"✅ Loaded {len(metadata)} variants from metadata")

    tested_values = extract_tested_values(metadata, model_type=model_type)
    print(f"✅ Extracted tested values for {len(tested_values)} parameters")

    print("\nChecking for duplicates in existing metadata...")
    metadata_duplicates = find_duplicates_in_metadata(metadata, model_type=model_type)

    if metadata_duplicates:
        print(
            f"⚠️  Warning: Found {len(metadata_duplicates)} duplicate hyperparameter combinations in metadata"
        )
        for sig, variants in list(metadata_duplicates.items())[:3]:
            variant_ids = [v.get("variant_id") for v in variants]
            print(f"   Duplicate signature: {variant_ids}")
    else:
        print("✅ No duplicates found in metadata")

    return tested_values, metadata_duplicates


def _check_combination_overlap(
    recommendations: Dict[str, List[Any]],
    metadata: List[Dict[str, Any]],
    model_type: str,
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    print("\nChecking which recommended combinations already exist in metadata...")
    recommended_combos = generate_combinations(recommendations)
    new_combos, existing_combos = filter_out_existing_combinations(
        recommended_combos,
        metadata,
        model_type=model_type,
    )

    print("✅ Analysis complete:")
    print(f"   Total recommended combinations: {len(recommended_combos)}")
    print(f"   New combinations: {len(new_combos)}")
    print(f"   Existing combinations: {len(existing_combos)}")

    if existing_combos:
        print(f"\n⚠️  Warning: {len(existing_combos)} recommended combinations already exist:")
        for existing in existing_combos[:5]:
            combo = existing["combination"]
            variant_id = existing.get("variant_id", "N/A")
            print(f"   {combo} -> variant_id: {variant_id}")

    return new_combos, existing_combos


def _calculate_parameter_overlap(
    recommendations: Dict[str, List[Any]],
    tested_values: Dict[str, List[Any]],
) -> Dict[str, Dict[str, Any]]:
    print("\nChecking parameter value overlap with tested values...")
    overlap_summary: Dict[str, Dict[str, Any]] = {}

    for param, rec_values in recommendations.items():
        tested = set(tested_values.get(param, []))
        rec_set = set(rec_values)
        overlap = rec_set & tested
        new_values = rec_set - tested

        overlap_summary[param] = {
            "recommended": len(rec_values),
            "tested": len(tested),
            "overlap": len(overlap),
            "new": len(new_values),
            "overlap_values": sorted(list(overlap)) if overlap else [],
        }

    return overlap_summary


def _print_json_output(
    model_type: str,
    validation_errors: List[str],
    duplicate_check: Dict[str, Any],
    metadata_duplicates: Dict[tuple, List[Dict[str, Any]]],
    new_combos: List[Dict[str, Any]],
    existing_combos: List[Dict[str, Any]],
    overlap_summary: Dict[str, Dict[str, Any]],
) -> None:
    results = {
        "model_type": model_type,
        "validation": {"valid": len(validation_errors) == 0, "errors": validation_errors},
        "duplicate_check": duplicate_check,
        "metadata_duplicates": {
            "count": len(metadata_duplicates),
            "examples": [
                {
                    "signature": str(sig),
                    "variant_ids": [v.get("variant_id") for v in variants],
                }
                for sig, variants in list(metadata_duplicates.items())[:5]
            ],
        },
        "recommendation_overlap": {
            "total_combinations": len(new_combos) + len(existing_combos),
            "new_combinations": len(new_combos),
            "existing_combinations": len(existing_combos),
            "existing_examples": existing_combos[:10],
        },
        "parameter_overlap": overlap_summary,
    }
    print(json.dumps(results, indent=2, default=str))


def _print_console_output_verify(
    new_combos: List[Dict[str, Any]],
    existing_combos: List[Dict[str, Any]],
    overlap_summary: Dict[str, Dict[str, Any]],
) -> None:
    print("\nParameter Value Overlap Summary:")
    for param, summary in overlap_summary.items():
        print(f"\n{param}:")
        print(f"  Recommended values: {summary['recommended']}")
        print(f"  Tested values: {summary['tested']}")
        print(f"  Overlap: {summary['overlap']} values")
        print(f"  New values: {summary['new']} values")
        if summary["overlap_values"]:
            print(f"  Overlapping values: {summary['overlap_values'][:10]}")

    print(f"\n{'=' * 80}")
    print("VERIFICATION SUMMARY")
    print(f"{'=' * 80}")

    total_new = sum(s["new"] for s in overlap_summary.values())
    total_overlap = sum(s["overlap"] for s in overlap_summary.values())
    total_combos = len(new_combos) + len(existing_combos)

    print("✅ Recommendations are valid")
    print(f"✅ {len(new_combos)} new combinations to test")
    print(f"⚠️  {len(existing_combos)} combinations already exist in metadata")
    print(f"✅ {total_new} new parameter values recommended")
    print(f"⚠️  {total_overlap} parameter values overlap with tested values")

    if len(new_combos) == 0:
        print("\n⚠️  Warning: All recommended combinations already exist in metadata!")
        print("   Consider updating recommendations with new parameter values.")
    elif len(new_combos) < total_combos * 0.5:
        print("\n⚠️  Warning: More than 50% of recommended combinations already exist.")
        print("   Consider expanding parameter ranges or exploring new values.")
    else:
        print("\n✅ Good coverage: Most recommended combinations are new.")


def run_verify_hyperparameter_recommendations(
    model_type: str,
    recommendations_path: Path,
    metadata_dir: Optional[Path],
    as_json: bool,
) -> int:
    model_type = _normalize_model_type(model_type)
    try:
        recommendations = _load_and_validate_recommendations(recommendations_path)

        if not _validate_recommendations_structure(recommendations, model_type):
            return 1

        duplicate_check = _check_recommendation_duplicates(recommendations, model_type)

        print("\nLoading existing metadata...")
        metadata = load_regression_metadata(model_type, metadata_dir)
        tested_values, metadata_duplicates = _analyze_metadata(metadata, model_type)

        new_combos, existing_combos = _check_combination_overlap(
            recommendations, metadata, model_type
        )

        overlap_summary = _calculate_parameter_overlap(recommendations, tested_values)

        validation_errors = validate_recommendations(recommendations, model_type=model_type)
        if as_json:
            _print_json_output(
                model_type,
                validation_errors,
                duplicate_check,
                metadata_duplicates,
                new_combos,
                existing_combos,
                overlap_summary,
            )
        else:
            _print_console_output_verify(new_combos, existing_combos, overlap_summary)

        return 0

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return 1
