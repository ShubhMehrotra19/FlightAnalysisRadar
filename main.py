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
    """Main execution function with proper parameter handling"""
    parser = argparse.ArgumentParser(description='Flight Data Analysis Pipeline with Interactive Dashboard')
    parser.add_argument('--config', '-c', type=str, help='Configuration file path')
    parser.add_argument('--steps', '-s', nargs='+', 
                       choices=['extract', 'transform', 'analyze', 'visualize', 'dashboard'],
                       help='Pipeline steps to execute')
    parser.add_argument('--data-file', '-d', type=str, help='Override data file path')
    parser.add_argument('--output-dir', '-o', type=str, help='Override output directory')
    parser.add_argument('--open-dashboard', action='store_true', 
                       help='Automatically open dashboard in web browser')
    parser.add_argument('--dashboard-only', action='store_true',
                       help='Generate only the dashboard (runs extract, transform, analyze, dashboard)')
    
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
    
    # Load configuration - THIS IS THE FIX
    try:
        # Load config into a dictionary first
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
    
    # Initialize pipeline - PASS THE CONFIG DICTIONARY, NOT PATH
    try:
        print(f"🔧 Initializing pipeline with config dictionary...")
        
        # The key fix: pass the config dictionary directly
        pipeline = FlightDataPipeline(config_dict)
        
        print(f"✅ Pipeline initialized successfully")
        
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {str(e)}")
        print(f"   Error type: {type(e)}")
        traceback.print_exc()
        sys.exit(1)
    
    # Run pipeline
    try:
        print("\n" + "="*70)
        print("🚀 FLIGHT DATA ANALYSIS PIPELINE")
        print("="*70)
        
        results = pipeline.run_pipeline(steps=steps)
        
        print("\n" + "="*70)
        print("🎉 PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        # Print summary
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
        
        # Handle dashboard
        if 'dashboard_path' in results:
            dashboard_path = Path(results['dashboard_path'])
            print(f"\n🖥️  INTERACTIVE DASHBOARD:")
            print(f"   • File: {dashboard_path}")
            
            if dashboard_path.exists():
                print(f"   • Size: {dashboard_path.stat().st_size / 1024:.1f} KB")
                
                # Convert to absolute path for browser
                abs_path = dashboard_path.resolve()
                dashboard_url = f"file://{abs_path}"
                
                print(f"   • URL: {dashboard_url}")
                print(f"\n💡 DASHBOARD FEATURES:")
                print(f"   • Interactive charts and visualizations")
                print(f"   • Natural Language Query interface")
                print(f"   • Real-time data exploration")
                print(f"   • Responsive design for all devices")
                
                # Auto-open dashboard if requested
                if args.open_dashboard or args.dashboard_only:
                    try:
                        print(f"\n🌐 Opening dashboard in web browser...")
                        webbrowser.open(dashboard_url)
                    except Exception as e:
                        print(f"   ⚠️  Could not auto-open browser: {str(e)}")
                        print(f"   📂 Please manually open: {abs_path}")
            else:
                print(f"   ⚠️  Dashboard file not found at expected location")
        
        # Show generated files
        print(f"\n📁 OUTPUT FILES:")
        print(f"   • Reports Directory: {pipeline.reports_dir}")
        print(f"   • Processed Data: {pipeline.data_dir}")
        
        if 'visualizations' in results:
            viz_results = results['visualizations']
            if 'static_plots' in viz_results and viz_results['static_plots']:
                print(f"   • Static Charts: {len(viz_results['static_plots'])} files")
            if 'interactive_plots' in viz_results and viz_results['interactive_plots']:
                print(f"   • Interactive Charts: {len(viz_results['interactive_plots'])} files")
        
        # Instructions for next steps
        print(f"\n🚀 NEXT STEPS:")
        print(f"   1. Open the dashboard HTML file in your web browser")
        print(f"   2. Use the NLP query interface to ask questions about your data")
        print(f"   3. Explore the interactive charts and visualizations")
        print(f"   4. Check the reports directory for additional analysis files")
        
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
        print(f"\n❌ PIPELINE EXECUTION FAILED:")
        print(f"   Error: {str(e)}")
        print(f"   Error type: {type(e)}")
        print(f"\n💡 TROUBLESHOOTING:")
        print(f"   • Check your data file format and content")
        print(f"   • Ensure all dependencies are installed: pip install -r requirements.txt")
        print(f"   • Verify the configuration file is correct")
        print(f"   • Check the logs for more detailed error information")
        
        # Print more detailed error in debug mode
        if '--debug' in sys.argv or True:  # Always show traceback for now
            print(f"\n🔍 FULL TRACEBACK:")
            traceback.print_exc()
        
        return 1


def main_with_args(args_list):
    """Run main with specific arguments (useful for testing)"""
    original_argv = sys.argv
    try:
        sys.argv = ['main.py'] + args_list
        return main()
    finally:
        sys.argv = original_argv


def launch_dashboard_only():
    """Quick function to launch just the dashboard"""
    print("🚀 Quick Dashboard Launch...")
    return main_with_args(['--dashboard-only', '--open-dashboard'])


if __name__ == "__main__":
    exit_code = main()
    
    if exit_code == 0:
        print(f"\n✨ Thank you for using Flight Data Analysis Pipeline!")
        print(f"   For support and updates, visit: https://github.com/your-repo/FlightRadarAnalytics")
    
    sys.exit(exit_code)