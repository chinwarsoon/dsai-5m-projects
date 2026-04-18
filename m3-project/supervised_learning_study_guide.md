# Supervised Learning Study Guide

This document is a companion guide to:

- `notebooks/part_1_supervised_learning_2_lesson.ipynb`
- `notebooks/part_2_supervised_learning_2_lesson.ipynb`
- `notebooks/part_3_supervised_learning_2_lesson.ipynb`
- `notebooks/part_4_supervised_learning_2_lesson.ipynb`

It explains the purpose of each notebook, the core mathematics, what the code is doing, how the pieces fit into a full supervised learning workflow, and what to pay attention to when applying the ideas in practice.

## Environment setup used for this guide

A local virtual environment was created in this repository at `.venv` and the core notebook packages were installed there, including:

- `scikit-learn`
- `seaborn`
- `pandas`
- `numpy`
- `matplotlib`
- `jupyter`

Useful commands:

```bash
source .venv/bin/activate
jupyter notebook
```

Or, to run Python directly from the environment:

```bash
.venv/bin/python your_script.py
```

## 1. Big Picture: What These Four Parts Teach

Together, the four notebooks cover a compact supervised learning workflow:

1. `Part 1` introduces preprocessing, which prepares raw data for machine learning algorithms.
2. `Part 2` introduces evaluation metrics for classification and regression.
3. `Part 3` puts everything together in an end-to-end workflow on the Titanic dataset.
4. `Part 4` explains the bias-variance tradeoff, which helps us reason about underfitting and overfitting.

In supervised learning, we learn a mapping from input features `X` to a target `y`.

- Classification predicts categories such as `survived` or `not survived`.
- Regression predicts continuous values such as price or temperature.

The full loop is:

1. Prepare data.
2. Split into training and test sets.
3. Transform features.
4. Train a model.
5. Evaluate with the right metric.
6. Improve the model while avoiding underfitting and overfitting.

## 2. Part 1: Preprocessing

## Why this part matters

Most machine learning models expect clean numerical inputs. Real datasets usually contain:

- Categorical values such as `red`, `male`, `embarked=S`
- Numerical values with different scales
- Missing values

Preprocessing turns raw data into a model-ready representation.

## 2.1 Categorical preprocessing

### Label encoding

Label encoding maps each category to an integer.

Example:

- `red -> 0`
- `green -> 1`
- `blue -> 2`

This is simple, but it can accidentally create a fake ordering. For example, a model may interpret `blue=2` as "larger" than `red=0`, even when color has no natural order.

### When label encoding is appropriate

- Good for ordinal categories, where order is real.
- Typical examples: `low < medium < high`, `bronze < silver < gold`.

### When it is risky

- Risky for nominal categories with no natural order.
- Typical examples: city names, colors, product IDs.

### One-hot encoding

One-hot encoding creates one binary feature per category.

If `color` has three categories:

- `red -> [1, 0, 0]`
- `green -> [0, 1, 0]`
- `blue -> [0, 0, 1]`

This avoids fake ordering, which is why it is usually preferred for nominal categories.

### Tradeoff

One-hot encoding can increase dimensionality. If a feature has many unique values, it creates many columns, which can increase memory use and make some models less efficient.

## 2.2 What the Part 1 code does for categorical variables

### Pandas approach

The notebook first shows a quick exploratory workflow with `pandas`.

`df['color'].astype('category').cat.codes`

- Converts the column into pandas categorical type
- Assigns an integer code to each category
- Useful for quick inspection and lightweight preprocessing

`pd.get_dummies(df, columns=['color'])`

- Expands the `color` column into binary columns such as `color_red`, `color_green`, `color_blue`
- Very convenient for small examples and fast prototyping

### Scikit-learn approach

The notebook then shows the pipeline-friendly method using `sklearn`.

`LabelEncoder()`

- Fits a mapping from category to integer
- In scikit-learn, it is mainly intended for target labels `y`
- It is not the preferred general encoder for feature columns in production pipelines

