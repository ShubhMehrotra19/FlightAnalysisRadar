import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

def quick_launch():
    """Quick dashboard launch with minimal setup"""
    print("🚀 Flight Data Dashboard - Quick Launch")
    print("="*50)
    
    try:
        from main import main_with_args
        
        # Run with dashboard-only settings
        exit_code = main_with_args([
            '--dashboard-only',
            '--open-dashboard'
        ])
        
        if exit_code == 0:
            print("\n✅ Dashboard launched successfully!")
            print("🌐 The dashboard should now be open in your web browser")
            
            # Keep the script running to show instructions
            input("\nPress Enter to exit...")
        else:
            print("\n❌ Dashboard launch failed. Check the error messages above.")
            input("\nPress Enter to exit...")
            
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {str(e)}")
        print("\n💡 Try running the full pipeline instead:")
        print("   python main.py --dashboard-only --open-dashboard")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    quick_launch()


