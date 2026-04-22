# Linear Regression Workplan — HDB Resale Price Prediction

## Project Context

Build a machine learning pipeline to predict HDB resale prices for records in `test.csv`, then output predictions for the subset of IDs listed in `sample_sub_reg.csv`.

---

## File Layout

| Path | Description |
|------|-------------|
| `data/train.csv` | Labelled training data; includes `resale_price` target column |
| `data/test.csv` | Unlabelled scoring data; includes `id` identifier column |
| `output/sample_sub_reg.csv` | Submission template — contains only the `Id` column for the required subset of test IDs |
| `output/Team_10_submission.csv` | **Generated** — final predictions aligned to `sample_sub_reg.csv` IDs |
| `workflow/main.ipynb` | Pipeline notebook (VS Code / Google Colab compatible) |
| `reference/` | Lesson notebooks used as implementation reference |

> **Note:** `test.csv` contains IDs that are **different** from `train.csv`. Not all IDs in `test.csv` appear in `sample_sub_reg.csv`; the final output must be filtered to only those IDs.

---

## Pipeline Steps (implemented in `workflow/main.ipynb`)

### 1. Environment Setup
- Resolve project root automatically (works in both VS Code and Google Colab).
- Define all paths (`TRAIN_PATH`, `TEST_PATH`, `OUTPUT_PATH`, `SAMPLE_SUB_PATH`).
- Set `TARGET_COLUMN = "resale_price"` and `ID_CANDIDATES = ["Id", "id"]`.

### 2. Data Loading
- Load `train.csv` and `test.csv` with error handling for missing / empty files.
- Detect the ID column dynamically from `ID_CANDIDATES`.
- Display head and shapes for quick sanity check.

### 3. Explore Data
- Display first rows and shapes of both datasets.
- Confirm ID and target columns exist.

### 4. Prepare Features
- Separate features (`X`) and target (`y`) from training data; drop the ID column.
- **Drop `floor_area_sqft`**: it is a perfect linear transformation of `floor_area_sqm` (`sqft = sqm × 10.764`), carrying zero additional information and introducing multicollinearity. `floor_area_sqm` (SI unit) is retained.
- **Keep `town`** (26 unique values) as a categorical feature — it is one of the strongest predictors of resale price because location determines proximity to amenities, MRT, schools, and the CBD.
- Apply the same column drops to `X_test`; align `X_test` columns to match `X`.

### 5. Build Preprocessing Pipeline (`ColumnTransformer`)
- **Numeric features:** median imputation.
- **Categorical features:** most-frequent imputation → one-hot encoding (`handle_unknown="ignore"`).

### 6. Model Selection via Cross-Validation
- Candidate models: `TownTierFirstRandomForest` and `RandomForestRegressor` (baseline).
- 3-fold CV scored by **RMSE** (manual `KFold` loop so both model types work).
- Best model selected automatically (lowest mean CV RMSE).

### 7. Validation on Hold-out Set
- 80/20 train/validation split (`random_state=42`).
- Report **Validation RMSE** and **Validation MAE**.

### 8. Evaluate: Actual vs Predicted
- Side-by-side comparison table (Actual, Predicted, Residual, Residual %, Abs Error).
- Residual summary statistics (mean, median, std, MAE, MAPE).
- Prediction accuracy buckets: within $10 K, $50 K, $100 K.
- Best and worst 5 predictions by absolute error.

### 9. Evaluate: Visualisation
- Predicted vs Actual scatter plot.
- Residual plot (residuals vs predicted).
- Residual histogram.
- Q-Q plot (normality check).

### 10. Evaluate: Comprehensive Metrics
- R² score, RMSE, MAE, MAPE, Explained Variance.
- Automated performance assessment (Excellent / Good / Moderate / Poor).

### 11. Feature Importance Analysis
- Extract feature importances from the trained model.
- Bar chart of top 20 features.
- Cumulative importance table.
- Importance grouped by feature category (Numeric, Town, Flat Type, etc.).
- Candidates for removal (bottom 10 % by importance).

### 12. Generate Final Submission
- Retrain best model on **full** training set.
- Predict on all rows of `test.csv`.
- Filter predictions to only the IDs in `sample_sub_reg.csv` (preserving their order).
- Save as `output/Team_10_submission.csv` with columns `[id, Predicted]`.