`OneHotEncoder(sparse_output=False)`

- Learns category values during `fit`
- Converts later data consistently during `transform`
- `sparse_output=False` makes the output dense for readability in the notebook
- In larger datasets, sparse output is often more memory-efficient

`encoder.get_feature_names_out(['color'])`

- Produces readable output column names
- Useful when converting transformed arrays back into DataFrames

## 2.3 Numerical preprocessing

The notebook covers three common transformations: standardization, min-max scaling, and normalization.

### Why scaling matters

Some algorithms are sensitive to feature scale because they use distances, dot products, or optimization over coefficients.

Examples:

- KNN uses distances directly
- SVM depends strongly on feature magnitudes
- Logistic regression and linear models often train more smoothly with scaled data

Tree-based models are usually less sensitive to scaling.

### Standardization

Standardization rescales a feature so it has mean `0` and standard deviation `1`.

\[
x' = \frac{x - \mu}{\sigma}
\]

Where:

- `x` is the original value
- `mu` is the feature mean
- `sigma` is the feature standard deviation

### Intuition

Standardization answers: "How many standard deviations away from the mean is this value?"

### When to use it

- Common default for linear models, SVMs, PCA, logistic regression
- Good when features follow different ranges and outliers are not extreme

### Min-max scaling

Min-max scaling maps a feature into a fixed range, usually `[0, 1]`.

\[
x' = \frac{x - \min(x)}{\max(x) - \min(x)}
\]

### Intuition

It preserves order and relative spacing within the original minimum and maximum.

### When to use it

- Useful for KNN and neural-network-style workflows
- Useful when a bounded range is convenient
- Sensitive to outliers because the min and max define the scaling

### Normalization

Normalization in this notebook refers to row-wise vector normalization, not column scaling.

For L2 normalization:

\[
x' = \frac{x}{||x||_2} = \frac{x}{\sqrt{\sum_i x_i^2}}
\]

### Intuition

Each row is treated like a vector and rescaled to length `1`. This preserves direction but changes magnitude.

### When to use it

- Text/vector space models
- Similarity-based methods
- Cases where relative composition matters more than raw scale

### Important distinction

- `StandardScaler` and `MinMaxScaler` transform columns
- `Normalizer` transforms rows

That distinction is easy to miss and matters a lot.

## 2.4 Missing values

Many models cannot train directly on missing values, so the notebook introduces imputation.

### Mean imputation

The code uses:

`SimpleImputer(strategy='mean')`

This replaces missing values in each column with the column mean.

### Why this helps

- Keeps all rows instead of dropping data
- Simple baseline that is easy to implement

### Caveats

- Mean imputation can distort the distribution
- It reduces variance
- It may weaken relationships between variables

### Better choices in some cases

- `median` for skewed numerical data
- `most_frequent` for categorical data
- model-based imputation for more advanced workflows

## 2.5 Why Part 1 ends with metrics

The notebook transitions from preprocessing into model evaluation by creating a synthetic classification problem and fitting logistic regression. That bridge is intentional:

- preprocessing prepares inputs
- a model is trained
- metrics tell us whether the model is useful

That transition sets up Part 2.

## 3. Part 2: Evaluation Metrics

This notebook explains how to judge model quality.

A model is not "good" just because it trains successfully. We need metrics that match the business or decision context.

## 3.1 Classification metrics

The notebook builds a synthetic binary classification dataset using:

- `make_classification`
- `train_test_split`
- `LogisticRegression`

### Why this setup is useful

- Synthetic data is controlled and easy to reproduce
- Train-test split simulates generalization to unseen data
- Logistic regression is a standard baseline classifier

## 3.2 Confusion matrix

The confusion matrix is the foundation for many classification metrics.

It contains:

- `TP`: true positives
- `TN`: true negatives
- `FP`: false positives
- `FN`: false negatives

Interpretation:

- TP: model predicts positive and the true label is positive
- TN: model predicts negative and the true label is negative
- FP: model predicts positive but the true label is negative
- FN: model predicts negative but the true label is positive

