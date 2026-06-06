"""
model03.py — Crop type KNN predictor

Predicts what type of crop to plant from:
  - N:               soil nitrogen content
  - P:               soil phosphorus content
  - K:               soil potassium content
  - TYPE_OF_CROP:    categorical crop category (e.g. 'cereals')
  - TEMPERATURE:     average temperature
  - SEASON:          growing season (e.g. 'kharif', 'rabi')
  - SOWN:            sowing month (e.g. 'Jun')
  - HARVESTED:       harvest month (e.g. 'Oct')
  - WATER_SOURCE:    irrigation source (e.g. 'rainfed')
  - RELATIVE_HUMIDITY: relative humidity (%)

Hard-coded training averages:
  - CROPDURATION:    109.347
  - WATERREQUIRED:   887.26
  - SOIL_PH:         6.624
  - SOIL:            'sandy Loamy soil'

No model parameters stored in the DB because KNN is unsupervised.
Scaler parameters (means, stds) and training data are stored in the DB.

Scaling is done via StandardScaler
Categorical features are one-hot encoded and appended unscaled.
cosine similarity.
"""

import json
from collections import Counter

import numpy as np
from flask import current_app
from backend.db_connection import get_db


# ------------------------------------------------------------
# Hard-coded averages used to fill hidden features at predict time
# ------------------------------------------------------------
_CROPDURATION_AVG  = 109.347
_WATERREQUIRED_AVG = 887.26
_SOIL_PH_AVG       = 6.624
_SOIL_AVG          = 'sandy Loamy soil'

# Order has to match column order used when the scaler was fitted
_CONTINUOUS_COLS = [
    'CROPDURATION',
    'TEMPERATURE',
    'WATERREQUIRED',
    'RELATIVE_HUMIDITY',
    'N',
    'P',
    'K',
]

# one-hot columns, prefix
_OHE_PREFIXES = ('TYPE_OF_CROP_', 'SOIL_', 'SOWN_', 'HARVESTED_', 'WATER_SOURCE_', 'SEASON')


def train():
    """
    Placeholder for a training routine. Could be triggered from an
    admin route to retrain the model and store new parameters in the DB.
    """
    return 'Training the model'


def test():
    return 'Testing the model'


# ------------------------------------------------------------
# Internal helpers — fetch stored vals from the DB
# ------------------------------------------------------------

def _get_scaler_params():
    """
    Fetches the most-recent StandardScaler parameters from model3_scaler.

    Returns:
        tuple[np.ndarray, np.ndarray]: (means, stds), each shape (n_continuous,)
    Raises:
            ValueError: if no parameters exist in the database yet.
    """
    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(
            'SELECT feature_means, feature_stds '
            'FROM model3_scaler '
            'ORDER BY id DESC LIMIT 1'
        )
        row = cursor.fetchone()

    if row is None:
        raise ValueError("No model3 params found in the database.")

    means = np.array(json.loads(row['feature_means']))
    stds  = np.array(json.loads(row['feature_stds']))
    current_app.logger.info(f'model03 scaler loaded: means={means}, stds={stds}')
    return means, stds


def _get_ohe_cols():
    """
    Fetches the list of one-hot encoded column names from model3_ohe_cols.
    These must be stored in the exact order used during training.

    Returns:
        list[str]:( e.g. ['TYPE_OF_CROP_cereals', 'SEASON_kharif', ...])

    Raises:
        ValueError: if no OHE column list exists yet.
    """
    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(
            'SELECT col_names '
            'FROM model3_ohe_cols '
            'ORDER BY id DESC LIMIT 1'
        )
        row = cursor.fetchone()

    if row is None:
        raise ValueError('No model3 OHE column list found in the database.')

    cols = json.loads(row['col_names'])
    current_app.logger.info(f'model03 OHE cols loaded: {len(cols)} columns')
    return cols


def _get_training_data():
    """
    Fetches the training matrix and labels from the DB.
    Rows are stored as JSON arrays, labels as plain strings.

    Returns:
        tuple[np.ndarray, np.ndarray]:
            X_train  shape (n_samples, n_features) already scaled + OHE
            y_train  shape (n_samples,) crop name strings

    Raises:
        ValueError: if no training data exists yet.
    """
    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(
            'SELECT feature_vector, crop_label '
            'FROM model3_training_data '
            'ORDER BY row_id ASC'
        )
        rows = cursor.fetchall()

    if not rows:
        raise ValueError('No model3 training data found in the database.')

    X_train = np.array([json.loads(r['feature_vector']) for r in rows], dtype=float)
    y_train = np.array([r['crop_label'] for r in rows])
    current_app.logger.info(f'model03 training data: {X_train.shape}')
    return X_train, y_train


# ------------------------------------------------------------
# KNN with cosine similarity (vectorised inner loop)
# ------------------------------------------------------------

def _knn_cos(X_train, y_train, X_test, k):
    """
    K-nearest-neighbours classifier using cosine similarity.

    Args:
        X_train  (np.ndarray): shape (n_train, n_features)
        y_train  (np.ndarray): shape (n_train,) - string labels
        X_test   (np.ndarray): shape (n_test,  n_features)
        k        (int):  number of neighbours

    Returns:
        tuple[np.ndarray, list[np.ndarray]]:
            y_pred            - predicted labels, shape (n_test,)
            nearest_indices   - list of length n_test, each element is an
                                array of k training-row indices
    """
    train_norms = np.linalg.norm(X_train, axis=1, keepdims=True)
    X_train_normed = X_train / np.where(train_norms == 0, 1, train_norms)

    y_pred           = []
    nearest_indices  = []

    for test_point in X_test:
        norm = np.linalg.norm(test_point)
        test_normed = test_point / (norm if norm != 0 else 1)

        similarities     = test_normed @ X_train_normed.T          # (n_train,)
        neighbour_idx    = np.argsort(similarities)[-k:]            # top-k indices
        neighbour_labels = y_train[neighbour_idx]

        most_common = Counter(neighbour_labels).most_common(1)[0][0]
        y_pred.append(most_common)
        nearest_indices.append(neighbour_idx)

    return np.array(y_pred), nearest_indices


