"""Hardware display drivers package"""
import logging


def display_for(config):
    """Factory function to get the appropriate display implementation"""
    display_config = config.get("ui", {}).get("display", config.get("display", {}))
    display_type = display_config.get("type", "waveshare213in_v4")
    
    if display_type == "waveshare213in_v4":
        from .waveshare213in_v4 import Waveshare213V4
        return Waveshare213V4(config)
    else:
        logging.error(f"Unknown display type: {display_type}")
        raise ValueError(f"Unknown display type: {display_type}")