See [confusion-matrix.png](/home/franklin/dsai/5m-data-3.3-supervised-learning/assets/confusion-matrix.png).

### Why it matters

Accuracy alone hides the types of mistakes a model makes. The confusion matrix shows error structure, not just total score.

## 3.3 Accuracy

\[
\text{Accuracy} = \frac{\text{correct predictions}}{\text{total predictions}}
\]

Equivalently:

\[
\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}
\]

### When it works well

- Balanced classes
- Similar cost for false positives and false negatives

### When it fails

In highly imbalanced data, a model can get high accuracy by predicting the majority class most of the time.

Example:

- If 95% of labels are negative, always predicting negative gives 95% accuracy, but the model is useless for finding positives.

## 3.4 Precision

\[
\text{Precision} = \frac{TP}{TP + FP}
\]

Precision asks:

"Of the items predicted positive, how many were actually positive?"

### Use precision when

- False positives are costly
- Examples: spam flagging, fraud alerts, medical false alarms, review escalation systems

## 3.5 Recall

\[
\text{Recall} = \frac{TP}{TP + FN}
\]

Recall asks:

"Of the actual positives, how many did we catch?"

### Use recall when

- False negatives are costly
- Examples: disease screening, fraud detection, safety alerts

Recall is also called:

- sensitivity
- true positive rate

## 3.6 Specificity

\[
\text{Specificity} = \frac{TN}{TN + FP}
\]

Specificity asks:

"Of the actual negatives, how many did we correctly reject?"

It complements recall by focusing on the negative class.

## 3.7 F1 score

\[
F1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
\]

The F1 score is the harmonic mean of precision and recall.

### Why harmonic mean

It penalizes imbalance. If precision is high but recall is poor, the F1 score stays limited. That makes it a good "balance" metric.

### Use F1 when

- classes are imbalanced
- you need one summary score combining precision and recall

## 3.8 ROC curve and AUC

The ROC curve plots:

- x-axis: false positive rate
- y-axis: true positive rate

Where:

\[
\text{FPR} = \frac{FP}{FP + TN}
\]

\[
\text{TPR} = \frac{TP}{TP + FN}
\]

The curve is generated by sweeping the classification threshold.

### Why thresholds matter

Models like logistic regression produce probabilities. To convert probability into a class label, we choose a threshold, often `0.5`.

- Lower threshold: more positives predicted, usually higher recall and higher false positive rate
- Higher threshold: fewer positives predicted, usually higher precision and lower recall

### AUC

AUC is the area under the ROC curve.

Interpretation:

- `1.0`: perfect separation
- `0.5`: random guessing
- `< 0.5`: worse than random in the current direction

See [roc-auc.png](/home/franklin/dsai/5m-data-3.3-supervised-learning/assets/roc-auc.png).

### Why ROC/AUC is useful

- Evaluates ranking quality across thresholds
- Helps compare classifiers without fixing a single threshold too early

### Practical caution

ROC/AUC is helpful, but in very imbalanced datasets, precision-recall curves can sometimes be more informative.

## 3.9 What the classification code is doing

`make_classification(...)`

- Generates a synthetic binary classification dataset
- Good for demonstrations because the notebook does not depend on an external CSV

`train_test_split(...)`

- Splits data into training and test sets
- Prevents us from evaluating on the same data we trained on

`LogisticRegression()`

- Fits a linear decision boundary in feature space
- Outputs class probabilities using the logistic function

The core logistic function is:

\[
\sigma(z) = \frac{1}{1 + e^{-z}}
\]

Where `z = w^T x + b`.

This maps any real-valued score into a probability between `0` and `1`.

`predict(X_test)`

- Produces class labels

`predict_proba(X_test)[:, 1]`

- Produces probability for the positive class
- Necessary for ROC/AUC because ROC depends on threshold sweeps over scores, not only final labels

### Verified output from the synthetic classification example

Running the notebook logic locally in `.venv` produced:

