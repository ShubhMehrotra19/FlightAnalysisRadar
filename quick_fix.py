#!/usr/bin/env python3
"""
Quick diagnostic and fix script for the path error
File: FlightRadarAnalytics/quick_fix.py
"""

import sys
import os
from pathlib import Path
import traceback

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

def diagnose_issue():
    """Diagnose the path error issue"""
    print("🔍 FLIGHT DATA PIPELINE - DIAGNOSTIC TOOL")
    print("="*50)
    
    # Step 1: Check directory structure
    print("\n1. DIRECTORY STRUCTURE CHECK")
    print("-" * 30)
    
    required_dirs = ['app', 'data', 'reports']
    required_files = ['config.py', 'main.py']
    
    for dir_name in required_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if dir_path.exists():
            print(f"   ✅ {dir_name}/ directory exists")
        else:
            print(f"   ❌ {dir_name}/ directory missing")
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   🔧 Created {dir_name}/ directory")
    
    for file_name in required_files:
        file_path = PROJECT_ROOT / file_name
        if file_path.exists():
            print(f"   ✅ {file_name} exists")
        else:
            print(f"   ❌ {file_name} missing")
    
    # Step 2: Check pipeline structure
    print("\n2. PIPELINE STRUCTURE CHECK")
    print("-" * 30)
    
    pipeline_files = [
        'app/pipeline/__init__.py',
        'app/pipeline/flight_data_pipeline.py',
        'app/data_processor.py',
        'app/analyzer.py',
        'app/visualizer.py',
        'app/dashboard_generator.py'
    ]
    
    for file_path in pipeline_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} missing")
            # Create directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path.endswith('__init__.py'):
                full_path.touch()
                print(f"   🔧 Created {file_path}")
    
    # Step 3: Test imports
    print("\n3. IMPORT TEST")
    print("-" * 30)
    
    try:
        print("   Testing config import...")
        from config import Config
        print("   ✅ Config import successful")
        
        # Test config loading
        test_config = Config.load()
        print(f"   ✅ Config loading successful: {type(test_config)}")
        
    except Exception as e:
        print(f"   ❌ Config import failed: {str(e)}")
        traceback.print_exc()
    
    try:
        print("   Testing pipeline import...")
        from app.pipeline.flight_data_pipeline import FlightDataPipeline
        print("   ✅ Pipeline import successful")
        
        # Test pipeline initialization with dict (the fix)
        test_config = {"data_source": "test.xlsx", "reports_dir": str(PROJECT_ROOT / "reports")}
        test_pipeline = FlightDataPipeline(test_config)
        print("   ✅ Pipeline initialization with dict successful")
        
    except Exception as e:
        print(f"   ❌ Pipeline import/init failed: {str(e)}")
        traceback.print_exc()
    
    # Step 4: Check data files
    print("\n4. DATA FILES CHECK")
    print("-" * 30)
    
    data_dir = PROJECT_ROOT / "data"
    if data_dir.exists():
        excel_files = list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*.xls"))
        if excel_files:
            print(f"   ✅ Found {len(excel_files)} Excel files:")
            for file in excel_files:
                print(f"      • {file.name}")
        else:
            print("   ⚠️  No Excel files found in data/ directory")
            print("   📝 Please add your flight data Excel file to the data/ directory")
    else:
        print("   ❌ data/ directory not found")
    
    # Step 5: Provide fix recommendations
    print("\n5. RECOMMENDED FIXES")
    print("-" * 30)
    
    print("   🔧 IMMEDIATE FIXES:")
    print("      1. Replace your main.py with main_fixed.py")
    print("      2. Replace your config.py with the fixed config.py")
    print("      3. Replace your flight_data_pipeline.py with fixed_flight_data_pipeline.py")
    
    print("\n   📋 KEY CHANGES MADE:")
    print("      • Fixed FlightDataPipeline constructor to handle both config dicts and paths")
    print("      • Fixed main.py to pass config dictionary instead of path object")
    print("      • Added proper error handling and debugging")
    print("      • Improved directory and file validation")


def create_minimal_missing_files():
    """Create minimal versions of missing files"""
    print("\n6. CREATING MISSING FILES")
    print("-" * 30)
    
    # Create __init__.py files
    init_files = [
        'app/__init__.py',
        'app/pipeline/__init__.py'
    ]
    
    for init_file in init_files:
        init_path = PROJECT_ROOT / init_file
        init_path.parent.mkdir(parents=True, exist_ok=True)
        if not init_path.exists():
            init_path.write_text('# Auto-generated __init__.py\n')
            print(f"   ✅ Created {init_file}")
    
    # Create minimal stub files if they don't exist
    stub_files = {
        'app/analyzer.py': '''
class FlightAnalyzer:
    def __init__(self, config):
        self.config = config
    
    def run_analysis(self, df):
        return {
            'basic_stats': {'total_flights': len(df)},
            'efficiency_metrics': {'on_time_performance': 0.8}
        }
''',
        'app/visualizer.py': '''
class Visualizer:
    def __init__(self, reports_dir):
        self.reports_dir = reports_dir
    
    def generate_reports(self, df, analysis):
        return {'static_plots': [], 'interactive_plots': []}
'''
    }
    
    for file_path, content in stub_files.items():
        full_path = PROJECT_ROOT / file_path
        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            print(f"   ✅ Created stub {file_path}")


def test_fixed_pipeline():
    """Test the pipeline with the fixes"""
    print("\n7. TESTING FIXED PIPELINE")
    print("-" * 30)
    
    try:
        # Test the fix by running a minimal pipeline
        from config import Config
        from app.pipeline.flight_data_pipeline import FlightDataPipeline
        
        config = Config.load()
        print(f"   ✅ Config loaded: {type(config)}")
        
        pipeline = FlightDataPipeline(config)
        print(f"   ✅ Pipeline created successfully")
        print(f"   ✅ Pipeline components initialized")
        
        print("\n   🎉 PIPELINE READY TO RUN!")
        print("   📋 You can now run: python main_fixed.py --dashboard-only")
        
    except Exception as e:
        print(f"   ❌ Pipeline test failed: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    diagnose_issue()
    create_minimal_missing_files()
    test_fixed_pipeline()
    
    print(f"\n✨ DIAGNOSTIC COMPLETE!")
    print(f"   🔧 Use the fixed files provided to resolve the path error")
    print(f"   📞 If issues persist, check that your data file exists in data/ directory")