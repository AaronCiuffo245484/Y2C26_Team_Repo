"""
RSML Annotation Comparison Tool

Compares root annotations between multiple annotators to assess inter-rater reliability.
Generates a markdown report with statistics, visualizations, and ICC calculations.

Usage:
    python annotation_comparison.py <annotation_dir> <image_dir> <output_dir>

Arguments:
    annotation_dir: Directory containing annotator subdirectories with RSML files
    image_dir: Directory containing source PNG images (will search recursively)
    output_dir: Directory to save reports and visualizations

Author: Aaron 
Date: February 2026
"""

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
import cv2
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.stats import f as f_dist


# ==================== RSML LOADING ====================

def load_single_rsml(rsml_path):
    """Load a single RSML file and extract basic root information."""
    rsml_path = Path(rsml_path)
    tree = ET.parse(rsml_path)
    root_elem = tree.getroot()
    
    results = []
    
    for root in root_elem.findall('.//root'):
        root_id = root.get('ID')
        label = root.get('label')
        
        length_elem = root.find('.//properties/length')
        length_cm = float(length_elem.text) if length_elem is not None else None
        length_mm = length_cm * 10 if length_cm is not None else None
        
        points = []
        polyline = root.find('.//geometry/polyline')
        if polyline is not None:
            for point in polyline.findall('point'):
                x = float(point.get('x'))
                y = float(point.get('y'))
                points.append((x, y))
        
        start_x, start_y = points[0] if points else (None, None)
        end_x, end_y = points[-1] if points else (None, None)
        
        results.append({
            'root_id': root_id,
            'label': label,
            'length_cm': length_cm,
            'length_mm': length_mm,
            'num_points': len(points),
            'start_x': start_x,
            'start_y': start_y,
            'end_x': end_x,
            'end_y': end_y,
            'points': points
        })
    
    return pd.DataFrame(results)


# ==================== IMAGE SEARCH ====================

def find_image_for_rsml(rsml_filename, image_search_dir):
    """
    Recursively search for PNG image matching RSML filename.
    
    Parameters:
    -----------
    rsml_filename : str
        Name of RSML file (e.g., 'inv_28_07_02.rsml')
    image_search_dir : Path
        Top-level directory to search for images
    
    Returns:
    --------
    Path to matching image or None if not found
    """
    png_filename = rsml_filename.replace('.rsml', '.png')
    
    # Search recursively for the image
    for img_path in Path(image_search_dir).rglob(png_filename):
        return img_path
    
    return None


# ==================== MASK GENERATION ====================

def extract_root_with_diameter(root_element):
    """Extract polyline points and diameter values from a root element."""
    root_id = root_element.get('ID')
    label = root_element.get('label')
    
    points = []
    polyline = root_element.find('.//geometry/polyline')
    if polyline is not None:
        for point in polyline.findall('point'):
            x = float(point.get('x'))
            y = float(point.get('y'))
            points.append((x, y))
    
    diameters = []
    diameter_func = root_element.find(".//function[@name='diameter']")
    if diameter_func is not None:
        for sample in diameter_func.findall('sample'):
            diameters.append(float(sample.text))
    
    return {
        'root_id': root_id,
        'label': label,
        'points': points,
        'diameters': diameters
    }


def get_image_dimensions(rsml_path, image_search_dir=None):
    """Get image dimensions by loading the corresponding PNG file."""
    rsml_path = Path(rsml_path)
    
    if image_search_dir is not None:
        image_path = find_image_for_rsml(rsml_path.name, image_search_dir)
        if image_path is None:
            return None
    else:
        image_path = rsml_path.with_suffix('.png')
    
    if not image_path.exists():
        return None
    
    img = Image.open(image_path)
    width, height = img.size
    return height, width


def create_root_mask(points, diameters, img_shape, line_thickness=2):
    """Create a binary mask from polyline points."""
    mask = np.zeros(img_shape, dtype=np.uint8)
    
    if len(points) < 2:
        return mask
    
    pts = np.array(points, dtype=np.int32)
    cv2.polylines(mask, [pts], False, 255, thickness=line_thickness)
    
    return mask


