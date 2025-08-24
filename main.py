import sys
import argparse
import webbrowser
import os
from pathlib import Path
import traceback

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))


def main():
    """Main execution function with enhanced dashboard support"""
    parser = argparse.ArgumentParser(description='Enhanced Flight Data Analysis Pipeline with Multi-Feature Dashboard')
    parser.add_argument('--config', '-c', type=str, help='Configuration file path')
    parser.add_argument('--steps', '-s', nargs='+', 
                       choices=['extract', 'transform', 'analyze', 'visualize', 'dashboard'],
                       help='Pipeline steps to execute')
    parser.add_argument('--data-file', '-d', type=str, help='Override data file path')
    parser.add_argument('--output-dir', '-o', type=str, help='Override output directory')
    parser.add_argument('--open-dashboard', action='store_true', 
                       help='Automatically open dashboard in web browser')
    parser.add_argument('--dashboard-only', action='store_true',
                       help='Generate only the enhanced dashboard (runs extract, transform, analyze, dashboard)')
    parser.add_argument('--feature', '-f', choices=['dashboard', 'analytics', 'scheduling', 'predictions', 'nlp'],
                       help='Focus on specific dashboard feature')
    
    args = parser.parse_args()
    
    # Import here to avoid issues if modules aren't ready
    try:
        from app.pipeline.flight_data_pipeline import FlightDataPipeline
        from config import Config
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure you're running from the project root directory and all dependencies are installed.")
        print("\n🔍 Debug info:")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Project root: {PROJECT_ROOT}")
        print(f"   Python path: {sys.path}")
        traceback.print_exc()
        sys.exit(1)
    
    # Load configuration
    try:
        config_dict = Config.load(args.config)
        print(f"✅ Configuration loaded successfully")
        print(f"   Config type: {type(config_dict)}")
        
        # Override config with command line arguments
        if args.data_file:
            config_dict['data_source'] = args.data_file
            print(f"   Data source overridden to: {args.data_file}")
        
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
    
    # Set steps based on arguments
    if args.dashboard_only:
        steps = ['extract', 'transform', 'analyze', 'dashboard']
    else:
        steps = args.steps
    
    print(f"📋 Pipeline steps to execute: {steps}")
    
    # Initialize pipeline with enhanced dashboard
    try:
        print(f"🔧 Initializing enhanced pipeline...")
        
        # Use enhanced dashboard generator
        pipeline = EnhancedFlightDataPipeline(config_dict)
        
        print(f"✅ Enhanced pipeline initialized successfully")
        
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {str(e)}")
        print(f"   Error type: {type(e)}")
        traceback.print_exc()
        sys.exit(1)
    
    # Run pipeline
    try:
        print("\n" + "="*70)
        print("🚀 ENHANCED FLIGHT DATA ANALYSIS SYSTEM")
        print("="*70)
        
        results = pipeline.run_pipeline(steps=steps)
        
        print("\n" + "="*70)
        print("🎉 ENHANCED PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        # Print comprehensive summary
        if 'analysis' in results:
            stats = results['analysis'].get('basic_stats', {})
            print(f"\n📊 ANALYSIS SUMMARY:")
            print(f"   • Total Flights: {stats.get('total_flights', 0):,}")
            
            date_range = stats.get('date_range', {})
            if date_range.get('start'):
                print(f"   • Data Period: {date_range['start']} to {date_range['end']}")
            
            efficiency = results['analysis'].get('efficiency_metrics', {})
            if 'on_time_performance' in efficiency:
                print(f"   • On-Time Performance: {efficiency['on_time_performance']*100:.1f}%")
            
            if 'delay_analysis' in results['analysis']:
                delay_info = results['analysis']['delay_analysis']
                if 'Departure Delay (min)' in delay_info:
                    avg_delay = delay_info['Departure Delay (min)']['mean']
                    print(f"   • Average Delay: {avg_delay:.1f} minutes")
        
        # Handle enhanced dashboard
        if 'dashboard_path' in results:
            dashboard_path = Path(results['dashboard_path'])
            print(f"\n🖥️  ENHANCED MULTI-FEATURE DASHBOARD:")
            print(f"   • File: {dashboard_path}")
            
            if dashboard_path.exists():
                print(f"   • Size: {dashboard_path.stat().st_size / 1024:.1f} KB")
                
                # Convert to absolute path for browser
                abs_path = dashboard_path.resolve()
                dashboard_url = f"file://{abs_path}"
                
                print(f"   • URL: {dashboard_url}")
                print(f"\n✨ ENHANCED DASHBOARD FEATURES:")
                print(f"   🏠 Dashboard: Real-time operations overview and KPIs")
                print(f"   📊 Analytics: Advanced metrics with filtering and reporting")
                print(f"   📅 Scheduling: Flight scheduling management and optimization")
                print(f"   🔮 Predictions: AI-powered forecasting and insights")
                print(f"   💬 NLP Query: Natural language interface for data exploration")
                
                if args.feature:
                    print(f"\n🎯 FOCUSED FEATURE: {args.feature.upper()}")
                    print(f"   The dashboard will highlight the {args.feature} section")
                
                # Auto-open dashboard if requested
                if args.open_dashboard or args.dashboard_only:
                    try:
                        print(f"\n🌐 Opening enhanced dashboard in web browser...")
                        
                        # Add feature focus parameter if specified
                        if args.feature:
                            dashboard_url += f"#{args.feature}"
                        
                        webbrowser.open(dashboard_url)
                        
                        print(f"✅ Dashboard opened successfully!")
                        
                    except Exception as e:
                        print(f"   ⚠️  Could not auto-open browser: {str(e)}")
                        print(f"   📂 Please manually open: {abs_path}")
            else:
                print(f"   ⚠️  Dashboard file not found at expected location")
        
        # Show generated files
        print(f"\n📁 OUTPUT FILES:")
        print(f"   • Enhanced Dashboard: {pipeline.reports_dir / 'flight_dashboard.html'}")
        print(f"   • Reports Directory: {pipeline.reports_dir}")
        print(f"   • Processed Data: {pipeline.data_dir}")
        
        if 'visualizations' in results:
            viz_results = results['visualizations']
            if 'static_plots' in viz_results and viz_results['static_plots']:
                print(f"   • Static Charts: {len(viz_results['static_plots'])} files")
            if 'interactive_plots' in viz_results and viz_results['interactive_plots']:
                print(f"   • Interactive Charts: {len(viz_results['interactive_plots'])} files")
        
        # Enhanced usage instructions
        print(f"\n🚀 GETTING STARTED WITH THE ENHANCED DASHBOARD:")
        print(f"   1. 🏠 Dashboard Tab: View real-time operations overview")
        print(f"   2. 📊 Analytics Tab: Explore advanced metrics and generate reports")
        print(f"   3. 📅 Scheduling Tab: Manage flight schedules and optimize operations")
        print(f"   4. 🔮 Predictions Tab: Access AI forecasting and predictive insights")
        print(f"   5. 💬 NLP Query Tab: Ask questions in natural language")
        
        print(f"\n💡 SAMPLE NLP QUERIES TO TRY:")
        print(f"   • 'What's the average delay by airline?'")
        print(f"   • 'Which hours have the most delays?'")
        print(f"   • 'Show me weekend vs weekday performance'")
        print(f"   • 'Predict delays for next week'")
        print(f"   • 'What are the seasonal trends?'")
        
        print(f"\n🔧 ADVANCED FEATURES:")
        print(f"   • Interactive filtering and drill-down analysis")
        print(f"   • Automated report generation (PDF export)")
        print(f"   • Schedule optimization recommendations")
        print(f"   • Machine learning-powered predictions")
        print(f"   • Real-time data refresh capabilities")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n❌ FILE NOT FOUND ERROR:")
        print(f"   {str(e)}")
        print(f"\n💡 TROUBLESHOOTING:")
        print(f"   • Make sure your data file is in the data/ directory")
        print(f"   • Check the filename matches the configuration")
        print(f"   • Verify file permissions and accessibility")
        print(f"\n🔍 DEBUG INFO:")
        print(f"   • Looking for: {config_dict.get('data_source', 'Unknown')}")
        print(f"   • Data directory: {pipeline.data_dir if 'pipeline' in locals() else 'Not initialized'}")
        
        if 'pipeline' in locals():
            data_files = list(pipeline.data_dir.glob("*.xlsx")) + list(pipeline.data_dir.glob("*.xls"))
            print(f"   • Available data files: {[f.name for f in data_files]}")
        
        return 1
        
    except Exception as e:
        print(f"\n❌ ENHANCED PIPELINE EXECUTION FAILED:")
        print(f"   Error: {str(e)}")
        print(f"   Error type: {type(e)}")
        print(f"\n💡 TROUBLESHOOTING:")
        print(f"   • Check your data file format and content")
        print(f"   • Ensure all dependencies are installed: pip install -r requirements.txt")
        print(f"   • Verify the configuration file is correct")
        print(f"   • For enhanced features, ensure scikit-learn is installed")
        print(f"   • Check the logs for more detailed error information")
        
        # Print more detailed error in debug mode
        if '--debug' in sys.argv or True:  # Always show traceback for now
            print(f"\n🔍 FULL TRACEBACK:")
            traceback.print_exc()
        
        return 1


class EnhancedFlightDataPipeline:
    """Enhanced pipeline class that uses the new dashboard generator"""
    
    def __init__(self, config):
        self.config = config
        self.data_dir = Path(config.get('data_dir', 'data'))
        self.reports_dir = Path(config.get('reports_dir', 'reports'))
        
        # Import the enhanced dashboard generator
        try:
            from app.dashboard_generator import EnhancedDashboardGenerator
            self.dashboard_generator = EnhancedDashboardGenerator(config)
        except ImportError:
            print("⚠️  Enhanced dashboard generator not found, using standard version")
            from app.dashboard_generator import DashboardGenerator
            self.dashboard_generator = DashboardGenerator(config)
    
    def run_pipeline(self, steps=None):
        """Run the enhanced pipeline"""
        if steps is None:
            steps = ['extract', 'transform', 'analyze', 'dashboard']
        
        results = {}
        
        # Import pipeline components
        from app.data_processor import DataProcessor
        from app.analyzer import FlightAnalyzer
        
        # Extract data
        if 'extract' in steps:
            print("📥 Extracting data...")
            processor = DataProcessor(self.config, self.data_dir)
            df_raw = processor.extract_data()
            print(f"   ✅ Extracted {len(df_raw)} raw records")
        
        # Transform data
        if 'transform' in steps:
            print("🔄 Transforming data...")
            df_clean = processor.transform_data(df_raw)
            print(f"   ✅ Processed {len(df_clean)} clean records")
            results['transformed_data'] = df_clean
        
        if 'analyze' in steps:
            print("📊 Analyzing data...")
            analyzer = FlightAnalyzer(self.config)
            # Change this line from analyzer.analyze(df_clean) to:
            analysis_results = analyzer.run_analysis(df_clean)
            print(f"   ✅ Generated comprehensive analysis")
            results['analysis'] = analysis_results
        
        # Generate enhanced dashboard
        if 'dashboard' in steps:
            print("🖥️  Generating enhanced multi-feature dashboard...")
            dashboard_path = self.dashboard_generator.create_dashboard(df_clean, analysis_results)
            print(f"   ✅ Enhanced dashboard created with all features")
            results['dashboard_path'] = dashboard_path
        
        return results


def main_with_args(args_list):
    """Run main with specific arguments (useful for testing)"""
    original_argv = sys.argv
    try:
        sys.argv = ['main.py'] + args_list
        return main()
    finally:
        sys.argv = original_argv


def launch_enhanced_dashboard():
    """Quick function to launch the enhanced dashboard"""
    print("🚀 Enhanced Multi-Feature Dashboard Launch...")
    return main_with_args(['--dashboard-only', '--open-dashboard'])


def launch_feature_focused(feature):
    """Launch dashboard with specific feature focus"""
    print(f"🎯 Launching dashboard focused on {feature.upper()} feature...")
    return main_with_args(['--dashboard-only', '--open-dashboard', '--feature', feature])


if __name__ == "__main__":
    exit_code = main()
    
    if exit_code == 0:
        print(f"\n✨ Thank you for using the Enhanced Flight Data Analysis System!")
        print(f"🌟 Explore all five powerful features in your new dashboard!")
    sys.exit(exit_code)