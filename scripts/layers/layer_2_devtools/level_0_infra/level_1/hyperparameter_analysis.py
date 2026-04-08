"""Hyperparameter analysis functions for ML model tuning.

This module provides analysis functions for hyperparameter optimization,
following DRY principles by reusing existing framework functions where possible.
"""

import logging
import statistics
from typing import Dict, List, Any
from collections import defaultdict

# Reuse existing framework function for top results extraction
try:
    from layers.layer_0_core.level_5 import extract_top_results
except ImportError:
    # Fallback if contest-specific import fails (may not be available in all contexts)
    extract_top_results = None

from ..level_0.hyperparameter import get_hyperparameters_for_model

logger = logging.getLogger(__name__)


def identify_top_performers(
    combined_data: List[Dict[str, Any]],
    top_n: int = 20,
    metric_key: str = 'cv_score'
) -> List[Dict[str, Any]]:
    """
    Identify top N performing configurations.
    
    Reuses extract_top_results() from framework when possible to follow DRY principles.
    Falls back to local implementation if framework function not available.
    
    Args:
        combined_data: Combined metadata and results (list of dicts with hyperparameters and cv_score)
        top_n: Number of top performers to return
        metric_key: Key to use for sorting (default: 'cv_score')
        
    Returns:
        List of top N configurations sorted by metric (descending)
    """
    # Try to use framework function if available and data format matches
    if extract_top_results is not None:
        try:
            # Framework function expects results with metric_key directly accessible
            # Our combined_data has cv_score, so we can use it directly
            return extract_top_results(combined_data, top_n=top_n, metric_key=metric_key)
        except (KeyError, AttributeError, TypeError):
            # Data format doesn't match, fall back to local implementation
            logger.debug("Framework extract_top_results() format mismatch, using local implementation")
    
    # Local implementation (fallback or when framework function not available)
    valid_data = [
        r for r in combined_data
        if r.get(metric_key) is not None
        and not (isinstance(r.get(metric_key), float) and (r[metric_key] != r[metric_key]))
    ]
    
    if not valid_data:
        logger.warning(f"No valid results found with {metric_key}")
        return []
    
    # Sort by metric (descending)
    sorted_data = sorted(
        valid_data,
        key=lambda x: x.get(metric_key, -float('inf')),
        reverse=True
    )
    
    top_results = sorted_data[:top_n]
    logger.info(f"Identified top {len(top_results)} performers (from {len(valid_data)} valid)")
    return top_results


def calculate_parameter_statistics(
    combined_data: List[Dict[str, Any]],
    param_name: str
) -> Dict[str, Any]:
    """
    Calculate statistics for a specific hyperparameter.
    
    Args:
        combined_data: Combined metadata and results
        param_name: Name of hyperparameter to analyze
        
    Returns:
        Dictionary with statistics including value groups, counts, means, etc.
    """
    # Extract parameter values and scores
    param_scores = []
    for record in combined_data:
        param_value = record.get('hyperparameters', {}).get(param_name)
        cv_score = record.get('cv_score')
        
        if param_value is not None and cv_score is not None:
            # Handle NaN scores
            if isinstance(cv_score, float) and (cv_score != cv_score):
                continue
            param_scores.append((param_value, cv_score))
    
    if not param_scores:
        return {'error': f'No valid data for {param_name}'}
    
    # Group by parameter value
    value_groups = defaultdict(list)
    for param_value, score in param_scores:
        value_groups[param_value].append(score)
    
    # Calculate statistics per value
    value_stats = {}
    for value, scores in value_groups.items():
        value_stats[value] = {
            'count': len(scores),
            'mean': statistics.mean(scores),
            'median': statistics.median(scores),
            'std': statistics.stdev(scores) if len(scores) > 1 else 0.0,
            'min': min(scores),
            'max': max(scores)
        }
    
    # Calculate overall correlation (if numeric)
    param_values = [pv for pv, _ in param_scores]
    scores = [s for _, s in param_scores]
    
    try:
        # Check if parameter is numeric
        numeric_values = [float(v) for v in param_values]
        # Simple correlation calculation
        if len(set(numeric_values)) > 1:
            correlation = _calculate_correlation(numeric_values, scores)
        else:
            correlation = None
    except (ValueError, TypeError):
        correlation = None
    
    # Overall statistics
    all_scores = [s for _, s in param_scores]
    
    return {
        'parameter': param_name,
        'unique_values': len(value_stats),
        'total_records': len(param_scores),
        'value_statistics': value_stats,
        'correlation': correlation,
        'overall_score_stats': {
            'mean': statistics.mean(all_scores),
            'median': statistics.median(all_scores),
            'std': statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0,
            'min': min(all_scores),
            'max': max(all_scores)
        }
    }