def create_masks_from_rsml(rsml_path, line_thickness=2, image_search_dir=None):
    """Create binary masks from RSML file."""
    rsml_path = Path(rsml_path)
    
    img_shape = get_image_dimensions(rsml_path, image_search_dir=image_search_dir)
    if img_shape is None:
        raise ValueError(f"Cannot find corresponding image file for {rsml_path}")
    
    tree = ET.parse(rsml_path)
    root_elem = tree.getroot()
    
    individual_masks = {}
    combined_mask = np.zeros(img_shape, dtype=np.uint8)
    
    for root in root_elem.findall('.//root'):
        root_data = extract_root_with_diameter(root)
        label = root_data['label']
        
        mask = create_root_mask(
            root_data['points'], 
            root_data['diameters'], 
            img_shape,
            line_thickness
        )
        
        individual_masks[label] = mask
        combined_mask = cv2.bitwise_or(combined_mask, mask)
    
    return {
        'individual_masks': individual_masks,
        'combined_mask': combined_mask,
        'img_shape': img_shape
    }


# ==================== BATCH LOADING ====================

def load_all_annotators_with_masks(parent_dir, image_search_dir, line_thickness=2):
    """Load RSML data from all annotator subdirectories and generate masks."""
    parent_dir = Path(parent_dir)
    image_search_dir = Path(image_search_dir)
    
    all_data = []
    subdirs = sorted([d for d in parent_dir.iterdir() if d.is_dir()])
    
    print(f"Found {len(subdirs)} annotator directories")
    
    for subdir in subdirs:
        annotator_id = subdir.name.split('_')[0]
        rsml_files = sorted(subdir.glob('*.rsml'))
        
        print(f"  Loading {annotator_id}: {len(rsml_files)} files...", end=" ")
        
        for rsml_file in rsml_files:
            df = load_single_rsml(rsml_file)
            df['annotator'] = annotator_id
            df['filename'] = rsml_file.name
            
            try:
                masks = create_masks_from_rsml(rsml_file, line_thickness=line_thickness, 
                                              image_search_dir=image_search_dir)
                
                mask_list = []
                for idx, row in df.iterrows():
                    label = row['label']
                    if label in masks['individual_masks']:
                        mask_list.append(masks['individual_masks'][label])
                    else:
                        mask_list.append(None)
                
                df['mask'] = mask_list
                        
            except Exception as e:
                df['mask'] = None
            
            all_data.append(df)
        
        print("OK")
    
    combined = pd.concat(all_data, ignore_index=True)
    
    cols = ['annotator', 'filename', 'label', 'length_mm', 'num_points',
            'start_x', 'start_y', 'end_x', 'end_y',
            'length_cm', 'root_id', 'points']
    
    if 'mask' in combined.columns:
        cols.append('mask')
    
    combined = combined[cols]
    
    print(f"\nTotal: {len(combined)} roots from {combined['annotator'].nunique()} annotators")
    
    return combined


# ==================== FILTERING ====================

def filter_primary_roots(df):
    """Filter dataframe to only primary roots (root_01 through root_05)."""
    valid_labels = ['root_01', 'root_02', 'root_03', 'root_04', 'root_05']
    return df[df['label'].isin(valid_labels)].copy()


# ==================== VALIDATION ====================

def check_primary_root_completeness(df):
    """Check if all 5 primary roots are present for each file/annotator."""
    expected_labels = ['root_01', 'root_02', 'root_03', 'root_04', 'root_05']
    problems = []
    
    df_primary = filter_primary_roots(df)
    
    for filename in df_primary['filename'].unique():
        file_data = df_primary[df_primary['filename'] == filename]
        
        for annotator in file_data['annotator'].unique():
            ann_data = file_data[file_data['annotator'] == annotator]
            present_labels = set(ann_data['label'].tolist())
            missing_labels = [l for l in expected_labels if l not in present_labels]
            
            if missing_labels:
                problems.append({
                    'annotator': annotator,
                    'filename': filename,
                    'missing': missing_labels,
                    'present': sorted(present_labels)
                })
    
    return pd.DataFrame(problems)


# ==================== METRICS ====================

