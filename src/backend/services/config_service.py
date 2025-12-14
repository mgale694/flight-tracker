"""Configuration management service."""
import toml
from pathlib import Path
from typing import Dict, Optional
from models.schemas import ConfigUpdate


class ConfigService:
    """Service for managing application configuration."""
    
    def __init__(self, config_file: Path):
        """Initialize the config service.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self._cache: Optional[Dict] = None
    
    def load_config(self) -> Dict:
        """Load configuration from TOML file.
        
        Returns:
            Configuration dictionary
        """
        try:
            config = toml.load(self.config_file)
            self._cache = config
            return config
        except Exception as e:
            if self._cache:
                return self._cache
            # Return default config
            return self._get_default_config()
    
    def save_config(self, config: Dict) -> None:
        """Save configuration to TOML file.
        
        Args:
            config: Configuration dictionary to save
            
        Raises:
            Exception: If config cannot be saved
        """
        with open(self.config_file, 'w') as f:
            toml.dump(config, f)
        self._cache = config
    
    def update_config(self, config_update: ConfigUpdate) -> Dict:
        """Update configuration with provided values.
        
        Args:
            config_update: Configuration updates
            
        Returns:
            Updated configuration dictionary
        """
        config = self.load_config()
        main_config = config.get("main", {})
        
        updates = {}
        
        if config_update.address is not None:
            main_config["address"] = config_update.address
            updates["address"] = config_update.address
        
        if config_update.search_radius_meters is not None:
            main_config["search_radius_meters"] = config_update.search_radius_meters
            updates["search_radius_meters"] = config_update.search_radius_meters
        
        if config_update.max_flights is not None:
            main_config["max_flights"] = config_update.max_flights
            updates["max_flights"] = config_update.max_flights
        
        if config_update.max_elapsed_time is not None:
            main_config["max_elapsed_time"] = config_update.max_elapsed_time
            updates["max_elapsed_time"] = config_update.max_elapsed_time
        
        if config_update.display_fields is not None:
            main_config["display_fields"] = config_update.display_fields
            updates["display_fields"] = config_update.display_fields
        
        config["main"] = main_config
        self.save_config(config)
        
        return config, updates
    
    def get_main_config(self) -> Dict:
        """Get main configuration section.
        
        Returns:
            Main configuration dictionary
        """
        config = self.load_config()
        return config.get("main", {})
    
    @staticmethod
    def _get_default_config() -> Dict:
        """Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "main": {
                "address": "San Francisco, CA",
                "search_radius_meters": 3000,
                "max_flights": 20,
                "max_elapsed_time": 1800,
                "display_fields": ["FROM", "AIRLINE", "MODEL", "REG", "ROUTE"]
            },
            "logging": {
                "max_activities": 500,
                "categories": ["SYSTEM", "RADAR", "FLIGHT", "CONFIG", "ERROR", "INFO"]
            }
        }
