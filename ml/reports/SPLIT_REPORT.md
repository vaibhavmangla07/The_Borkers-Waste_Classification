# Dataset Split Report

## Dataset
ml/garbage_classification_dataset

## Total usable images
15496

## Training set
10844 images (70.0%)

## Validation set
2320 images (15.0%)

## Test set
2332 images (15.0%)

## Class distribution
| Category | Train | Validation | Test | Total |
|---|---|---|---|---|
| cardboard | 623 | 133 | 135 | 891 |
| e-waste | 661 | 141 | 143 | 945 |
| glass | 1396 | 299 | 300 | 1995 |
| metal | 538 | 115 | 116 | 769 |
| organic | 689 | 147 | 149 | 985 |
| other | 5598 | 1199 | 1201 | 7998 |
| paper | 735 | 157 | 158 | 1050 |
| plastic | 604 | 129 | 130 | 863 |

## Excluded classes
None

## Duplicate handling
Exact duplicates grouped by MD5 hash. Only the first image of a duplicate group is included in the manifest. Duplicate groups are kept strictly within a single split (train/val/test) to prevent data leakage.

## Random seed
42

## Leakage checks
Data leakage prevented by strict hash-based grouping prior to split allocation.