# ------------------------------------------------------------
# Public predict function called by route handlers
# ------------------------------------------------------------

def predict(N, P, K, TYPE_OF_CROP, TEMPERATURE, SEASON, SOWN, HARVESTED,
            WATER_SOURCE, RELATIVE_HUMIDITY, k=3):
    """
    Returns a single crop prediction given the input features.

    Args:
        N                  (str | float): soil nitrogen
        P                  (str | float): soil phosphorus
        K                  (str | float): soil potassium
        TYPE_OF_CROP       (str):         e.g. 'cereals'
        TEMPERATURE        (str | float): average temperature (°C)
        SEASON             (str):         e.g. 'kharif'
        SOWN               (str):         sowing month, e.g. 'Jun'
        HARVESTED          (str):         harvest month, e.g. 'Oct'
        WATER_SOURCE       (str):         e.g. 'rainfed'
        RELATIVE_HUMIDITY  (str | float): relative humidity (%)
        k                  (int):         number of KNN neighbours (default 3)

    Returns:
        str: predicted crop name

    Raises:
        ValueError: if a categorical value is not in the stored OHE columns,
                    or if required DB artefacts are missing.
    """
    # --- load DB artefacts ---
    means, stds  = _get_scaler_params()
    ohe_cols     = _get_ohe_cols()
    X_train, y_train = _get_training_data()

    # --- build continuous feature vector (same order as _CONTINUOUS_COLS) ---
    x_cont = np.array([
        float(_CROPDURATION_AVG),
        float(TEMPERATURE),
        float(_WATERREQUIRED_AVG),
        float(RELATIVE_HUMIDITY),
        float(N),
        float(P),
        float(K),
    ])

    # scale using training statistics
    x_scaled = (x_cont - means) / stds  # shape (n_continuous,)

    # --- build OHE vector ---
    ohe_input = np.zeros(len(ohe_cols), dtype=float)

    categorical_inputs = {
        'TYPE_OF_CROP': TYPE_OF_CROP,
        'SEASON':       SEASON,
        'SOWN':         SOWN,
        'HARVESTED':    HARVESTED,
        'WATER_SOURCE': WATER_SOURCE,
    }

    for prefix, value in categorical_inputs.items():
        col_name = f'{prefix}_{value}'
        if col_name not in ohe_cols:
            raise ValueError(
                f"Unknown value '{value}' for '{prefix}'. "
                f"Expected one of: {[c for c in ohe_cols if c.startswith(prefix)]}"
            )
        ohe_input[ohe_cols.index(col_name)] = 1.0

    # concatenate and predict
    new_X = np.concatenate([x_scaled, ohe_input]).reshape(1, -1)  # (1, n_features)

    y_pred, _ = _knn_cos(X_train, y_train, new_X, k)
    prediction = str(y_pred[0])

    current_app.logger.info(
        f'model03.predict(N={N}, P={P}, K={K}, TYPE_OF_CROP={TYPE_OF_CROP}, '
        f'TEMP={TEMPERATURE}, SEASON={SEASON}, k={k}) -> {prediction}'
    )
    return prediction


def get_observations_with_predictions(k=5):
    """
    Fetches the full crop dataset from the DB, runs leave-one-out-style
    KNN predictions (using all training rows), and returns the results.
    Used by the admin accuracy / confusion-matrix page.

    Args:
        k (int): number of neighbours (default 3)

    Returns:
        list[dict]: one dict per row, with keys:
            crop_label, predicted_label, correct (bool),
            plus the original feature columns
    """
    means, stds  = _get_scaler_params()
    ohe_cols     = _get_ohe_cols()
    X_train, y_train = _get_training_data()

    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(
            'SELECT * FROM model3_observations ORDER BY row_id ASC'
        )
        rows = cursor.fetchall()

    results = []
    for row in rows:
        try:
            pred = predict(
                N                 = row['N'],
                P                 = row['P'],
                K                 = row['K'],
                TYPE_OF_CROP      = row['TYPE_OF_CROP'],
                TEMPERATURE       = row['TEMPERATURE'],
                SEASON            = row['SEASON'],
                SOWN              = row['SOWN'],
                HARVESTED         = row['HARVESTED'],
                WATER_SOURCE      = row['WATER_SOURCE'],
                RELATIVE_HUMIDITY = row['RELATIVE_HUMIDITY'],
                k                 = k,
            )
        except ValueError as exc:
            current_app.logger.warning(f'model03 skip row {row.get("row_id")}: {exc}')
            continue

        results.append({
            'row_id':          row.get('row_id'),
            'crop_label':      row['CROPS'],
            'predicted_label': pred,
            'correct':         row['CROPS'] == pred,
            'N':               row['N'],
            'P':               row['P'],
            'K':               row['K'],
            'TYPE_OF_CROP':    row['TYPE_OF_CROP'],
            'TEMPERATURE':     row['TEMPERATURE'],
            'SEASON':          row['SEASON'],
            'SOWN':            row['SOWN'],
            'HARVESTED':       row['HARVESTED'],
            'WATER_SOURCE':    row['WATER_SOURCE'],
            'RELATIVE_HUMIDITY': row['RELATIVE_HUMIDITY'],
        })

    return results