---

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| CV RMSE | Cross-validated Root Mean Squared Error (model selection) |
| Validation RMSE | RMSE on 20 % hold-out split |
| Validation MAE | Mean Absolute Error on 20 % hold-out split |
| MAPE | Mean Absolute Percentage Error on 20 % hold-out split |
| R² | Coefficient of Determination on 20 % hold-out split |
| Explained Variance | Explained Variance Score on 20 % hold-out split |

---

## Feature Engineering Decisions

| Decision | Rationale |
|----------|-----------|
| Drop `floor_area_sqft` | Perfect linear duplicate of `floor_area_sqm` (ratio = 10.764, std = 0). Keeping both inflates feature count and introduces multicollinearity. |
| Keep `town` | 26 unique HDB towns. Location is a primary driver of resale price (CBD proximity, MRT access, school catchment). One-hot encoded by the preprocessing pipeline. |
| Add `town_tier` | Binary column derived from `town`. Forces the largest price-variance split to the root of every tree. See Improvement Phase I2. |

---

## Compatibility

The notebook resolves the project root at runtime and works without modification in:
- **VS Code** (run from any directory inside the workspace)
- **Google Colab** (upload the `m3-project` folder or mount Google Drive)

---

## Improvement Phase — Feature Engineering Applied

This section documents each feature engineering decision applied to improve prediction quality, the rationale behind it, and the expected impact on the model.

---

### I1. Drop `floor_area_sqft` (redundant unit column)

| | |
|---|---|
| **Status** | ✅ Implemented (cell 8) |
| **What** | Remove `floor_area_sqft` from both `X` and `X_test` before training. |
| **Why** | `floor_area_sqft = floor_area_sqm × 10.764` — a perfect linear transformation with zero variance in the ratio across all 150,634 rows. Keeping both columns gives the model two identical signals, inflating feature count and introducing multicollinearity without adding any new information. |
| **Impact** | Reduces feature count by 1. Prevents the model from splitting on two columns that encode the same thing, freeing split budget for genuinely informative features. |
| **Retained** | `floor_area_sqm` (SI unit, more interpretable). |

---

### I2. `town_tier` — binary location tier as root split

| | |
|---|---|
| **Status** | ✅ Implemented (cell 8 + cell 12) |
| **What** | Engineer a new binary column `town_tier`: `1` if the town's mean resale price ≥ overall mean ($449,162), `0` otherwise. Force this column to be the **first split node** in every tree via `TownTierFirstRandomForest`. |
| **Why** | `town` alone spans a $329,000 price range (YISHUN $375K → BUKIT TIMAH $704K). A single binary split on `town_tier` immediately separates the dataset into two price regimes, reducing the variance each sub-tree must explain. Standard Random Forest may not choose `town_tier` as the root because random feature sampling at each node is not guaranteed to select it first. |

**Town split (based on overall mean $449,162):**

| Tier | Towns |
|------|-------|
| `1` — Premium (14 towns, mean ≥ $449K) | BISHAN, BUKIT MERAH, BUKIT TIMAH, CENTRAL AREA, CLEMENTI, KALLANG/WHAMPOA, MARINE PARADE, PASIR RIS, PUNGGOL, QUEENSTOWN, SENGKANG, SERANGOON, TAMPINES, TOA PAYOH |
| `0` — Standard (12 towns, mean < $449K) | ANG MO KIO, BEDOK, BUKIT BATOK, BUKIT PANJANG, CHOA CHU KANG, GEYLANG, HOUGANG, JURONG EAST, JURONG WEST, SEMBAWANG, WOODLANDS, YISHUN |

| | |
|---|---|
| **How it minimises nodes** | By splitting on `town_tier` at the root, each sub-tree only needs to explain price variation *within* its tier rather than across the full $330K range. Accurate leaf predictions are reached with fewer subsequent splits → shallower effective trees → fewer total nodes per forest. |
| **Model** | `TownTierFirstRandomForest` — a custom ensemble that builds each tree in two stages: (1) root split on `town_tier`, (2) two independent `DecisionTreeRegressor` sub-trees grown on the above-average and below-average subsets respectively, using all remaining features with standard `max_features="sqrt"` random sampling. |
| **Baseline comparison** | Standard `RandomForestRegressor` is kept as a CV baseline. The model with lower CV RMSE is selected automatically. |

---

### Planned Improvements (not yet implemented)

The following improvements are identified from feature importance analysis and domain knowledge. They should be applied in order of expected impact.

#### P1. Target-encode `street_name` (high-cardinality categorical)

