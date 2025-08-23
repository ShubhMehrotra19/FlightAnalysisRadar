import os
import sys
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
import json

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
    def __init__(self, config_path_or_dict=None):
        """
        Initialize pipeline with either a config path or config dictionary
        
        Args:
            config_path_or_dict: Either a path to config file (string/Path) or config dictionary
        """
        # Fix the main issue: handle both config path and config dict
        if isinstance(config_path_or_dict, dict):
            # If it's already a config dictionary, use it directly
            self.config = config_path_or_dict
            logger.info("Using provided config dictionary")
        else:
            # If it's a path or None, load config from file
            self.config = self._load_config(config_path_or_dict)
            logger.info(f"Loaded config from: {config_path_or_dict or 'default settings'}")
        
        # Set up directory paths
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.reports_dir = self.project_root / "reports"
        self.notebooks_dir = self.project_root / "notebooks"
        
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Reports directory: {self.reports_dir}")
        
        # Add reports_dir to config for dashboard generator
        self.config['reports_dir'] = str(self.reports_dir)
        
        # Ensure directories exist
        self._create_directories()
        
        # Initialize components after config is properly set
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize pipeline components"""
        try:
            # Import components here to avoid circular imports
            from ..data_processor import DataProcessor
            from ..analyzer import FlightAnalyzer
            from ..visualizer import Visualizer
            from ..dashboard_generator import DashboardGenerator
            
            # Pipeline components
            self.data_processor = DataProcessor(self.config, self.data_dir)
            self.analyzer = FlightAnalyzer(self.config)
            self.visualizer = Visualizer(self.reports_dir)
            self.dashboard_generator = DashboardGenerator(self.config)
            
            logger.info("✅ All pipeline components initialized successfully")
            
        except ImportError as e:
            logger.error(f"❌ Failed to import pipeline components: {str(e)}")
            # Create mock components for testing
            logger.warning("⚠️  Using mock components for testing")
            self.data_processor = None
            self.analyzer = None
            self.visualizer = None
            self.dashboard_generator = None
        
    def _load_config(self, config_path):
        """Load pipeline configuration from file or use defaults"""
        default_config = {
            "data_source": "429e6e3f-281d-4e4c-b00a-92fb020cb2fcFlight_Data.xlsx",
            "analysis_params": {
                "delay_threshold": 15,
                "cascade_factor": 0.4,
                "simulation_delay_reduction": 5,
                "peak_hour_shift": 1
            },
            "output_formats": ["csv", "json", "html"],
            "dashboard_port": 8050,
            "generate_standalone_dashboard": True
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                logger.info(f"✅ Loaded custom config from: {config_path}")
            except Exception as e:
                logger.warning(f"⚠️  Could not load config file {config_path}: {str(e)}")
                logger.info("Using default configuration")
        else:
            logger.info("Using default configuration")
        
        return default_config
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [self.data_dir, self.reports_dir, self.notebooks_dir]
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"✅ Directory ready: {directory}")
            except Exception as e:
                logger.error(f"❌ Could not create directory {directory}: {str(e)}")
                raise
    
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
        logger.info(f"Pipeline steps: {steps}")
        
        results = {}
        raw_data = None
        cleaned_data = None
        analysis_results = None
        
        try:
            # Check if components are available
            if not all([self.data_processor, self.analyzer, self.visualizer, self.dashboard_generator]):
                raise RuntimeError("Pipeline components not properly initialized")
            
            # Step 1: Data Extraction and Loading
            if 'extract' in steps:
                logger.info("📂 Step 1: Data Extraction")
                raw_data = self.data_processor.extract_data()
                results['raw_data_shape'] = raw_data.shape
                logger.info(f"✅ Extracted {raw_data.shape[0]} records")
            
            # Step 2: Data Transformation and Cleaning
            if 'transform' in steps:
                logger.info("🔧 Step 2: Data Transformation")
                if raw_data is None:
                    raw_data = self.data_processor.extract_data()
                cleaned_data = self.data_processor.transform_data(raw_data)
                results['cleaned_data_shape'] = cleaned_data.shape
                logger.info(f"✅ Cleaned data: {cleaned_data.shape[0]} records, {cleaned_data.shape[1]} features")
            
            # Step 3: Analysis
            if 'analyze' in steps:
                logger.info("📊 Step 3: Flight Analysis")
                if cleaned_data is None:
                    if raw_data is None:
                        raw_data = self.data_processor.extract_data()
                    cleaned_data = self.data_processor.transform_data(raw_data)
                analysis_results = self.analyzer.run_analysis(cleaned_data)
                results['analysis'] = analysis_results
                logger.info("✅ Analysis completed")
            
            # Step 4: Visualization
            if 'visualize' in steps:
                logger.info("📈 Step 4: Visualization Generation")
                if cleaned_data is None or analysis_results is None:
                    if raw_data is None:
                        raw_data = self.data_processor.extract_data()
                    if cleaned_data is None:
                        cleaned_data = self.data_processor.transform_data(raw_data)
                    if analysis_results is None:
                        analysis_results = self.analyzer.run_analysis(cleaned_data)
                
                viz_results = self.visualizer.generate_reports(cleaned_data, analysis_results)
                results['visualizations'] = viz_results
                logger.info("✅ Visualizations generated")
            
            # Step 5: Dashboard
            if 'dashboard' in steps:
                logger.info("🖥️  Step 5: Interactive Dashboard Generation")
                if cleaned_data is None or analysis_results is None:
                    if raw_data is None:
                        raw_data = self.data_processor.extract_data()
                    if cleaned_data is None:
                        cleaned_data = self.data_processor.transform_data(raw_data)
                    if analysis_results is None:
                        analysis_results = self.analyzer.run_analysis(cleaned_data)
                
                dashboard_path = self.dashboard_generator.create_dashboard(cleaned_data, analysis_results)
                results['dashboard_path'] = dashboard_path
                logger.info(f"✅ Interactive Dashboard created at: {dashboard_path}")
                logger.info("📱 Open the HTML file in your web browser to interact with the dashboard")
            
            # Generate final report
            self._generate_pipeline_report(results)
            
            logger.info("🎉 Pipeline execution completed successfully!")
            return results
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _generate_pipeline_report(self, results):
        """Generate pipeline execution summary"""
        report = {
            "execution_time": datetime.now().isoformat(),
            "pipeline_results": results,
            "status": "completed",
            "files_generated": []
        }
        
        # Add generated files to report
        if 'dashboard_path' in results:
            report['files_generated'].append(results['dashboard_path'])
        if 'visualizations' in results:
            viz_results = results['visualizations']
            if 'static_plots' in viz_results:
                report['files_generated'].extend(viz_results['static_plots'])
            if 'interactive_plots' in viz_results:
                report['files_generated'].extend(viz_results['interactive_plots'])
            if 'summary_report' in viz_results:
                report['files_generated'].append(viz_results['summary_report'])
        
        try:
            report_path = self.reports_dir / "pipeline_report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"📋 Pipeline report saved to: {report_path}")
        except Exception as e:
            logger.warning(f"⚠️  Could not save pipeline report: {str(e)}")

    def get_dashboard_url(self):
        """Get the dashboard file path for direct access"""
        dashboard_path = self.reports_dir / "flight_dashboard.html"
        if dashboard_path.exists():
            return str(dashboard_path)
        return None


# Test function for debugging
def test_pipeline_initialization():
    """Test pipeline initialization with different parameter types"""
    print("🧪 Testing Pipeline Initialization")
    print("="*50)
    
    # Test 1: Initialize with None
    try:
        print("Test 1: Initialize with None")
        pipeline1 = FlightDataPipeline(None)
        print("✅ Success with None parameter")
    except Exception as e:
        print(f"❌ Failed with None: {str(e)}")
    
    # Test 2: Initialize with config dict
    try:
        print("\nTest 2: Initialize with config dictionary")
        test_config = {
            "data_source": "test_data.xlsx",
            "analysis_params": {"delay_threshold": 15}
        }
        pipeline2 = FlightDataPipeline(test_config)
        print("✅ Success with config dictionary")
    except Exception as e:
        print(f"❌ Failed with config dict: {str(e)}")
    
    # Test 3: Initialize with non-existent path
    try:
        print("\nTest 3: Initialize with non-existent config path")
        pipeline3 = FlightDataPipeline("non_existent_config.json")
        print("✅ Success with non-existent path (should use defaults)")
    except Exception as e:
        print(f"❌ Failed with path: {str(e)}")


if __name__ == "__main__":
    test_pipeline_initialization()