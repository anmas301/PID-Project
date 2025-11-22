"""
Model Module
Machine Learning model untuk prediksi risiko ISPA berdasarkan kualitas udara
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    mean_squared_error, r2_score, accuracy_score
)
import joblib
import sys
from pathlib import Path
import logging
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATA_PATHS, MODEL_CONFIG, RISK_THRESHOLDS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ISPARiskPredictor:
    """Model untuk prediksi risiko ISPA"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = []
        self.model_type = 'classification'  # or 'regression'
        self.data_paths = DATA_PATHS
        self.model_config = MODEL_CONFIG
    
    def prepare_features(self, df):
        """
        Prepare features untuk modeling
        
        Args:
            df: dataframe with raw data
            
        Returns:
            processed dataframe
        """
        df_model = df.copy()
        
        # Select relevant features
        potential_features = [
            'aqi', 'pm2_5', 'pm10', 'co', 'no2', 'o3', 'so2',
            'temp_c', 'humidity', 'wind_kph', 'pressure_mb',
            'hour', 'day_of_week', 'month', 'is_weekend'
        ]
        
        # Only keep columns that exist
        self.feature_columns = [col for col in potential_features if col in df_model.columns]
        
        # Handle missing values
        df_model[self.feature_columns] = df_model[self.feature_columns].fillna(
            df_model[self.feature_columns].median()
        )
        
        logger.info(f"Prepared {len(self.feature_columns)} features for modeling")
        return df_model
    
    def create_target_from_aqi(self, df):
        """
        Create target variable from AQI values
        Untuk classification: risk_category
        Untuk regression: synthetic ISPA risk score
        
        Args:
            df: dataframe with aqi column
            
        Returns:
            dataframe with target column
        """
        df_target = df.copy()
        
        if 'risk_category' in df_target.columns:
            # Use existing risk category
            df_target['target'] = df_target['risk_category']
        elif 'aqi' in df_target.columns:
            # Create risk category from AQI
            def categorize_aqi(aqi):
                if pd.isna(aqi):
                    return 'unknown'
                for category, (low, high) in RISK_THRESHOLDS.items():
                    if low <= aqi <= high:
                        return category
                return 'hazardous'
            
            df_target['target'] = df_target['aqi'].apply(categorize_aqi)
        else:
            logger.error("No AQI or risk_category column found")
            return df_target
        
        # Create synthetic ISPA risk score (0-100)
        # Higher AQI = higher ISPA risk
        if 'aqi' in df_target.columns:
            df_target['ispa_risk_score'] = df_target['aqi'].apply(
                lambda x: min(100, x * 0.2) if pd.notna(x) else 0
            )
            
            # Adjust based on weather conditions
            if 'humidity' in df_target.columns:
                # High humidity can increase respiratory issues
                df_target['ispa_risk_score'] += (df_target['humidity'] - 50) * 0.1
            
            if 'temp_c' in df_target.columns:
                # Extreme temperatures increase risk
                df_target['ispa_risk_score'] += np.abs(df_target['temp_c'] - 25) * 0.2
            
            # Normalize to 0-100
            df_target['ispa_risk_score'] = df_target['ispa_risk_score'].clip(0, 100)
        
        logger.info("Created target variables for modeling")
        return df_target
    
    def train_classification_model(self, X_train, y_train):
        """
        Train classification model untuk risk category prediction
        
        Args:
            X_train: training features
            y_train: training labels
            
        Returns:
            trained model
        """
        logger.info("Training classification model...")
        
        # Encode labels
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        
        # Initialize model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=self.model_config['random_state'],
            n_jobs=-1
        )
        
        # Train
        self.model.fit(X_train, y_train_encoded)
        
        # Cross-validation with adaptive folds
        n_samples = len(X_train)
        cv_folds = min(self.model_config['cv_folds'], n_samples)
        
        if cv_folds >= 2:
            try:
                cv_scores = cross_val_score(
                    self.model, X_train, y_train_encoded, 
                    cv=cv_folds
                )
                logger.info(f"CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
            except Exception as e:
                logger.warning(f"Cross-validation failed: {e}")
        else:
            logger.info("Skipping cross-validation (insufficient data)")
        
        self.model_type = 'classification'
        return self.model
    
    def train_regression_model(self, X_train, y_train):
        """
        Train regression model untuk ISPA risk score prediction
        
        Args:
            X_train: training features
            y_train: training target values
            
        Returns:
            trained model
        """
        logger.info("Training regression model...")
        
        # Initialize model
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=self.model_config['random_state']
        )
        
        # Train
        self.model.fit(X_train, y_train)
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_train, y_train,
            cv=self.model_config['cv_folds'],
            scoring='r2'
        )
        
        logger.info(f"CV R2 Score: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
        
        self.model_type = 'regression'
        return self.model
    
    def evaluate_model(self, X_test, y_test):
        """
        Evaluate trained model
        
        Args:
            X_test: test features
            y_test: test labels/values
            
        Returns:
            evaluation metrics dict
        """
        if self.model is None:
            logger.error("Model not trained yet")
            return {}
        
        logger.info("Evaluating model...")
        
        if self.model_type == 'classification':
            y_test_encoded = self.label_encoder.transform(y_test)
            y_pred = self.model.predict(X_test)
            
            accuracy = accuracy_score(y_test_encoded, y_pred)
            report = classification_report(
                y_test_encoded, y_pred,
                target_names=self.label_encoder.classes_,
                output_dict=True
            )
            
            metrics = {
                'type': 'classification',
                'accuracy': accuracy,
                'classification_report': report
            }
            
            logger.info(f"Test Accuracy: {accuracy:.3f}")
            
        else:  # regression
            y_pred = self.model.predict(X_test)
            
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)
            
            metrics = {
                'type': 'regression',
                'mse': mse,
                'rmse': rmse,
                'r2_score': r2
            }
            
            logger.info(f"Test RMSE: {rmse:.3f}, R2: {r2:.3f}")
        
        return metrics
    
    def get_feature_importance(self):
        """
        Get feature importance from trained model
        
        Returns:
            dataframe with feature importance
        """
        if self.model is None:
            logger.error("Model not trained yet")
            return pd.DataFrame()
        
        if hasattr(self.model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': self.model.feature_importances_
            })
            importance_df = importance_df.sort_values('importance', ascending=False)
            
            logger.info("Feature importance calculated")
            return importance_df
        else:
            logger.warning("Model does not support feature importance")
            return pd.DataFrame()
    
    def predict(self, X):
        """
        Make predictions on new data
        
        Args:
            X: features dataframe
            
        Returns:
            predictions
        """
        if self.model is None:
            logger.error("Model not trained yet")
            return None
        
        # Scale features
        X_scaled = self.scaler.transform(X[self.feature_columns])
        
        # Predict
        predictions = self.model.predict(X_scaled)
        
        if self.model_type == 'classification':
            # Decode labels
            predictions = self.label_encoder.inverse_transform(predictions)
        
        return predictions
    
    def save_model(self, filename='ispa_risk_model.joblib'):
        """
        Save trained model to file
        
        Args:
            filename: output filename
        """
        if self.model is None:
            logger.error("No model to save")
            return
        
        model_path = self.data_paths['models'] / filename
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder if self.model_type == 'classification' else None,
            'feature_columns': self.feature_columns,
            'model_type': self.model_type
        }
        
        joblib.dump(model_data, model_path)
        logger.info(f"Model saved to {model_path}")
    
    def load_model(self, filename='ispa_risk_model.joblib'):
        """
        Load trained model from file
        
        Args:
            filename: model filename
        """
        model_path = self.data_paths['models'] / filename
        
        if not model_path.exists():
            logger.error(f"Model file not found: {model_path}")
            return False
        
        model_data = joblib.load(model_path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data.get('label_encoder')
        self.feature_columns = model_data['feature_columns']
        self.model_type = model_data['model_type']
        
        logger.info(f"Model loaded from {model_path}")
        return True
    
    def predict_future_risk(self, current_data, days_ahead=7):
        """
        Predict future ISPA risk for next N days
        
        Args:
            current_data: current dataframe with latest measurements
            days_ahead: number of days to predict ahead
            
        Returns:
            dataframe with predictions
        """
        logger.info(f"Predicting ISPA risk for next {days_ahead} days...")
        
        predictions = []
        
        # For each location, predict future risk
        for location in current_data['location'].unique():
            location_data = current_data[current_data['location'] == location].iloc[-1]
            
            for day in range(1, days_ahead + 1):
                pred_date = pd.Timestamp.now() + pd.Timedelta(days=day)
                
                # Create features for prediction (using current values as baseline)
                pred_features = {
                    'aqi': location_data.get('aqi', 50),
                    'pm2_5': location_data.get('pm2_5', 10),
                    'pm10': location_data.get('pm10', 20),
                    'temp_c': location_data.get('temp_c', 25),
                    'humidity': location_data.get('humidity', 80),
                    'wind_kph': location_data.get('wind_kph', 10),
                    'pressure_mb': location_data.get('pressure_mb', 1010),
                    'hour': pred_date.hour,
                    'day_of_week': pred_date.dayofweek,
                    'month': pred_date.month,
                    'is_weekend': 1 if pred_date.dayofweek >= 5 else 0
                }
                
                # Add derived features
                if 'pm2_5' in pred_features and 'pm10' in pred_features:
                    pred_features['pm_ratio'] = pred_features['pm2_5'] / (pred_features['pm10'] + 1)
                
                if 'temp_c' in pred_features and 'humidity' in pred_features:
                    pred_features['heat_index'] = pred_features['temp_c'] + (0.5 * pred_features['humidity'] / 100)
                
                # Calculate ISPA risk score
                ispa_risk = min(100, pred_features['aqi'] * 0.2)
                ispa_risk += (pred_features['humidity'] - 50) * 0.1
                ispa_risk += abs(pred_features['temp_c'] - 25) * 0.2
                ispa_risk = max(0, min(100, ispa_risk))
                
                # Determine risk category
                if ispa_risk < 20:
                    risk_cat = 'Low Risk'
                elif ispa_risk < 40:
                    risk_cat = 'Moderate Risk'
                elif ispa_risk < 60:
                    risk_cat = 'High Risk'
                else:
                    risk_cat = 'Very High Risk'
                
                predictions.append({
                    'location': location,
                    'date': pred_date.date(),
                    'predicted_ispa_risk': round(ispa_risk, 2),
                    'risk_category': risk_cat,
                    'predicted_aqi': pred_features['aqi'],
                    'predicted_pm2_5': pred_features['pm2_5']
                })
        
        pred_df = pd.DataFrame(predictions)
        logger.info(f"Generated {len(pred_df)} predictions")
        
        return pred_df
    
    def train_pipeline(self, df, target_type='classification'):
        """
        Complete training pipeline
        
        Args:
            df: training dataframe
            target_type: 'classification' or 'regression'
            
        Returns:
            evaluation metrics
        """
        logger.info("Starting model training pipeline...")
        
        # Prepare features
        df_prepared = self.prepare_features(df)
        df_prepared = self.create_target_from_aqi(df_prepared)
        
        # Select target
        if target_type == 'classification':
            target_col = 'target'
        else:
            target_col = 'ispa_risk_score'
        
        # Remove rows with missing target
        df_model = df_prepared.dropna(subset=[target_col])
        
        if len(df_model) == 0:
            logger.error("No valid data for training")
            return {}
        
        # Check if we have enough data for cross-validation
        min_samples = max(2, self.model_config['cv_folds'])
        if len(df_model) < min_samples:
            logger.warning(f"Not enough data ({len(df_model)} samples) for cross-validation. Skipping CV.")
            return {}
        
        # Split data
        X = df_model[self.feature_columns]
        y = df_model[target_col]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=min(0.2, 1/len(df_model)),
            random_state=self.model_config['random_state']
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        if target_type == 'classification':
            self.train_classification_model(X_train_scaled, y_train)
        else:
            self.train_regression_model(X_train_scaled, y_train)
        
        # Evaluate
        metrics = self.evaluate_model(X_test_scaled, y_test)
        
        # Feature importance
        feature_importance = self.get_feature_importance()
        if not feature_importance.empty:
            importance_path = self.data_paths['output'] / 'feature_importance.csv'
            feature_importance.to_csv(importance_path, index=False)
            logger.info(f"Feature importance saved to {importance_path}")
        
        # Save model
        self.save_model()
        
        logger.info("Model training pipeline completed!")
        return metrics


if __name__ == "__main__":
    # Test model module
    print("Testing model module...")
    print("Run this through the main pipeline with actual data")
