# Annotation Quality Report

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
