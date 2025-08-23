#!/usr/bin/env python3
"""
Configuration module for Flight Data Analysis Pipeline
File: FlightRadarAnalytics/config.py
"""

import json
import os
from pathlib import Path


class Config:
    """Configuration manager for the flight data analysis pipeline"""
    
    DEFAULT_CONFIG = {
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
    
    @classmethod
    def load(cls, config_path=None):
        """
        Load configuration from file or return defaults
        
        Args:
            config_path (str, optional): Path to configuration file
            
        Returns:
            dict: Configuration dictionary
        """
        config = cls.DEFAULT_CONFIG.copy()
        
        if config_path is None:
            print("ℹ️  No config file specified, using default configuration")
            return config
            
        if not isinstance(config_path, (str, Path)):
            print(f"⚠️  Invalid config path type: {type(config_path)}. Using defaults.")
            return config
            
        config_file = Path(config_path)
        
        if not config_file.exists():
            print(f"⚠️  Config file not found: {config_path}. Using defaults.")
            return config
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                
            # Merge user config with defaults
            config.update(user_config)
            print(f"✅ Configuration loaded from: {config_path}")
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file {config_path}: {str(e)}")
            print("Using default configuration")
            
        except Exception as e:
            print(f"❌ Error loading config file {config_path}: {str(e)}")
            print("Using default configuration")
            
        return config
    
    @classmethod
    def save(cls, config, config_path):
        """
        Save configuration to file
        
        Args:
            config (dict): Configuration to save
            config_path (str): Path where to save the configuration
        """
        try:
            config_file = Path(config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
                
            print(f"✅ Configuration saved to: {config_path}")
            
        except Exception as e:
            print(f"❌ Error saving config file {config_path}: {str(e)}")
    
    @classmethod
    def create_sample_config(cls, output_path="sample_config.json"):
        """
        Create a sample configuration file
        
        Args:
            output_path (str): Where to save the sample config
        """
        sample_config = {
            "data_source": "your_flight_data.xlsx",
            "analysis_params": {
                "delay_threshold": 15,
                "cascade_factor": 0.4,
                "simulation_delay_reduction": 5,
                "peak_hour_shift": 1
            },
            "output_formats": ["csv", "json", "html"],
            "dashboard_port": 8050,
            "generate_standalone_dashboard": True,
            "_comments": {
                "data_source": "Path to your flight data file (Excel format)",
                "delay_threshold": "Minutes - flights delayed more than this are considered late",
                "cascade_factor": "Factor for calculating cascade delays (0-1)",
                "simulation_delay_reduction": "Minutes to reduce delays in simulation",
                "peak_hour_shift": "Hours to shift peak times in optimization",
                "output_formats": "Supported: csv, json, html, xlsx",
                "dashboard_port": "Port for running dashboard server",
                "generate_standalone_dashboard": "Generate standalone HTML dashboard"
            }
        }
        
        cls.save(sample_config, output_path)
        return output_path


# Test function
def test_config():
    """Test configuration loading"""
    print("🧪 Testing Configuration Module")
    print("="*40)
    
    # Test 1: Load default config
    print("Test 1: Load default configuration")
    config1 = Config.load()
    print(f"   Config keys: {list(config1.keys())}")
    print(f"   Data source: {config1.get('data_source')}")
    
    # Test 2: Load non-existent config
    print("\nTest 2: Load non-existent configuration")
    config2 = Config.load("non_existent.json")
    print(f"   Config keys: {list(config2.keys())}")
    
    # Test 3: Create sample config
    print("\nTest 3: Create sample configuration")
    sample_path = Config.create_sample_config("test_sample_config.json")
    print(f"   Sample config created at: {sample_path}")
    
    # Test 4: Load the sample config
    print("\nTest 4: Load sample configuration")
    config4 = Config.load(sample_path)
    print(f"   Loaded config keys: {list(config4.keys())}")
    
    # Clean up
    try:
        os.remove(sample_path)
        print(f"   Cleaned up test file: {sample_path}")
    except:
        pass


if __name__ == "__main__":
    test_config()