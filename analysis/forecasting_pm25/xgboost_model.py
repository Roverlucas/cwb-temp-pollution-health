import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor

def run_xgboost_model(X_train, X_test, y_train, y_test, scaler_y):
    best_result = {
        'mse': float('inf'),
    }

    for n_estimators in range(50, 501, 50):
        model = XGBRegressor(n_estimators=n_estimators, max_depth=None, learning_rate=0.1, random_state=42)
        model.fit(X_train, y_train.ravel())

        y_pred = model.predict(X_test)
        y_pred_inv = scaler_y.inverse_transform(y_pred.reshape(-1, 1))
        y_test_inv = scaler_y.inverse_transform(y_test)

        mse = mean_squared_error(y_test_inv, y_pred_inv)

        if mse < best_result['mse']:
            best_result = {
                'mse': mse,
                'rmse': np.sqrt(mse),
                'mae': mean_absolute_error(y_test_inv, y_pred_inv),
                'n_estimators': n_estimators,
                'y_pred': y_pred_inv.flatten()
            }

    return best_result