- Confusion matrix: `[[90, 3], [4, 103]]`
- Accuracy: `0.9650`
- Precision: `0.9717`
- Recall: `0.9626`
- F1: `0.9671`
- AUC: `0.9807`

These values are strong, which makes sense for a synthetic dataset generated to be learnable.

## 3.10 Regression metrics

The notebook then switches from classification to regression evaluation.

That is a useful teaching move because it reinforces that:

- classification predicts labels
- regression predicts continuous values
- the metric must match the task type

### Mean Absolute Error (MAE)

\[
\text{MAE} = \frac{1}{n}\sum_{i=1}^{n} |y_i - \hat{y}_i|
\]

MAE gives the average absolute size of the error.

### Strength

- Easy to interpret
- Same unit as the target

### Weakness

- Does not penalize large errors as strongly as MSE

### Mean Squared Error (MSE)

\[
\text{MSE} = \frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2
\]

MSE squares errors before averaging.

### Why squaring matters

- Large errors are penalized more heavily
- Useful when large misses are especially bad

### Weakness

- Sensitive to outliers
- Unit is squared, which is less intuitive

### Root Mean Squared Error (RMSE)

\[
\text{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}
\]

RMSE is the square root of MSE, so it returns to the original unit of the target.

### R-squared

\[
R^2 = 1 - \frac{\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}{\sum_{i=1}^{n}(y_i - \bar{y})^2}
\]

It compares model error to the error of predicting the mean every time.

Interpretation:

- `1.0`: perfect fit
- `0.0`: no better than predicting the mean
- `< 0.0`: worse than predicting the mean

### Adjusted R-squared

\[
\text{Adjusted } R^2 = 1 - \frac{(1-R^2)(n-1)}{n-p-1}
\]

Where:

- `n` is the number of observations
- `p` is the number of predictors

Adjusted `R^2` penalizes unnecessary predictors and is useful when comparing models with different feature counts.

### Verified output from the regression example

Running the notebook logic locally in `.venv` produced:

- MAE: `0.5000`
- MSE: `0.3750`
- RMSE: `0.6124`
- R²: `0.9486`

## 4. Part 3: End-to-End Workflow on Titanic

This is the most practical notebook because it assembles the workflow end to end.

## 4.1 Goal

Predict whether a Titanic passenger survived based on passenger features.

Target:

- `survived`

Features chosen in the notebook:

- `pclass`
- `sex`
- `age`
- `sibsp`
- `parch`
- `fare`
- `embarked`

## 4.2 Why these features make sense

- `pclass` captures socio-economic status
- `sex` is historically important in Titanic survival outcomes
- `age` may matter because children were sometimes prioritized
- `sibsp` and `parch` encode family relationships aboard
- `fare` correlates with ticket class and status
- `embarked` may carry route and passenger-group information

The notebook intentionally mixes numerical and categorical variables so preprocessing becomes realistic.

## 4.3 Data inspection

The early cells do:

- `titanic.shape`
- `titanic.head()`
- `titanic.survived.value_counts()`
- `titanic.isna().sum()`

These checks answer four essential questions:

1. How large is the dataset?
2. What do the columns look like?
3. Is the target balanced?
4. Which columns contain missing values?

This is exactly what a strong workflow should do before modeling.

## 4.4 Train-test split

The notebook uses:

`train_test_split(X, y, test_size=0.2, random_state=0)`

Meaning:

- 80% training data
- 20% testing data
- `random_state=0` makes the split reproducible

### Why split before fitting transformers

This is a crucial anti-leakage rule.

If we fit imputers, encoders, or scalers on the full dataset before splitting, information from the test set leaks into training. That leads to overly optimistic evaluation.

The pipeline design in this notebook prevents that mistake.

## 4.5 The preprocessing pipeline

This is the core engineering idea of the notebook.

### Numerical pipeline

`Pipeline(steps=[('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())])`

Meaning:

1. Fill missing numerical values with the median.
2. Standardize the numerical columns.

### Why median here

