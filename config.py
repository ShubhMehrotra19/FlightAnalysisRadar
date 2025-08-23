import json
from pathlib import Path

class Config:
    """Configuration management"""
    
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
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    
    @classmethod
    def load(cls, config_path=None):
        """Load configuration from file or use defaults"""
        config = cls.DEFAULT_CONFIG.copy()
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                cls._deep_update(config, user_config)
        
        return config
    
    @classmethod
    def save(cls, config, config_path):
        """Save configuration to file"""
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    @staticmethod
    def _deep_update(base_dict, update_dict):
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                Config._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value