def calculate_mask_metrics(mask_a, mask_b):
    """Calculate Dice coefficient and IoU between two masks."""
    if mask_a is None or mask_b is None:
        return {'dice': None, 'iou': None}
    
    intersection = np.logical_and(mask_a > 0, mask_b > 0).sum()
    union = np.logical_or(mask_a > 0, mask_b > 0).sum()
    sum_areas = (mask_a > 0).sum() + (mask_b > 0).sum()
    
    iou = intersection / union if union > 0 else 0
    dice = (2 * intersection) / sum_areas if sum_areas > 0 else 0
    
    return {'dice': dice, 'iou': iou}


def calculate_smape(actual, predicted):
    """Calculate Symmetric Mean Absolute Percentage Error."""
    numerator = abs(actual - predicted)
    denominator = (abs(actual) + abs(predicted)) / 2
    
    if denominator == 0:
        return 0
    
    return float(100 * numerator / denominator)


# ==================== COMPARISON ====================

def compare_primary_roots_with_smape(df):
    """Compare primary roots with SMAPE, Dice, and IoU metrics."""
    df_primary = filter_primary_roots(df)
    
    comparisons = []
    
    for filename in df_primary['filename'].unique():
        file_data = df_primary[df_primary['filename'] == filename]
        annotators = sorted(file_data['annotator'].unique())
        
        for i, ann_a in enumerate(annotators):
            for ann_b in annotators[i+1:]:
                data_a = file_data[file_data['annotator'] == ann_a].set_index('label')
                data_b = file_data[file_data['annotator'] == ann_b].set_index('label')
                
                common_labels = set(data_a.index) & set(data_b.index)
                
                for label in sorted(common_labels):
                    length_a = data_a.loc[label, 'length_mm']
                    length_b = data_b.loc[label, 'length_mm']
                    mask_a = data_a.loc[label, 'mask'] if 'mask' in data_a.columns else None
                    mask_b = data_b.loc[label, 'mask'] if 'mask' in data_b.columns else None
                    
                    diff = length_a - length_b
                    abs_diff = abs(diff)
                    pct_diff = 100 * diff / length_b if length_b != 0 else None
                    smape = calculate_smape(length_a, length_b)
                    
                    mask_metrics = calculate_mask_metrics(mask_a, mask_b)
                    
                    comparisons.append({
                        'filename': filename,
                        'label': label,
                        'annotator_a': ann_a,
                        'annotator_b': ann_b,
                        'length_a': length_a,
                        'length_b': length_b,
                        'diff': diff,
                        'abs_diff': abs_diff,
                        'pct_diff': pct_diff,
                        'smape': smape,
                        'dice': mask_metrics['dice'],
                        'iou': mask_metrics['iou']
                    })
    
    return pd.DataFrame(comparisons)


# ==================== ICC CALCULATION ====================

def calculate_icc(df):
    """Calculate Intraclass Correlation Coefficient (ICC) for inter-annotator reliability."""
    df_primary = filter_primary_roots(df)
    
    pivot_data = df_primary.pivot_table(
        index=['filename', 'label'],
        columns='annotator',
        values='length_mm',
        aggfunc='first'
    )
    
    pivot_data_complete = pivot_data.dropna()
    
    if len(pivot_data_complete) == 0:
        print("No items with complete annotations from all annotators")
        return None
    
    print(f"ICC calculated on {len(pivot_data_complete)} items with complete annotations")
    
    ratings = pivot_data_complete.values
    
    n_items = ratings.shape[0]
    n_raters = ratings.shape[1]
    
    grand_mean = np.mean(ratings)
    
    item_means = np.mean(ratings, axis=1)
    ss_items = n_raters * np.sum((item_means - grand_mean) ** 2)
    
    rater_means = np.mean(ratings, axis=0)
    ss_raters = n_items * np.sum((rater_means - grand_mean) ** 2)
    
    ss_total = np.sum((ratings - grand_mean) ** 2)
    ss_error = ss_total - ss_items - ss_raters
    
    df_items = n_items - 1
    df_raters = n_raters - 1
    df_error = df_items * df_raters
    
    ms_items = ss_items / df_items
    ms_raters = ss_raters / df_raters
    ms_error = ss_error / df_error
    
    icc = (ms_items - ms_error) / (ms_items + (n_raters - 1) * ms_error + 
                                    n_raters * (ms_raters - ms_error) / n_items)
    
    f_items = ms_items / ms_error
    
    f_lower = f_dist.ppf(0.025, df_items, df_error)
    f_upper = f_dist.ppf(0.975, df_items, df_error)
    
    icc_lower = (f_items / f_upper - 1) / (f_items / f_upper + n_raters - 1)
    icc_upper = (f_items / f_lower - 1) / (f_items / f_lower + n_raters - 1)
    
    if icc < 0.5:
        interpretation = "Poor reliability"
    elif icc < 0.75:
        interpretation = "Moderate reliability"
    elif icc < 0.9:
        interpretation = "Good reliability"
    else:
        interpretation = "Excellent reliability"
    
    results = {
        'icc': icc,
        'icc_lower_95': max(0, icc_lower),
        'icc_upper_95': min(1, icc_upper),
        'n_items': n_items,
        'n_raters': n_raters,
        'interpretation': interpretation
    }
    
    return results