Median is more robust to outliers than mean. That is often a good default for variables like `age` or `fare`.

### Categorical pipeline

`Pipeline(steps=[('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))])`

Meaning:

1. Fill missing categorical values with the mode.
2. One-hot encode categories.

### Why `handle_unknown='ignore'`

This is an important production-safe setting.

If the test set contains a category not seen during training, the encoder will not crash. Instead, it leaves the unseen category with zeros in the encoded space.

### ColumnTransformer

`ColumnTransformer(...)` applies different preprocessing pipelines to different column groups.

That is one of scikit-learn's most useful abstractions for tabular data.

It allows:

- numerical columns to be imputed and scaled
- categorical columns to be imputed and encoded
- all within one consistent object

### Full pipeline

The notebook wraps the preprocessor and model together:

`Pipeline(steps=[('preprocessor', preprocessor), ('model', LogisticRegression())])`

This means:

- raw DataFrame goes in
- transformed features are created internally
- the model trains on transformed features

### Why this is good practice

- Prevents data leakage
- Keeps training and inference consistent
- Makes experimentation cleaner
- Works naturally with cross-validation and grid search later

See [titanic-data-pipeline.png](/home/franklin/dsai/5m-data-3.3-supervised-learning/assets/titanic-data-pipeline.png).

## 4.6 Logistic regression in this notebook

Logistic regression is a strong baseline classifier for tabular binary classification.

It models:

\[
P(y=1 \mid x) = \sigma(w^T x + b)
\]

Where:

- `x` is the transformed feature vector
- `w` is the coefficient vector
- `b` is the intercept
- `sigma` is the logistic sigmoid

### Why it is a good first model

- Fast and interpretable
- Handles linearly separable structure well
- Often competitive as a baseline on tabular data

### Why scaling helps logistic regression

Scaling makes optimization more stable and helps coefficients operate on comparable scales.

## 4.7 Evaluation in the Titanic workflow

The notebook computes:

- accuracy
- precision
- recall
- F1
- ROC AUC

This is a strong choice because it avoids relying on a single metric.

For survival prediction, which metric matters most depends on the question:

- If missing survivors is especially costly, prioritize recall.
- If false survival predictions are especially costly, prioritize precision.
- If you want general ranking performance, check AUC.

## 4.8 Self-study variation: KNN with min-max scaling

The exercise replaces:

- `StandardScaler` with `MinMaxScaler`
- `LogisticRegression` with `KNeighborsClassifier`

This is pedagogically important because KNN behaves very differently from logistic regression.

### Why min-max scaling is a natural choice for KNN

KNN depends on distance between points. If one feature has a much larger range, it can dominate the distance calculation.

Min-max scaling makes features comparable by putting them into the same range.

### How KNN works

To classify a new point:

1. Compute its distance to training points.
2. Find the `k` nearest neighbors.
3. Let those neighbors vote on the class.

### Why KNN can be sensitive

- sensitive to feature scale
- sensitive to noisy features
- prediction can be slower for large datasets
- performance depends on the choice of `k`

### Why this exercise is valuable

It teaches that preprocessing is not one-size-fits-all. The best transformation often depends on the model family.

## 4.10 Note on reproducing the Titanic notebook locally

The notebook uses:

`sns.load_dataset('titanic')`

That convenience loader fetches dataset metadata from the seaborn online repository. In this sandboxed environment, package installation worked, but outbound dataset fetching is blocked, so the Titanic cells could not be rerun end to end here without replacing that call with a local CSV copy of the dataset.

So for Part 3:

- the code structure was inspected directly from the notebook
- the pipeline explanation in this guide is accurate to the notebook source
- the exact Titanic metric values were not re-verified in this sandbox because dataset download is blocked

## 4.9 Practical lessons from Part 3

Part 3 teaches several best practices that are more important than the exact Titanic scores:

1. Inspect the dataset before modeling.
2. Separate features and target clearly.
3. Handle numerical and categorical columns differently.
4. Use pipelines to avoid leakage.
5. Evaluate on a held-out test set.
6. Compare models, not just one model.

