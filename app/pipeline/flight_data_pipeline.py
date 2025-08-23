import os
import sys
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
import json

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from data_processor import DataProcessor
from app.analyzer import FlightAnalyzer
from app.visualizer import Visualizer
from app.dashboard_generator import DashboardGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FlightDataPipeline:
    """
    Main pipeline orchestrator for flight data analysis
    """
    def __init__(self, config=None):
        self.config = self._load_config(config)
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.reports_dir = self.project_root / "reports"
        self.notebooks_dir = self.project_root / "notebooks"
        
        # Ensure directories exist
        self._create_directories()
        
        # Pipeline components
        self.data_processor = DataProcessor(self.config, self.data_dir)
        self.analyzer = FlightAnalyzer(self.config)
        self.visualizer = Visualizer(self.reports_dir)
        self.dashboard_generator = DashboardGenerator(self.config)
        
    def _load_config(self, config):
        """Load pipeline configuration"""
        default_config = {
            "data_source": "429e6e3f-281d-4e4c-b00a-92fb020cb2fcFlight_Data.xlsx",
            "analysis_params": {
                "delay_threshold": 15,
                "cascade_factor": 0.4,
                "simulation_delay_reduction": 5,
                "peak_hour_shift": 1
            },
            "output_formats": ["csv", "json", "html"],
            "dashboard_port": 8050
        }
        
        if config:
            if isinstance(config, str) and os.path.exists(config):
                with open(config, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            elif isinstance(config, dict):
                default_config.update(config)
        
        return default_config
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [self.data_dir, self.reports_dir, self.notebooks_dir]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def run_pipeline(self, steps=None):
        """
        Execute the complete pipeline
        
        Args:
            steps (list): Specific steps to run. If None, runs all steps.
                         Options: ['extract', 'transform', 'analyze', 'visualize', 'dashboard']
        """
        if steps is None:
            steps = ['extract', 'transform', 'analyze', 'visualize', 'dashboard']
        
        logger.info("🚀 Starting Flight Data Analysis Pipeline")
        
        results = {}
        
        try:
            # Step 1: Data Extraction and Loading
            if 'extract' in steps:
                logger.info("📂 Step 1: Data Extraction")
                raw_data = self.data_processor.extract_data()
                results['raw_data_shape'] = raw_data.shape
                logger.info(f"✅ Extracted {raw_data.shape[0]} records")
            
            # Step 2: Data Transformation and Cleaning
            if 'transform' in steps:
                logger.info("🔧 Step 2: Data Transformation")
                cleaned_data = self.data_processor.transform_data(raw_data)
                results['cleaned_data_shape'] = cleaned_data.shape
                logger.info(f"✅ Cleaned data: {cleaned_data.shape[0]} records, {cleaned_data.shape[1]} features")
            
            # Step 3: Analysis
            if 'analyze' in steps:
                logger.info("📊 Step 3: Flight Analysis")
                analysis_results = self.analyzer.run_analysis(cleaned_data)
                results['analysis'] = analysis_results
                logger.info("✅ Analysis completed")
            
            # Step 4: Visualization
            if 'visualize' in steps:
                logger.info("📈 Step 4: Visualization Generation")
                viz_results = self.visualizer.generate_reports(cleaned_data, analysis_results)
                results['visualizations'] = viz_results
                logger.info("✅ Visualizations generated")
            
            # Step 5: Dashboard
            if 'dashboard' in steps:
                logger.info("🖥  Step 5: Dashboard Generation")
                dashboard_url = self.dashboard_generator.create_dashboard(cleaned_data, analysis_results)
                results['dashboard_url'] = dashboard_url
                logger.info(f"✅ Dashboard available at: {dashboard_url}")
            
            # Generate final report
            self._generate_pipeline_report(results)
            
            logger.info("🎉 Pipeline execution completed successfully!")
            return results
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
            raise

    def _generate_pipeline_report(self, results):
        """Generate pipeline execution summary"""
        report = {
            "execution_time": datetime.now().isoformat(),
            "pipeline_results": results,
            "status": "completed"
        }
        
        report_path = self.reports_dir / "pipeline_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📋 Pipeline report saved to: {report_path}")