| | |
|---|---|
| **What** | Replace `street_name` (hundreds of unique values) with its mean `resale_price` per street, computed on the training set only using out-of-fold encoding to prevent leakage. |
| **Why** | One-hot encoding `street_name` produces hundreds of sparse binary columns, most of which appear in very few rows. Target encoding collapses this into a single numeric column that directly captures the street-level price premium. |
| **Implementation** | Use `sklearn.preprocessing.TargetEncoder` (scikit-learn ≥ 1.3) inside the `ColumnTransformer`, or a manual out-of-fold mean-encoding scheme for older versions. |
| **Risk** | Data leakage if encoding is computed on the full training set before CV splits. Must encode within each fold. |

#### P2. Interaction feature: `town_tier × floor_area_sqm`

| | |
|---|---|
| **What** | Add `town_tier_x_area = town_tier × floor_area_sqm` as a new numeric column. |
| **Why** | A large flat in a premium town commands a disproportionately higher price than a large flat in a standard town. This interaction captures the non-additive relationship between size and location tier that a linear combination cannot express. |
| **Implementation** | `X['town_tier_x_area'] = X['town_tier'] * X['floor_area_sqm']` — applied to both `X` and `X_test` in cell 8. |
| **Expected impact** | Moderate — most useful for the upper tail of the price distribution where large premium-town flats are systematically under-predicted. |

#### P3. `hdb_age_tier` — binned building age

| | |
|---|---|
| **What** | Bin `hdb_age` into three categories: `new` (< 10 years), `mid` (10–30 years), `old` (> 30 years). |
| **Why** | The relationship between age and price is non-linear: very new flats carry a premium, mid-age flats are stable, and very old flats approaching lease expiry drop sharply. Binning makes this threshold pattern explicit rather than forcing the model to discover it through many numeric splits. |
| **Implementation** | `pd.cut(X['hdb_age'], bins=[0, 10, 30, 999], labels=['new', 'mid', 'old'])` → treated as categorical → one-hot encoded by the existing `ColumnTransformer`. |

#### P4. `mrt_proximity_tier` — binned MRT distance

| | |
|---|---|
| **What** | Bin `mrt_nearest_distance` into: `walking` (< 400 m), `near` (400–800 m), `far` (> 800 m). |
| **Why** | MRT proximity has a threshold effect: flats within walking distance command a clear premium, but the difference between 900 m and 1,500 m is marginal. A continuous distance column forces the model to learn this threshold via many splits; a binned column expresses it in a single node. |
| **Implementation** | `pd.cut(X['mrt_nearest_distance'], bins=[0, 400, 800, float('inf')], labels=['walking', 'near', 'far'])` → one-hot encoded. |

#### P5. Drop low-importance coordinate columns

| | |
|---|---|
| **What** | Drop `mrt_latitude`, `mrt_longitude`, `bus_stop_latitude`, `bus_stop_longitude`, `pri_sch_latitude`, `pri_sch_longitude`, `sec_sch_latitude`, `sec_sch_longitude`. |
| **Why** | These are raw coordinates of nearby amenities. The corresponding distance columns (`mrt_nearest_distance`, `bus_stop_nearest_distance`, etc.) already encode the relevant signal in a more useful form. Raw coordinates add noise and increase dimensionality without improving predictions. |
| **Expected impact** | Small improvement in training speed and slight reduction in overfitting. |

---

### Improvement Priority Summary

| Priority | ID | Improvement | Expected RMSE Impact | Effort | Status |
|----------|----|-------------|----------------------|--------|--------|
| 1 | I1 | Drop `floor_area_sqft` | Low — removes noise, not signal | Low | ✅ Done |
| 2 | I2 | `town_tier` root split | High — addresses largest price variance driver | Low | ✅ Done |
| 3 | P1 | Target-encode `street_name` | High — collapses hundreds of sparse OHE columns | Medium | ⬜ Planned |
| 4 | P2 | `town_tier × floor_area_sqm` interaction | Moderate — captures premium-town size premium | Low | ⬜ Planned |
| 5 | P3 | `hdb_age_tier` binning | Moderate — makes lease-expiry threshold explicit | Low | ⬜ Planned |
| 6 | P4 | `mrt_proximity_tier` binning | Low–Moderate — captures MRT threshold effect | Low | ⬜ Planned |
| 7 | P5 | Drop coordinate columns | Low — reduces noise and feature count | Low | ⬜ Planned |