## 5. Part 4: Bias-Variance Tradeoff

This notebook explains one of the most important ideas in machine learning theory.

## 5.1 The core idea

Prediction error can come from different sources. Two major sources are bias and variance.

### Bias

Bias is error from overly simple assumptions.

High bias means:

- model is too simple
- misses real patterns
- underfits

### Variance

Variance is error from excessive sensitivity to the training sample.

High variance means:

- model is too flexible
- memorizes noise
- overfits

## 5.2 The example used in the notebook

The notebook generates noisy data from:

\[
y = \cos(1.5 \pi x) + \text{noise}
\]

Then it fits polynomial regression models with degrees:

- `1`
- `4`
- `15`

### Why this is a good demo

Polynomial degree directly controls model complexity.

- degree 1 is too simple for the curved true function
- degree 15 is flexible enough to chase noise
- degree 4 is a middle ground

## 5.3 What the code is doing

`PolynomialFeatures(degree=d, include_bias=False)`

- Expands an input `x` into polynomial terms
- Example for degree 3: `x, x^2, x^3`

`LinearRegression()`

- Fits a linear model on the expanded polynomial features

`make_pipeline(polynomial_features, linear_regression)`

- Chains feature expansion and regression into one object

This is polynomial regression, even though the final estimator is linear regression, because the features themselves are nonlinear.

## 5.4 Why degree controls complexity

If the original feature is `x`, then polynomial features create:

\[
\hat{y} = \beta_0 + \beta_1 x + \beta_2 x^2 + \cdots + \beta_d x^d
\]

As `d` increases:

- the function class becomes more flexible
- training fit can improve
- risk of overfitting also increases

## 5.5 Test MSE in the plots

The notebook titles each plot with test MSE.

That matters because overfitting is not defined by training performance alone.

A high-variance model often has:

- very low training error
- worse test error

That is why the notebook evaluates on held-out data.

## 5.6 Visual interpretation

The intended interpretations are:

- Degree 1: high bias, low variance
- Degree 4: healthier balance
- Degree 15: low bias, high variance

### Verified output from the bias-variance example

Running the notebook logic locally in `.venv` produced these test MSE values:

- Degree 1: `0.344519`
- Degree 4: `0.020637`
- Degree 15: `0.032473`

This is consistent with the notebook's teaching goal:

- degree 1 underfits badly
- degree 4 gives the best generalization among the three
- degree 15 is more flexible, but not better on test data than degree 4

The notebook also points to two helpful visuals:

- [bv-tradeoff-2.png](/home/franklin/dsai/5m-data-3.3-supervised-learning/assets/bv-tradeoff-2.png)
- [bv-tradeoff.png](/home/franklin/dsai/5m-data-3.3-supervised-learning/assets/bv-tradeoff.png)

## 5.7 Practical ways to balance bias and variance

The notebook lists several strategies. Here is what they do in practice.

### Cross-validation

- Estimates performance across multiple splits
- Helps detect models that look good only on one lucky split

### More training data

- Often reduces variance
- Especially helpful for flexible models

### Feature selection

- Removes noisy or irrelevant variables
- Can reduce variance and improve interpretability

### Regularization

- Constrains model complexity
- Examples: Ridge and Lasso
- Usually increases bias a bit to reduce variance more

### Ensemble methods

- Combine multiple models
- Can stabilize predictions and improve generalization

## 6. How the Four Parts Connect

These notebooks are strongest when read as one story:

- Part 1 answers: "How do I prepare messy data?"
- Part 2 answers: "How do I measure model quality?"
- Part 3 answers: "How do I build a real workflow end to end?"
- Part 4 answers: "How do I reason about model complexity and generalization?"

That sequence is close to how real machine learning projects work.

## 7. Common Pitfalls These Notebooks Help You Avoid

### 1. Encoding nominal categories with integer labels

This can inject fake order into the data. Prefer one-hot encoding unless the categories are truly ordinal.

