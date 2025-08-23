import sys
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "app"))

from app.pipeline.flight_data_pipeline import FlightDataPipeline
from config import Config

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Flight Data Analysis Pipeline')
    parser.add_argument('--config', '-c', type=str, help='Configuration file path')
    parser.add_argument('--steps', '-s', nargs='+', 
                       choices=['extract', 'transform', 'analyze', 'visualize', 'dashboard'],
                       help='Pipeline steps to execute')
    parser.add_argument('--data-file', '-d', type=str, help='Override data file path')
    parser.add_argument('--output-dir', '-o', type=str, help='Override output directory')
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config.load(args.config)
    
    # Override config with command line arguments
    if args.data_file:
        config['data_source'] = args.data_file
    
    # Initialize and run pipeline
    pipeline = FlightDataPipeline(config)
    
    try:
        results = pipeline.run_pipeline(steps=args.steps)
        print("\n" + "="*60)
        print("🎉 PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Print summary
        if 'analysis' in results:
            stats = results['analysis'].get('basic_stats', {})
            print(f"📊 Analyzed {stats.get('total_flights', 0):,} flights")
            print(f"📅 Data period: {stats.get('date_range', {}).get('start', 'N/A')} to {stats.get('date_range', {}).get('end', 'N/A')}")
            
            efficiency = results['analysis'].get('efficiency_metrics', {})
            if 'on_time_performance' in efficiency:
                print(f"⏰ On-time performance: {efficiency['on_time_performance']*100:.1f}%")
        
        if 'dashboard_url' in results:
            print(f"🖥  Dashboard available at: {results['dashboard_url']}")
        
        print("\n📁 Output files generated in:")
        print(f"   • Reports: {pipeline.reports_dir}")
        print(f"   • Processed data: {pipeline.data_dir}")
        
    except Exception as e:
        print(f"\n❌ Pipeline execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()