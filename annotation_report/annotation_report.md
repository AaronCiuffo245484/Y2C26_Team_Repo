# Annotation Quality Report

## Introduction

The following report documents an inter-annotator agreement analysis conducted as part of the
exploratory data analysis (EDA) phase of this project. Its purpose is to establish a quantitative
baseline for annotation quality before model training begins, and to identify any systematic sources
of measurement error in the ground truth data.

Annotations were produced by five annotators (AH, LP, ac, ar, ym) using the SmartRoot plugin for
FIJI. Each annotator traced primary and lateral root structures from inverted plate images,
following standardized documentation developed by the team. The resulting traces were exported as
Root System Markup Language (RSML) files, from which root length measurements and binary
segmentation masks were derived programmatically.

A total of 970 annotations across 15 image files were collected. Agreement was assessed using four
complementary metrics: intraclass correlation coefficient (ICC) for overall reliability, mean
absolute length difference for measurement precision, Symmetric Mean Absolute Percentage Error
(SMAPE) for scale-normalized comparison, and Dice coefficient and Intersection over Union (IoU)
for spatial mask overlap.

### Source Code

Please note this EDA was created using `.py` scripts rather than a `.ipynb` to generate this report. All source for generating this notebook can be found in our [Team Repo](https://github.com/AaronCiuffo245484/Y2C26_Team_Repo/tree/feature/rsml_data/utilities)

## Summary of Findings

Inter-annotator agreement was high overall. ICC(2,1) under an absolute agreement model reached
0.996 (95% CI: [0.995, 0.998]), which exceeds the threshold for excellent reliability as defined
by Koo and Li (2016). Mean absolute length difference between annotator pairs was 0.597 mm
(median 0.396 mm), and mean SMAPE was 6.285, which is below the Kaggle competition baseline of
8.285 for this dataset.

Spatial overlap was moderate, with a mean Dice coefficient of 0.810 and mean IoU of 0.689. While
length measurements show strong agreement, the lower spatial overlap scores indicate that annotators
reach consistent length estimates through paths that do not always spatially coincide. This is a
known characteristic of polyline-based root tracing and represents an irreducible source of
variance in any mask-derived metric.

Validation identified two files with missing primary root labels, concentrated in a single image
(inv_28_07_02.rsml). The five worst-performing cases by Dice coefficient all originate from this
file, specifically root_03 and root_04, which are short roots (under 0.55 mm) where small
positional differences produce disproportionately large spatial disagreement. This highlights that
annotation variance is not uniformly distributed but is concentrated in structurally ambiguous,
short-root cases.

These results establish that the manual annotations are of sufficient quality to serve as ground
truth for model training. The residual variance quantified here provides an indicative ceiling on
the precision that automated methods can be expected to achieve: a model performing within the
inter-annotator range is performing at human level for this task.

## Dataset Overview

- **Total annotations**: 970
- **Annotators**: AH, LP, ac, ar, ym
- **Files annotated**: 15

### Files per Annotator

- **AH**: 14 files
- **LP**: 7 files
- **ac**: 14 files
- **ar**: 15 files
- **ym**: 15 files

- **Primary roots** (root_01 to root_05): 322
- **Auxiliary/lateral roots**: 648

## Validation Issues

**Files missing primary roots**: 2

- **ac**: `inv_28_07_02.rsml`
  - Missing: ['root_03', 'root_04']
  - Present: ['root_01', 'root_02', 'root_05']
- **AH**: `inv_28_07_02.rsml`
  - Missing: ['root_03']
  - Present: ['root_01', 'root_02', 'root_04', 'root_05']

## Inter-Annotator Agreement

**Total pairwise comparisons**: 554

### Intraclass Correlation Coefficient (ICC)

**Model**: ICC(2,1) - Two-way random effects, absolute agreement

| Metric | Value |
|--------|-------|
| ICC | 0.996 |
| 95% CI | [0.995, 0.998] |
| Interpretation | Excellent reliability |
| Items (measurements) | 33 |
| Raters (annotators) | 5 |

**Guidelines** (Koo & Li, 2016):
- < 0.50: Poor reliability
- 0.50-0.75: Moderate reliability
- 0.75-0.90: Good reliability
- > 0.90: Excellent reliability

### Length Measurements

| Metric | Value |
|--------|-------|
| Mean absolute difference | 0.597 mm |
| Median absolute difference | 0.396 mm |
| Std deviation | 0.559 mm |
| Max difference | 3.239 mm |
| Min difference | 0.001 mm |

### SMAPE (Kaggle Competition Metric)

| Metric | Value |
|--------|-------|
| Mean SMAPE | 6.285 |
| Median SMAPE | 2.522 |
| Std SMAPE | 13.263 |

*Reference: Kaggle baseline SMAPE was 8.285*

### Spatial Overlap (Masks)

| Metric | Value |
|--------|-------|
| Mean Dice coefficient | 0.810 |
| Median Dice coefficient | 0.827 |
| Mean IoU | 0.689 |
| Median IoU | 0.704 |

### By Annotator Pair

#### AH vs LP

- **Comparisons**: 34
- **Length difference**: 0.405 +/- 0.264 mm
- **SMAPE**: 7.789 +/- 12.015
- **Dice coefficient**: 0.802 +/- 0.150
- **IoU**: 0.686 +/- 0.140

#### AH vs ac

- **Comparisons**: 68
- **Length difference**: 0.604 +/- 0.444 mm
- **SMAPE**: 5.388 +/- 10.252
- **Dice coefficient**: 0.814 +/- 0.043
- **IoU**: 0.688 +/- 0.060

#### AH vs ar

- **Comparisons**: 69
- **Length difference**: 0.978 +/- 0.912 mm
- **SMAPE**: 6.229 +/- 8.059
- **Dice coefficient**: 0.835 +/- 0.050
- **IoU**: 0.719 +/- 0.069

#### AH vs ym

- **Comparisons**: 69
- **Length difference**: 0.615 +/- 0.506 mm
- **SMAPE**: 3.965 +/- 5.043
- **Dice coefficient**: 0.828 +/- 0.081
- **IoU**: 0.712 +/- 0.091

#### LP vs ac

- **Comparisons**: 33
- **Length difference**: 0.265 +/- 0.236 mm
- **SMAPE**: 4.063 +/- 5.678
- **Dice coefficient**: 0.810 +/- 0.036
- **IoU**: 0.682 +/- 0.050

#### LP vs ar

- **Comparisons**: 35
- **Length difference**: 0.733 +/- 0.617 mm
- **SMAPE**: 8.570 +/- 8.138
- **Dice coefficient**: 0.773 +/- 0.160
- **IoU**: 0.649 +/- 0.152

#### LP vs ym

- **Comparisons**: 35
- **Length difference**: 0.446 +/- 0.414 mm
- **SMAPE**: 8.891 +/- 18.327
- **Dice coefficient**: 0.772 +/- 0.168
- **IoU**: 0.649 +/- 0.155

#### ac vs ar

- **Comparisons**: 68
- **Length difference**: 0.707 +/- 0.580 mm
- **SMAPE**: 4.954 +/- 6.639
- **Dice coefficient**: 0.804 +/- 0.051
- **IoU**: 0.675 +/- 0.069

#### ac vs ym

- **Comparisons**: 68
- **Length difference**: 0.376 +/- 0.302 mm
- **SMAPE**: 3.986 +/- 8.388
- **Dice coefficient**: 0.816 +/- 0.040
- **IoU**: 0.691 +/- 0.055

#### ar vs ym

- **Comparisons**: 75
- **Length difference**: 0.562 +/- 0.423 mm
- **SMAPE**: 10.593 +/- 27.014
- **Dice coefficient**: 0.808 +/- 0.119
- **IoU**: 0.692 +/- 0.134

## Cases Requiring Review

The following cases show the worst spatial disagreements (lowest Dice coefficients).

### Problem Case 1

**File**: `inv_28_07_02.rsml` | **Root**: root_04 | **Annotators**: AH vs LP

| Metric | Value |
|--------|-------|
| AH length | 0.27 mm |
| LP length | 0.41 mm |
| Length difference | 0.143 mm (-34.7%) |
| Dice coefficient | 0.000 |
| IoU | 0.000 |
| SMAPE | 42.000 |

![Problem Case 1](problem_cases\problem_01_inv_28_07_02_root_04.png)

### Problem Case 2

**File**: `inv_28_07_02.rsml` | **Root**: root_04 | **Annotators**: LP vs ym

| Metric | Value |
|--------|-------|
| LP length | 0.41 mm |
| ym length | 0.37 mm |
| Length difference | 0.042 mm (11.4%) |
| Dice coefficient | 0.000 |
| IoU | 0.000 |
| SMAPE | 10.823 |

![Problem Case 2](problem_cases\problem_02_inv_28_07_02_root_04.png)

### Problem Case 3

**File**: `inv_28_07_02.rsml` | **Root**: root_04 | **Annotators**: LP vs ar

| Metric | Value |
|--------|-------|
| LP length | 0.41 mm |
| ar length | 0.33 mm |
| Length difference | 0.086 mm (26.4%) |
| Dice coefficient | 0.111 |
| IoU | 0.059 |
| SMAPE | 23.332 |

![Problem Case 3](problem_cases\problem_03_inv_28_07_02_root_04.png)

### Problem Case 4

**File**: `inv_28_07_02.rsml` | **Root**: root_03 | **Annotators**: LP vs ar

| Metric | Value |
|--------|-------|
| LP length | 0.37 mm |
| ar length | 0.54 mm |
| Length difference | 0.171 mm (-31.9%) |
| Dice coefficient | 0.200 |
| IoU | 0.111 |
| SMAPE | 37.990 |

![Problem Case 4](problem_cases\problem_04_inv_28_07_02_root_03.png)

### Problem Case 5

**File**: `inv_28_07_02.rsml` | **Root**: root_04 | **Annotators**: AH vs ym

| Metric | Value |
|--------|-------|
| AH length | 0.27 mm |
| ym length | 0.37 mm |
| Length difference | 0.101 mm (-27.2%) |
| Dice coefficient | 0.263 |
| IoU | 0.152 |
| SMAPE | 31.536 |

![Problem Case 5](problem_cases\problem_05_inv_28_07_02_root_04.png)