def _calculate_correlation(x: List[float], y: List[float]) -> float:
    """
    Calculate Pearson correlation coefficient.
    
    Args:
        x: First variable
        y: Second variable
        
    Returns:
        Correlation coefficient
    """
    n = len(x)
    if n < 2:
        return 0.0
    
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
    sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))
    
    denominator = (sum_sq_x * sum_sq_y) ** 0.5
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def analyze_parameter_trends(
    combined_data: List[Dict[str, Any]],
    param_name: str
) -> Dict[str, Any]:
    """
    Analyze trends in parameter values vs scores.
    
    Args:
        combined_data: Combined metadata and results
        param_name: Name of hyperparameter to analyze
        
    Returns:
        Dictionary with trend analysis
    """
    # Extract parameter values and scores
    param_scores = []
    for record in combined_data:
        param_value = record.get('hyperparameters', {}).get(param_name)
        cv_score = record.get('cv_score')
        
        if param_value is not None and cv_score is not None:
            if isinstance(cv_score, float) and (cv_score != cv_score):
                continue
            param_scores.append((param_value, cv_score))
    
    if not param_scores:
        return {'error': f'No valid data for {param_name}'}
    
    # Check if numeric
    try:
        numeric_values = [float(v) for v, _ in param_scores]
        is_numeric = True
    except (ValueError, TypeError):
        is_numeric = False
        numeric_values = None
    
    if is_numeric:
        # Sort by parameter value
        sorted_data = sorted(param_scores, key=lambda x: float(x[0]))
        
        # Calculate trend: compare scores at low vs high parameter values
        low_third = sorted_data[:len(sorted_data)//3]
        high_third = sorted_data[-len(sorted_data)//3:]
        
        low_scores = [s for _, s in low_third]
        high_scores = [s for _, s in high_third]
        
        low_mean = statistics.mean(low_scores)
        high_mean = statistics.mean(high_scores)
        
        trend = 'increasing' if high_mean > low_mean else 'decreasing' if high_mean < low_mean else 'stable'
        trend_strength = abs(high_mean - low_mean) / (statistics.stdev([low_mean, high_mean]) + 1e-10)
        
        return {
            'parameter': param_name,
            'is_numeric': True,
            'trend': trend,
            'trend_strength': trend_strength,
            'low_value_mean_score': low_mean,
            'high_value_mean_score': high_mean,
            'low_value_range': (float(sorted_data[0][0]), float(sorted_data[len(sorted_data)//3-1][0])),
            'high_value_range': (float(sorted_data[-len(sorted_data)//3][0]), float(sorted_data[-1][0]))
        }
    else:
        # Categorical: rank by mean score
        value_groups = defaultdict(list)
        for param_value, score in param_scores:
            value_groups[param_value].append(score)
        
        value_means = {
            value: statistics.mean(scores)
            for value, scores in value_groups.items()
        }
        
        sorted_values = sorted(value_means.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'parameter': param_name,
            'is_numeric': False,
            'value_ranking': sorted_values,
            'best_value': sorted_values[0][0] if sorted_values else None,
            'best_value_mean_score': sorted_values[0][1] if sorted_values else None
        }


def _get_top_performers_from_data(
    combined_data: List[Dict[str, Any]],
    top_percentile: float
) -> List[Dict[str, Any]]:
    """Extract and sort top performers from combined data."""
    valid_data = [
        r for r in combined_data
        if r.get('cv_score') is not None
        and not (isinstance(r.get('cv_score'), float) and (r['cv_score'] != r['cv_score']))
    ]
    
    sorted_data = sorted(
        valid_data,
        key=lambda x: x.get('cv_score', -float('inf')),
        reverse=True
    )
    
    top_n = max(1, int(len(sorted_data) * top_percentile))
    return sorted_data[:top_n]


def _extract_parameter_values(
    top_performers: List[Dict[str, Any]],
    param_name: str
) -> List[Any]:
    """Extract parameter values from top performers."""
    param_values = []
    for record in top_performers:
        value = record.get('hyperparameters', {}).get(param_name)
        if value is not None:
            param_values.append(value)
    return param_values


def _generate_numeric_recommendations(
    numeric_values: List[float],
    expansion_factor: float,
    tested_values: set
) -> List[float]:
    """Generate focused recommendations for numeric parameters."""
    min_val = min(numeric_values)
    max_val = max(numeric_values)
    
    # Expand range
    range_size = max_val - min_val
    if range_size == 0:
        # All values same, create small range
        center = min_val
        expanded_min = center / expansion_factor
        expanded_max = center * expansion_factor
    else:
        center = (min_val + max_val) / 2
        half_range = (range_size / 2) * expansion_factor
        expanded_min = max(0, center - half_range)
        expanded_max = center + half_range
    
    # Generate focused values
    focused_values = set(numeric_values)  # Include original top values
    
    # Add expanded boundaries
    if expanded_min < min_val:
        focused_values.add(expanded_min)
    if expanded_max > max_val:
        focused_values.add(expanded_max)
    
    # Convert to sorted list and filter tested values
    focused_list = sorted(list(focused_values))
    return [v for v in focused_list if v not in tested_values]


def _generate_categorical_recommendations(
    param_values: List[Any],
    tested_values: set
) -> List[Any]:
    """Generate focused recommendations for categorical parameters."""
    unique_values = sorted(list(set(param_values)))
    return [v for v in unique_values if v not in tested]


def generate_focused_grid_recommendations(
    combined_data: List[Dict[str, Any]],
    tested_values: Dict[str, List[Any]],
    model_type: str = 'lgbm',
    top_percentile: float = 0.1,
    expansion_factor: float = 1.2
) -> Dict[str, List[Any]]:
    """
    Generate focused grid search recommendations based on top performers.
    Automatically excludes already-tested values.
    
    This is more sophisticated than analyze_results_for_focused_grid() as it:
    - Uses percentile-based top performer selection
    - Automatically excludes tested values
    - Provides more detailed value generation
    
    Args:
        combined_data: Combined metadata and results
        tested_values: Dictionary of tested parameter values to exclude
        model_type: Type of model ('lgbm', 'xgboost', 'ridge')
        top_percentile: Top percentile to analyze (0.1 = top 10%)
        expansion_factor: Factor to expand ranges around top values
        
    Returns:
        Dictionary mapping parameter names to recommended value lists (only NEW values)
    """
    # Get top performers
    top_performers = _get_top_performers_from_data(combined_data, top_percentile)
    top_n = len(top_performers)
    
    recommendations = {}
    param_names = get_hyperparameters_for_model(model_type)
    
    for param_name in param_names:
        # Extract parameter values
        param_values = _extract_parameter_values(top_performers, param_name)
        if not param_values:
            continue
        
        # Check if numeric
        try:
            numeric_values = [float(v) for v in param_values]
            is_numeric = True
        except (ValueError, TypeError):
            is_numeric = False
        
        tested = set(tested_values.get(param_name, []))
        
        if is_numeric:
            new_values = _generate_numeric_recommendations(
                numeric_values, expansion_factor, tested
            )
        else:
            new_values = _generate_categorical_recommendations(param_values, tested)
        
        if new_values:
            recommendations[param_name] = new_values
    
    logger.info(
        f"Generated recommendations for {len(recommendations)} parameters "
        f"(based on top {top_n} performers, {top_percentile*100:.1f}%)"
    )
    
    return recommendations