# ==================== VISUALIZATION ====================

def generate_problem_case_visualizations(df, comparisons_df, image_search_dir, output_dir, n_cases=5):
    """Generate visualizations for the worst annotation disagreements."""
    image_search_dir = Path(image_search_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    figures = {}
    
    worst_dice = comparisons_df.nsmallest(n_cases, 'dice')
    
    for i, (idx, row) in enumerate(worst_dice.iterrows(), 1):
        try:
            df_primary = filter_primary_roots(df)
            file_data = df_primary[df_primary['filename'] == row['filename']]
            
            data_a = file_data[file_data['annotator'] == row['annotator_a']]
            data_a = data_a[data_a['label'] == row['label']]
            
            data_b = file_data[file_data['annotator'] == row['annotator_b']]
            data_b = data_b[data_b['label'] == row['label']]
            
            if len(data_a) == 0 or len(data_b) == 0:
                continue
            
            mask_a = data_a.iloc[0]['mask']
            mask_b = data_b.iloc[0]['mask']
            
            if mask_a is None or mask_b is None:
                continue
            
            img_path = find_image_for_rsml(row['filename'], image_search_dir)
            if img_path is None or not img_path.exists():
                continue
                
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            
            if img is None:
                continue
            
            combined_mask = cv2.bitwise_or(mask_a, mask_b)
            coords = np.column_stack(np.where(combined_mask > 0))
            
            if len(coords) == 0:
                continue
            
            padding = 100
            min_y, min_x = coords.min(axis=0)
            max_y, max_x = coords.max(axis=0)
            
            min_y = max(0, min_y - padding)
            max_y = min(img.shape[0], max_y + padding)
            min_x = max(0, min_x - padding)
            max_x = min(img.shape[1], max_x + padding)
            
            img_crop = img[min_y:max_y, min_x:max_x]
            mask_a_crop = mask_a[min_y:max_y, min_x:max_x]
            mask_b_crop = mask_b[min_y:max_y, min_x:max_x]
            
            fig, axes = plt.subplots(2, 2, figsize=(14, 14))
            
            axes[0, 0].imshow(img, cmap='gray')
            rect = Rectangle((min_x, min_y), max_x-min_x, max_y-min_y, 
                             linewidth=2, edgecolor='red', facecolor='none')
            axes[0, 0].add_patch(rect)
            axes[0, 0].set_title('Full Image', fontsize=12)
            axes[0, 0].axis('off')
            
            axes[0, 1].imshow(img_crop, cmap='gray', alpha=0.5)
            axes[0, 1].imshow(mask_a_crop, cmap='Reds', alpha=0.7)
            axes[0, 1].set_title(f'{row["annotator_a"]}: {row["label"]}\nLength: {row["length_a"]:.2f} mm', fontsize=12)
            axes[0, 1].axis('off')
            
            axes[1, 0].imshow(img_crop, cmap='gray', alpha=0.5)
            axes[1, 0].imshow(mask_b_crop, cmap='Blues', alpha=0.7)
            axes[1, 0].set_title(f'{row["annotator_b"]}: {row["label"]}\nLength: {row["length_b"]:.2f} mm', fontsize=12)
            axes[1, 0].axis('off')
            
            overlay = np.zeros((*img_crop.shape, 3), dtype=np.uint8)
            overlay[img_crop > 0] = [50, 50, 50]
            
            only_a = (mask_a_crop > 0) & (mask_b_crop == 0)
            only_b = (mask_b_crop > 0) & (mask_a_crop == 0)
            both = (mask_a_crop > 0) & (mask_b_crop > 0)
            
            overlay[only_a] = [255, 0, 0]
            overlay[only_b] = [0, 0, 255]
            overlay[both] = [255, 0, 255]
            
            axes[1, 1].imshow(overlay)
            axes[1, 1].set_title(f'Overlay\nDice: {row["dice"]:.3f}, IoU: {row["iou"]:.3f}\nRed={row["annotator_a"]}, Blue={row["annotator_b"]}, Purple=Both', 
                                 fontsize=11)
            axes[1, 1].axis('off')
            
            plt.suptitle(f'{row["filename"]} - {row["label"]}', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            filename = f'problem_{i:02d}_{row["filename"].replace(".rsml", "")}_{row["label"]}.png'
            fig_path = output_dir / filename
            fig.savefig(fig_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            figures[f'problem_{i}'] = fig_path
            
        except Exception as e:
            continue
    
    print(f"Generated {len(figures)} problem case visualizations")
    
    return figures


# ==================== EXPORT ====================

def export_comparisons_to_csv(comparisons_df, output_path):
    """Export comparison data to CSV."""
    export_df = comparisons_df.copy()
    
    cols_to_drop = [col for col in export_df.columns if 'mask' in col.lower()]
    if cols_to_drop:
        export_df = export_df.drop(columns=cols_to_drop)
    
    export_df.to_csv(output_path, index=False)
    
    print(f"Exported {len(export_df)} comparisons to: {output_path}")
    
    return output_path


def export_full_data_to_csv(df, output_path):
    """Export full annotation data to CSV."""
    export_df = df.copy()
    
    cols_to_drop = [col for col in export_df.columns if col in ['mask', 'points']]
    if cols_to_drop:
        export_df = export_df.drop(columns=cols_to_drop)
    
    export_df.to_csv(output_path, index=False)
    
    print(f"Exported {len(export_df)} annotations to: {output_path}")
    
    return output_path


# ==================== REPORT GENERATION ====================

def generate_markdown_report(df, comparisons_df, icc_results, image_search_dir, output_path, output_image_dir):
    """Generate comprehensive Markdown report with ICC and visualizations."""
    image_search_dir = Path(image_search_dir)
    output_image_dir = Path(output_image_dir)
    
    problem_figures = generate_problem_case_visualizations(
        df, comparisons_df, image_search_dir, output_image_dir, n_cases=5
    )
    
    report = []
    
    report.append("# Annotation Quality Report")
    report.append("")
    
    report.append("## Dataset Overview")
    report.append("")
    report.append(f"- **Total annotations**: {len(df)}")
    report.append(f"- **Annotators**: {', '.join(sorted(df['annotator'].unique()))}")
    report.append(f"- **Files annotated**: {df['filename'].nunique()}")
    report.append("")
    
    report.append("### Files per Annotator")
    report.append("")
    for annotator in sorted(df['annotator'].unique()):
        count = df[df['annotator'] == annotator]['filename'].nunique()
        report.append(f"- **{annotator}**: {count} files")
    report.append("")
    
    df_primary = filter_primary_roots(df)
    report.append(f"- **Primary roots** (root_01 to root_05): {len(df_primary)}")
    report.append(f"- **Auxiliary/lateral roots**: {len(df) - len(df_primary)}")
    report.append("")
    
    report.append("## Validation Issues")
    report.append("")
    
    missing = check_primary_root_completeness(df)
    report.append(f"**Files missing primary roots**: {len(missing)}")
    report.append("")
    if len(missing) > 0:
        for _, row in missing.iterrows():
            report.append(f"- **{row['annotator']}**: `{row['filename']}`")
            report.append(f"  - Missing: {row['missing']}")
            report.append(f"  - Present: {row['present']}")
    else:
        report.append("*None - all files have complete primary roots!*")
    report.append("")
    
    report.append("## Inter-Annotator Agreement")
    report.append("")
    report.append(f"**Total pairwise comparisons**: {len(comparisons_df)}")
    report.append("")
    
    report.append("### Intraclass Correlation Coefficient (ICC)")
    report.append("")
    if icc_results is not None:
        report.append(f"**Model**: ICC(2,1) - Two-way random effects, absolute agreement")
        report.append("")
        report.append("| Metric | Value |")
        report.append("|--------|-------|")
        report.append(f"| ICC | {icc_results['icc']:.3f} |")
        report.append(f"| 95% CI | [{icc_results['icc_lower_95']:.3f}, {icc_results['icc_upper_95']:.3f}] |")
        report.append(f"| Interpretation | {icc_results['interpretation']} |")
        report.append(f"| Items (measurements) | {icc_results['n_items']} |")
        report.append(f"| Raters (annotators) | {icc_results['n_raters']} |")
        report.append("")
        report.append("**Guidelines** (Koo & Li, 2016):")
        report.append("- < 0.50: Poor reliability")
        report.append("- 0.50-0.75: Moderate reliability")
        report.append("- 0.75-0.90: Good reliability")
        report.append("- > 0.90: Excellent reliability")
        report.append("")
    else:
        report.append("*Could not calculate ICC - insufficient complete annotations*")
        report.append("")
    
    report.append("### Length Measurements")
    report.append("")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    report.append(f"| Mean absolute difference | {comparisons_df['abs_diff'].mean():.3f} mm |")
    report.append(f"| Median absolute difference | {comparisons_df['abs_diff'].median():.3f} mm |")
    report.append(f"| Std deviation | {comparisons_df['abs_diff'].std():.3f} mm |")
    report.append(f"| Max difference | {comparisons_df['abs_diff'].max():.3f} mm |")
    report.append(f"| Min difference | {comparisons_df['abs_diff'].min():.3f} mm |")
    report.append("")
    
    if 'smape' in comparisons_df.columns:
        report.append("### SMAPE (Kaggle Competition Metric)")
        report.append("")
        report.append("| Metric | Value |")
        report.append("|--------|-------|")
        report.append(f"| Mean SMAPE | {comparisons_df['smape'].mean():.3f} |")
        report.append(f"| Median SMAPE | {comparisons_df['smape'].median():.3f} |")
        report.append(f"| Std SMAPE | {comparisons_df['smape'].std():.3f} |")
        report.append("")
        report.append(f"*Reference: Kaggle baseline SMAPE was 8.285*")
        report.append("")
    
    report.append("### Spatial Overlap (Masks)")
    report.append("")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    report.append(f"| Mean Dice coefficient | {comparisons_df['dice'].mean():.3f} |")
    report.append(f"| Median Dice coefficient | {comparisons_df['dice'].median():.3f} |")
    report.append(f"| Mean IoU | {comparisons_df['iou'].mean():.3f} |")
    report.append(f"| Median IoU | {comparisons_df['iou'].median():.3f} |")
    report.append("")
    
    report.append("### By Annotator Pair")
    report.append("")
    
    cols_to_agg = ['abs_diff', 'dice', 'iou']
    if 'smape' in comparisons_df.columns:
        cols_to_agg.append('smape')
    
    grouped = comparisons_df.groupby(['annotator_a', 'annotator_b']).agg({
        col: ['count', 'mean', 'std'] for col in cols_to_agg
    }).round(3)
    
    for (ann_a, ann_b), row in grouped.iterrows():
        report.append(f"#### {ann_a} vs {ann_b}")
        report.append("")
        report.append(f"- **Comparisons**: {int(row[(cols_to_agg[0], 'count')])}")
        report.append(f"- **Length difference**: {row[('abs_diff', 'mean')]:.3f} +/- {row[('abs_diff', 'std')]:.3f} mm")
        if 'smape' in comparisons_df.columns:
            report.append(f"- **SMAPE**: {row[('smape', 'mean')]:.3f} +/- {row[('smape', 'std')]:.3f}")
        report.append(f"- **Dice coefficient**: {row[('dice', 'mean')]:.3f} +/- {row[('dice', 'std')]:.3f}")
        report.append(f"- **IoU**: {row[('iou', 'mean')]:.3f} +/- {row[('iou', 'std')]:.3f}")
        report.append("")
    
    report.append("## Cases Requiring Review")
    report.append("")
    report.append("The following cases show the worst spatial disagreements (lowest Dice coefficients).")
    report.append("")
    
    worst_dice = comparisons_df.nsmallest(5, 'dice')
    for i, (_, row) in enumerate(worst_dice.iterrows(), 1):
        report.append(f"### Problem Case {i}")
        report.append("")
        report.append(f"**File**: `{row['filename']}` | **Root**: {row['label']} | **Annotators**: {row['annotator_a']} vs {row['annotator_b']}")
        report.append("")
        report.append("| Metric | Value |")
        report.append("|--------|-------|")
        report.append(f"| {row['annotator_a']} length | {row['length_a']:.2f} mm |")
        report.append(f"| {row['annotator_b']} length | {row['length_b']:.2f} mm |")
        report.append(f"| Length difference | {row['abs_diff']:.3f} mm ({row['pct_diff']:.1f}%) |")
        report.append(f"| Dice coefficient | {row['dice']:.3f} |")
        report.append(f"| IoU | {row['iou']:.3f} |")
        if 'smape' in row and not pd.isna(row['smape']):
            report.append(f"| SMAPE | {row['smape']:.3f} |")
        report.append("")
        
        if f'problem_{i}' in problem_figures:
            rel_path = problem_figures[f'problem_{i}'].relative_to(Path(output_path).parent)
            report.append(f"![Problem Case {i}]({rel_path})")
            report.append("")
    
    report_text = '\n'.join(report)
    
    with open(output_path, 'w') as f:
        f.write(report_text)
    
    print(f"\nMarkdown report saved to: {output_path}")
    
    return report_text


# ==================== MAIN ====================

def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) != 4:
        print("Usage: python annotation_comparison.py <annotation_dir> <image_dir> <output_dir>")
        print("")
        print("Arguments:")
        print("  annotation_dir: Directory containing annotator subdirectories with RSML files")
        print("  image_dir: Directory containing source PNG images (will search recursively)")
        print("  output_dir: Directory to save reports and visualizations")
        sys.exit(1)
    
    annotation_dir = Path(sys.argv[1])
    image_dir = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])
    
    if not annotation_dir.exists():
        print(f"Error: Annotation directory not found: {annotation_dir}")
        sys.exit(1)
    
    if not image_dir.exists():
        print(f"Error: Image directory not found: {image_dir}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print("RSML ANNOTATION COMPARISON TOOL")
    print("="*70)
    print(f"\nAnnotation directory: {annotation_dir}")
    print(f"Image directory: {image_dir}")
    print(f"Output directory: {output_dir}")
    print("")
    
    # Load all data
    print("Loading annotations...")
    df_all = load_all_annotators_with_masks(annotation_dir, image_dir)
    
    # Calculate comparisons
    print("\nCalculating pairwise comparisons...")
    comparisons = compare_primary_roots_with_smape(df_all)
    
    # Calculate ICC
    print("\nCalculating ICC...")
    icc_results = calculate_icc(df_all)
    
    # Export CSVs
    print("\nExporting data...")
    export_comparisons_to_csv(comparisons, output_dir / 'annotation_comparisons.csv')
    export_full_data_to_csv(filter_primary_roots(df_all), output_dir / 'primary_roots_data.csv')
    
    # Generate report
    print("\nGenerating markdown report...")
    generate_markdown_report(
        df_all,
        comparisons,
        icc_results,
        image_dir,
        output_dir / 'annotation_report.md',
        output_dir / 'problem_cases'
    )
    
    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)
    print(f"\nOutputs:")
    print(f"  - {output_dir / 'annotation_report.md'}")
    print(f"  - {output_dir / 'annotation_comparisons.csv'}")
    print(f"  - {output_dir / 'primary_roots_data.csv'}")
    print(f"  - {output_dir / 'problem_cases'}/ (visualizations)")
    print("")


if __name__ == '__main__':
    main()