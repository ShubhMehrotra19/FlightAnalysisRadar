import os
from pathlib import Path

def create_project_structure():
    """Create the complete project directory structure"""
    
    project_structure = {
        'FlightRadarAnalytics': {
            'app': {
                'pipeline': ['__init__.py'],
                '__init__.py': None,
            },
            'data': [],
            'notebooks': [],
            'reports': [],
        }
    }
    
    def create_structure(base_path, structure):
        for name, content in structure.items():
            path = base_path / name
            
            if isinstance(content, dict):
                # It's a directory
                path.mkdir(exist_ok=True)
                print(f"📁 Created directory: {path}")
                create_structure(path, content)
            elif isinstance(content, list):
                # It's a directory with files
                path.mkdir(exist_ok=True)
                print(f"📁 Created directory: {path}")
                for file_name in content:
                    file_path = path / file_name
                    if not file_path.exists():
                        file_path.touch()
                        print(f"📄 Created file: {file_path}")
            else:
                # It's a file
                if not path.exists():
                    path.touch()
                    print(f"📄 Created file: {path}")
    
    project_root = Path.cwd() / 'FlightRadarAnalytics'
    create_structure(Path.cwd(), project_structure)
    
    print("\n🎉 Project structure created successfully!")
    print(f"📂 Project root: {project_root}")
    print("\nNext steps:")
    print("1. Copy your Excel data file to the data/ directory")
    print("2. Install requirements: pip install -r requirements.txt")
    print("3. Run pipeline: python main.py")

if __name__ == "__main__":
    create_project_structure()