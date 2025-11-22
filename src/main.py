"""
Main Pipeline Orchestration
Menjalankan seluruh pipeline dari ingestion hingga model training
"""
import sys
from pathlib import Path
import logging
import argparse
from datetime import datetime
import json
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.ingestion import DataIngestion
from src.transformation import DataTransformation
from src.storage import DataStorage
from src.batch_processing import BatchProcessor
from src.model import ISPARiskPredictor
from config.config import DATA_PATHS, LOGGING_CONFIG

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    datefmt=LOGGING_CONFIG['date_format']
)
logger = logging.getLogger(__name__)


class Pipeline:
    """Main pipeline orchestration class"""
    
    def __init__(self, use_database=False):
        """
        Initialize pipeline
        
        Args:
            use_database: whether to store data in database
        """
        self.use_database = use_database
        self.ingestion = DataIngestion()
        self.transformation = DataTransformation()
        self.batch_processor = BatchProcessor()
        self.model = ISPARiskPredictor()
        
        if use_database:
            self.storage = DataStorage(use_postgres=True, use_mongodb=True)
        else:
            self.storage = None
        
        self.results = {}
    
    def run_ingestion(self):
        """Run data ingestion step"""
        logger.info("=" * 80)
        logger.info("STEP 1: DATA INGESTION")
        logger.info("=" * 80)
        
        ingestion_result = self.ingestion.run_ingestion()
        self.results['ingestion'] = ingestion_result
        
        logger.info("✓ Data ingestion completed")
        return ingestion_result
    
    def run_transformation(self, ingestion_result):
        """Run data transformation step"""
        logger.info("=" * 80)
        logger.info("STEP 2: DATA TRANSFORMATION")
        logger.info("=" * 80)
        
        transformation_result = self.transformation.transform_all(
            ingestion_result['api_data'],
            ingestion_result['csv_datasets']
        )
        self.results['transformation'] = transformation_result
        
        logger.info("✓ Data transformation completed")
        return transformation_result
    
    def run_storage(self, transformation_result):
        """Run data storage step"""
        if not self.use_database or self.storage is None:
            logger.info("Database storage skipped (not enabled)")
            return
        
        logger.info("=" * 80)
        logger.info("STEP 3: DATA STORAGE")
        logger.info("=" * 80)
        
        # Connect to databases
        if self.storage.connect_all():
            # Store transformed data
            self.storage.store_all_data(transformation_result)
            logger.info("✓ Data storage completed")
        else:
            logger.warning("⚠ Database connection failed, data not stored")
    
    def run_batch_processing(self, transformation_result):
        """Run batch processing step"""
        logger.info("=" * 80)
        logger.info("STEP 4: BATCH PROCESSING & ISPA ANALYSIS")
        logger.info("=" * 80)
        
        # Get real-time data for batch processing
        real_time_data = transformation_result.get('real_time_data')
        
        if real_time_data is not None and not real_time_data.empty:
            batch_result = self.batch_processor.run_batch_processing(real_time_data)
            self.results['batch_processing'] = batch_result
            
            # Generate future predictions
            logger.info("Generating future ISPA risk predictions...")
            try:
                future_predictions = self.model.predict_future_risk(real_time_data, days_ahead=7)
                
                # Save predictions
                pred_path = self.model.data_paths['output'] / 'future_ispa_predictions.csv'
                future_predictions.to_csv(pred_path, index=False)
                logger.info(f"Future predictions saved to {pred_path}")
                
                self.results['predictions'] = future_predictions
                
                # Generate alerts for high-risk predictions
                high_risk = future_predictions[future_predictions['predicted_ispa_risk'] > 60]
                if not high_risk.empty:
                    logger.warning(f"⚠️  {len(high_risk)} high-risk predictions found!")
                    alert_path = self.model.data_paths['output'] / 'risk_alerts.json'
                    high_risk.to_json(alert_path, orient='records', indent=2)
                    logger.info(f"Risk alerts saved to {alert_path}")
                
            except Exception as e:
                logger.error(f"Error generating predictions: {e}")
            
            logger.info("✓ Batch processing completed")
            return batch_result
        else:
            logger.warning("⚠ No real-time data available for batch processing")
            return {}
    
    def run_model_training(self, transformation_result, target_type='classification'):
        """Run model training step"""
        logger.info("=" * 80)
        logger.info("STEP 5: MODEL TRAINING")
        logger.info("=" * 80)
        
        # Get data for model training
        real_time_data = transformation_result.get('real_time_data')
        
        if real_time_data is not None and not real_time_data.empty:
            # Train model
            metrics = self.model.train_pipeline(real_time_data, target_type=target_type)
            self.results['model_training'] = metrics
            logger.info("✓ Model training completed")
            return metrics
        else:
            logger.warning("⚠ No data available for model training")
            return {}
    
    def generate_report(self):
        """Generate pipeline execution report"""
        logger.info("=" * 80)
        logger.info("PIPELINE EXECUTION REPORT")
        logger.info("=" * 80)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'pipeline_steps': {},
            'summary': {}
        }
        
        # Ingestion summary
        if 'ingestion' in self.results:
            ingestion = self.results['ingestion']
            report['pipeline_steps']['ingestion'] = {
                'api_pollution_records': len(ingestion['api_data'].get('pollution', [])),
                'api_weather_records': len(ingestion['api_data'].get('weather', [])),
                'csv_datasets_loaded': len(ingestion.get('csv_datasets', {}))
            }
        
        # Transformation summary
        if 'transformation' in self.results:
            transformation = self.results['transformation']
            report['pipeline_steps']['transformation'] = {
                'datasets_transformed': len(transformation)
            }
            
            if 'real_time_data' in transformation:
                report['pipeline_steps']['transformation']['real_time_records'] = len(
                    transformation['real_time_data']
                )
        
        # Batch processing summary
        if 'batch_processing' in self.results:
            batch = self.results['batch_processing']
            report['pipeline_steps']['batch_processing'] = {
                'daily_records': len(batch.get('daily', pd.DataFrame())),
                'weekly_records': len(batch.get('weekly', pd.DataFrame())),
                'monthly_records': len(batch.get('monthly', pd.DataFrame())),
                'anomalies_detected': batch.get('anomalies', pd.DataFrame())['is_anomaly'].sum() 
                    if 'anomalies' in batch and not batch['anomalies'].empty else 0
            }
            
            # ISPA correlation analysis
            if 'ispa_correlation' in batch:
                ispa_corr = batch['ispa_correlation']
                report['pipeline_steps']['ispa_analysis'] = {
                    'high_risk_locations': len(ispa_corr.get('high_risk_locations', [])),
                    'correlations_calculated': len(ispa_corr.get('pollution_ispa_correlation', {})),
                    'recommendations': len(ispa_corr.get('recommendations', []))
                }
        
        # Predictions summary
        if 'predictions' in self.results:
            predictions = self.results['predictions']
            report['pipeline_steps']['predictions'] = {
                'total_predictions': len(predictions),
                'locations': predictions['location'].nunique(),
                'days_ahead': predictions['date'].nunique(),
                'high_risk_predictions': len(predictions[predictions['predicted_ispa_risk'] > 60]),
                'moderate_risk_predictions': len(predictions[
                    (predictions['predicted_ispa_risk'] > 40) & 
                    (predictions['predicted_ispa_risk'] <= 60)
                ])
            }
        
        # Model training summary
        if 'model_training' in self.results:
            report['pipeline_steps']['model_training'] = self.results['model_training']
        
        # Overall summary
        report['summary']['status'] = 'SUCCESS'
        report['summary']['total_steps_completed'] = len(report['pipeline_steps'])
        
        # Save report
        report_path = DATA_PATHS['output'] / f'pipeline_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Pipeline report saved to: {report_path}")
        
        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        for step, details in report['pipeline_steps'].items():
            logger.info(f"\n{step.upper()}:")
            for key, value in details.items():
                logger.info(f"  - {key}: {value}")
        logger.info("=" * 80)
        
        return report
    
    def run_full_pipeline(self, train_model=True, model_type='classification'):
        """
        Run the complete pipeline
        
        Args:
            train_model: whether to train ML model
            model_type: 'classification' or 'regression'
        """
        logger.info("\n" + "=" * 80)
        logger.info("STARTING FULL PIPELINE EXECUTION")
        logger.info("=" * 80 + "\n")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Ingestion
            ingestion_result = self.run_ingestion()
            
            # Step 2: Transformation
            transformation_result = self.run_transformation(ingestion_result)
            
            # Step 3: Storage (optional)
            if self.use_database:
                self.run_storage(transformation_result)
            
            # Step 4: Batch Processing
            self.run_batch_processing(transformation_result)
            
            # Step 5: Model Training (optional)
            if train_model:
                self.run_model_training(transformation_result, target_type=model_type)
            
            # Generate report
            report = self.generate_report()
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.info("\n" + "=" * 80)
            logger.info(f"✓ PIPELINE COMPLETED SUCCESSFULLY in {execution_time:.2f} seconds")
            logger.info("=" * 80 + "\n")
            
            return report
            
        except Exception as e:
            logger.error(f"\n✗ PIPELINE FAILED: {e}", exc_info=True)
            raise
        
        finally:
            # Cleanup
            if self.storage:
                self.storage.close_all()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run ISPA Risk Monitoring Pipeline')
    
    parser.add_argument(
        '--use-database',
        action='store_true',
        help='Store data in PostgreSQL/MongoDB'
    )
    
    parser.add_argument(
        '--skip-model',
        action='store_true',
        help='Skip model training'
    )
    
    parser.add_argument(
        '--model-type',
        choices=['classification', 'regression'],
        default='classification',
        help='Type of model to train'
    )
    
    parser.add_argument(
        '--step',
        choices=['ingestion', 'transformation', 'batch', 'model', 'all'],
        default='all',
        help='Run specific pipeline step'
    )
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = Pipeline(use_database=args.use_database)
    
    # Run pipeline based on arguments
    if args.step == 'all':
        pipeline.run_full_pipeline(
            train_model=not args.skip_model,
            model_type=args.model_type
        )
    elif args.step == 'ingestion':
        pipeline.run_ingestion()
    elif args.step == 'transformation':
        ingestion_result = pipeline.run_ingestion()
        pipeline.run_transformation(ingestion_result)
    elif args.step == 'batch':
        ingestion_result = pipeline.run_ingestion()
        transformation_result = pipeline.run_transformation(ingestion_result)
        pipeline.run_batch_processing(transformation_result)
    elif args.step == 'model':
        ingestion_result = pipeline.run_ingestion()
        transformation_result = pipeline.run_transformation(ingestion_result)
        pipeline.run_model_training(transformation_result, target_type=args.model_type)


if __name__ == "__main__":
    main()
