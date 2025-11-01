"""
Configuration management for scixtract using hierarchical-conf.
"""

import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from hierarchical_conf import ConfigManager as HierarchicalConfigManager

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class Config:
    """Scixtract configuration."""
    # Ollama settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    ollama_timeout: int = 120
    ollama_temperature: float = 0.1
    ollama_top_p: float = 0.9
    ollama_num_ctx: int = 8192
    
    # Extraction settings
    output_dir: str = "extractions"
    update_knowledge: bool = True
    save_markdown: bool = True
    save_keywords: bool = True
    context_length: int = 200
    
    # Knowledge settings
    knowledge_db_path: Optional[str] = None
    knowledge_auto_update: bool = True
    knowledge_max_results: int = 20
    knowledge_export_format: str = "json"


class ConfigManager:
    """Clean config manager using hierarchical-conf."""
    
    CONFIG_PATHS = [
        "scixtract.toml",
        "~/.config/scixtract/config.toml",
        "~/.scixtract.toml",
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize config manager with hierarchical-conf."""
        config_paths = [config_path] if config_path else self.CONFIG_PATHS
        
        self.manager = HierarchicalConfigManager(
            config_class=Config,
            config_paths=config_paths,
            env_prefix="SCIXTRACT_",
            auto_load=True
        )
    
    @property
    def config(self) -> Config:
        """Get current configuration."""
        return self.manager.config
    
    def save_config(self, path: Optional[str] = None) -> None:
        """Save current configuration to TOML file."""
        self.manager.save_config(path)
    
    def create_example_config(self, path: str = "scixtract.toml") -> str:
        """Create example TOML configuration file."""
        example = Config()
        return self.manager.to_toml(example)
    
    
    def print_config(self) -> None:
        """Print current configuration."""
        print("📋 Scixtract Configuration:")
        print("=" * 40)
        
        c = self.config
        print(f"\n🤖 Ollama: {c.ollama_base_url} | {c.ollama_model}")
        print(f"📄 Output: {c.output_dir} | Knowledge: {c.update_knowledge}")
        print(f"🧠 Database: {c.knowledge_db_path or 'default'}")




def get_config(config_path: Optional[str] = None) -> Config:
    """Get configuration instance."""
    manager = ConfigManager(config_path)
    return manager.config


# Global config instance
_config_manager = None


def config() -> Config:
    """Get global config instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.config