### 2. Scaling everything without thinking

Scaling is helpful for many models, but the choice of scaler depends on the model and data distribution.

### 3. Dropping missing data too casually

Removing rows can shrink the dataset and introduce bias if missingness is systematic.

### 4. Evaluating with only accuracy

Accuracy can be misleading, especially with imbalance.

### 5. Fitting preprocessing before the train-test split

That causes leakage. Pipelines are the clean fix.

### 6. Choosing a model only by flexibility

A more complex model is not automatically better. Part 4 explains why.

## 8. Suggested Study Flow

If you are learning from these notebooks, a good sequence is:

1. Read Part 1 and rewrite each preprocessing method in your own words.
2. In Part 2, compute the metrics manually from a small confusion matrix.
3. In Part 3, sketch the pipeline on paper before running the code.
4. In Part 4, explain why degree 15 can look good on training data but bad on test data.

You will understand the material much more deeply if you can explain:

- why one-hot encoding is often safer than label encoding
- why train-test leakage is dangerous
- why precision and recall trade off
- why more complex models can generalize worse

## 9. References and Further Reading

These references match the topics used in the notebooks.

### Repository materials

- [Part 1 notebook](/home/franklin/dsai/5m-data-3.3-supervised-learning/notebooks/part_1_supervised_learning_2_lesson.ipynb)
- [Part 2 notebook](/home/franklin/dsai/5m-data-3.3-supervised-learning/notebooks/part_2_supervised_learning_2_lesson.ipynb)
- [Part 3 notebook](/home/franklin/dsai/5m-data-3.3-supervised-learning/notebooks/part_3_supervised_learning_2_lesson.ipynb)
- [Part 4 notebook](/home/franklin/dsai/5m-data-3.3-supervised-learning/notebooks/part_4_supervised_learning_2_lesson.ipynb)
- [Titanic pipeline image](/home/franklin/dsai/5m-data-3.3-supervised-learning/assets/titanic-data-pipeline.png)
- [Confusion matrix image](/home/franklin/dsai/5m-data-3.3-supervised-learning/assets/confusion-matrix.png)
- [ROC AUC image](/home/franklin/dsai/5m-data-3.3-supervised-learning/assets/roc-auc.png)
- [Bias-variance image 1](/home/franklin/dsai/5m-data-3.3-supervised-learning/assets/bv-tradeoff.png)
- [Bias-variance image 2](/home/franklin/dsai/5m-data-3.3-supervised-learning/assets/bv-tradeoff-2.png)

### Library and dataset references

- `pandas` documentation for categorical data and `get_dummies`
- `scikit-learn` documentation for `OneHotEncoder`, `SimpleImputer`, `StandardScaler`, `MinMaxScaler`, `Normalizer`, `Pipeline`, `ColumnTransformer`
- `scikit-learn` documentation for `LogisticRegression`, `KNeighborsClassifier`, and evaluation metrics
- Titanic dataset reference used in the notebook: Kaggle Titanic competition data dictionary

### Theory references

- Introduction to Statistical Learning: preprocessing, classification metrics, regression metrics, and bias-variance tradeoff
- Pattern Recognition and Machine Learning: probabilistic modeling and generalization concepts
- Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow: practical pipeline design

## 10. Final Summary

If you remember only the essentials, keep these:

1. Preprocessing is part of the model workflow, not a separate afterthought.
2. Choose encoders and scalers based on data type and model behavior.
3. Use the right metric for the task and error cost.
4. Pipelines help prevent leakage and make workflows reproducible.
5. Good generalization comes from balancing bias and variance, not simply maximizing training fit.

## Note on verification

This study guide was written by inspecting the notebook source and repository assets, then validating the runnable synthetic examples in a local `.venv`.

Verified locally:

- Part 2 synthetic classification metrics
- Part 2 regression metrics
- Part 4 bias-variance example

Not fully rerun in this sandbox:

- Part 3 Titanic example, because `seaborn.load_dataset('titanic')` requires network access to fetch dataset metadata
