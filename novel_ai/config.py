"""
Configuration management for the Novel AI system.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import json
import os
from pathlib import Path


@dataclass
class APIConfig:
    """Configuration for OpenRouter API integration"""
    api_key: str
    base_url: str
    model: str
    headers: Dict[str, str]
    generation_params: Dict[str, Any]
    max_retries: int = 3
    timeout: int = 30

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'APIConfig':
        """Create APIConfig from dictionary"""
        return cls(
            api_key=config['api_key'],
            base_url=config['base_url'],
            model=config['model'],
            headers={
                "Authorization": f"Bearer {config['api_key']}",
                "HTTP-Referer": config['headers']['HTTP-Referer'],
                "X-Title": config['headers']['X-Title']
            },
            generation_params=config['generation_params'],
            max_retries=config.get('max_retries', 3),
            timeout=config.get('timeout', 30)
        )


@dataclass
class SystemConfig:
    """System-wide configuration"""
    storage_path: str
    log_level: str = "INFO"
    api_config: Optional[APIConfig] = None

    @classmethod
    def load_from_file(cls, config_path: str) -> 'SystemConfig':
        """Load configuration from a JSON file"""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            config_data = json.load(f)

        api_config = None
        if 'api_config' in config_data:
            api_config = APIConfig.from_dict(config_data['api_config'])

        return cls(
            storage_path=config_data['storage_path'],
            log_level=config_data.get('log_level', 'INFO'),
            api_config=api_config
        )

    def save_to_file(self, config_path: str) -> None:
        """Save configuration to a JSON file"""
        config_data = {
            'storage_path': self.storage_path,
            'log_level': self.log_level,
        }

        if self.api_config:
            config_data['api_config'] = {
                'api_key': self.api_config.api_key,
                'base_url': self.api_config.base_url,
                'model': self.api_config.model,
                'headers': {
                    'HTTP-Referer': self.api_config.headers['HTTP-Referer'],
                    'X-Title': self.api_config.headers['X-Title']
                },
                'generation_params': self.api_config.generation_params,
                'max_retries': self.api_config.max_retries,
                'timeout': self.api_config.timeout
            }

        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)


def initialize_config(config_path: str = None) -> SystemConfig:
    """Initialize system configuration"""
    if config_path and os.path.exists(config_path):
        return SystemConfig.load_from_file(config_path)
    
    # Create default configuration
    storage_path = os.path.join(os.getcwd(), 'story_data')
    return SystemConfig(storage_path=storage_path)
