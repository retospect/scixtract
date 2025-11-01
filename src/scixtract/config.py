"""
Configuration management for AI PDF Extractor.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class OllamaConfig:
    """Ollama configuration settings."""
    base_url: str = "http://localhost:11434"
    default_model: str = "llama3.2"
    timeout: int = 120
    temperature: float = 0.1
    top_p: float = 0.9
    num_ctx: int = 8192


@dataclass
class ExtractionConfig:
    """PDF extraction configuration settings."""
    output_dir: str = "ai_extractions"
    update_knowledge: bool = True
    save_markdown: bool = True
    save_keywords: bool = True
    context_length: int = 200


@dataclass
class KnowledgeConfig:
    """Knowledge base configuration settings."""
    db_path: Optional[str] = None
    auto_update: bool = True
    max_search_results: int = 20
    export_format: str = "json"


@dataclass
class AIConfig:
    """Complete AI PDF Extractor configuration."""
    ollama: OllamaConfig
    extraction: ExtractionConfig
    knowledge: KnowledgeConfig
    
    def __init__(self) -> None:
        self.ollama = OllamaConfig()
        self.extraction = ExtractionConfig()
        self.knowledge = KnowledgeConfig()


class ConfigManager:
    """Manages configuration loading and saving."""
    
    DEFAULT_CONFIG_PATHS = [
        ".scixtract.json",
        ".scixtract.yaml",
        ".scixtract.yml",
        "scixtract.json",
        "scixtract.yaml",
        "scixtract.yml",
        os.path.expanduser("~/.scixtract.json"),
        os.path.expanduser("~/.scixtract.yaml"),
        os.path.expanduser("~/.config/scixtract/config.json"),
        os.path.expanduser("~/.config/scixtract/config.yaml"),
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = AIConfig()
        self.load_config()
    
    def find_config_file(self) -> Optional[Path]:
        """Find the first existing configuration file."""
        if self.config_path:
            config_file = Path(self.config_path)
            if config_file.exists():
                return config_file
            else:
                raise FileNotFoundError(f"Specified config file not found: {self.config_path}")
        
        # Search for default config files
        for config_path in self.DEFAULT_CONFIG_PATHS:
            config_file = Path(config_path)
            if config_file.exists():
                return config_file
        
        return None
    
    def load_config(self) -> None:
        """Load configuration from file."""
        config_file = self.find_config_file()
        
        if not config_file:
            # No config file found, use defaults
            self._load_from_environment()
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            self._update_config_from_dict(data)
            print(f"📋 Loaded configuration from: {config_file}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load config file {config_file}: {e}")
            print("Using default configuration")
        
        # Always check environment variables (they override config file)
        self._load_from_environment()
    
    def _update_config_from_dict(self, data: Dict[str, Any]) -> None:
        """Update configuration from dictionary data."""
        if 'ollama' in data:
            ollama_data = data['ollama']
            if 'base_url' in ollama_data:
                self.config.ollama.base_url = ollama_data['base_url']
            if 'default_model' in ollama_data:
                self.config.ollama.default_model = ollama_data['default_model']
            if 'timeout' in ollama_data:
                self.config.ollama.timeout = ollama_data['timeout']
            if 'temperature' in ollama_data:
                self.config.ollama.temperature = ollama_data['temperature']
            if 'top_p' in ollama_data:
                self.config.ollama.top_p = ollama_data['top_p']
            if 'num_ctx' in ollama_data:
                self.config.ollama.num_ctx = ollama_data['num_ctx']
        
        if 'extraction' in data:
            extraction_data = data['extraction']
            if 'output_dir' in extraction_data:
                self.config.extraction.output_dir = extraction_data['output_dir']
            if 'update_knowledge' in extraction_data:
                self.config.extraction.update_knowledge = extraction_data['update_knowledge']
            if 'save_markdown' in extraction_data:
                self.config.extraction.save_markdown = extraction_data['save_markdown']
            if 'save_keywords' in extraction_data:
                self.config.extraction.save_keywords = extraction_data['save_keywords']
            if 'context_length' in extraction_data:
                self.config.extraction.context_length = extraction_data['context_length']
        
        if 'knowledge' in data:
            knowledge_data = data['knowledge']
            if 'db_path' in knowledge_data:
                self.config.knowledge.db_path = knowledge_data['db_path']
            if 'auto_update' in knowledge_data:
                self.config.knowledge.auto_update = knowledge_data['auto_update']
            if 'max_search_results' in knowledge_data:
                self.config.knowledge.max_search_results = knowledge_data['max_search_results']
            if 'export_format' in knowledge_data:
                self.config.knowledge.export_format = knowledge_data['export_format']
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        # Ollama settings
        if os.getenv('OLLAMA_BASE_URL'):
            base_url = os.getenv('OLLAMA_BASE_URL')
            if base_url:
                self.config.ollama.base_url = base_url
        if os.getenv('OLLAMA_MODEL'):
            model = os.getenv('OLLAMA_MODEL')
            if model:
                self.config.ollama.default_model = model
        if os.getenv('OLLAMA_TIMEOUT'):
            try:
                timeout_str = os.getenv('OLLAMA_TIMEOUT')
                if timeout_str:
                    self.config.ollama.timeout = int(timeout_str)
            except ValueError:
                pass
        if os.getenv('OLLAMA_TEMPERATURE'):
            try:
                temp_str = os.getenv('OLLAMA_TEMPERATURE')
                if temp_str:
                    self.config.ollama.temperature = float(temp_str)
            except ValueError:
                pass
        
        # Extraction settings
        if os.getenv('AI_PDF_OUTPUT_DIR'):
            output_dir = os.getenv('AI_PDF_OUTPUT_DIR')
            if output_dir:
                self.config.extraction.output_dir = output_dir
        if os.getenv('AI_PDF_UPDATE_KNOWLEDGE'):
            update_knowledge = os.getenv('AI_PDF_UPDATE_KNOWLEDGE')
            if update_knowledge:
                self.config.extraction.update_knowledge = update_knowledge.lower() in ['true', '1', 'yes']
        
        # Knowledge settings
        if os.getenv('AI_PDF_KNOWLEDGE_DB'):
            db_path = os.getenv('AI_PDF_KNOWLEDGE_DB')
            if db_path:
                self.config.knowledge.db_path = db_path
    
    def save_config(self, config_path: Optional[str] = None, format: str = "json") -> None:
        """Save current configuration to file."""
        if config_path:
            output_path = Path(config_path)
        else:
            if format.lower() == "yaml":
                output_path = Path("scixtract.yaml")
            else:
                output_path = Path("scixtract.json")
        
        # Convert config to dictionary
        config_dict = {
            "ollama": asdict(self.config.ollama),
            "extraction": asdict(self.config.extraction),
            "knowledge": asdict(self.config.knowledge)
        }
        
        # Create directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if format.lower() in ["yaml", "yml"]:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuration saved to: {output_path}")
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def create_example_config(self, format: str = "json") -> str:
        """Create an example configuration file."""
        config_dict = {
            "ollama": {
                "base_url": "http://localhost:11434",
                "default_model": "qwen2.5:32b-instruct-q4_K_M",
                "timeout": 120,
                "temperature": 0.1,
                "top_p": 0.9,
                "num_ctx": 8192
            },
            "extraction": {
                "output_dir": "ai_extractions",
                "update_knowledge": True,
                "save_markdown": True,
                "save_keywords": True,
                "context_length": 200
            },
            "knowledge": {
                "db_path": "knowledge_index.db",
                "auto_update": True,
                "max_search_results": 20,
                "export_format": "json"
            }
        }
        
        if format.lower() in ["yaml", "yml"]:
            return yaml.dump(config_dict, default_flow_style=False, indent=2)
        else:
            return json.dumps(config_dict, indent=2, ensure_ascii=False)
    
    def print_config(self) -> None:
        """Print current configuration."""
        print("📋 Current Paper2Txt Configuration:")
        print("=" * 50)
        
        print("\n🤖 Ollama Settings:")
        print(f"   Base URL: {self.config.ollama.base_url}")
        print(f"   Default Model: {self.config.ollama.default_model}")
        print(f"   Timeout: {self.config.ollama.timeout}s")
        print(f"   Temperature: {self.config.ollama.temperature}")
        print(f"   Top P: {self.config.ollama.top_p}")
        print(f"   Context Length: {self.config.ollama.num_ctx}")
        
        print("\n📄 Extraction Settings:")
        print(f"   Output Directory: {self.config.extraction.output_dir}")
        print(f"   Update Knowledge: {self.config.extraction.update_knowledge}")
        print(f"   Save Markdown: {self.config.extraction.save_markdown}")
        print(f"   Save Keywords: {self.config.extraction.save_keywords}")
        print(f"   Context Length: {self.config.extraction.context_length}")
        
        print("\n🧠 Knowledge Settings:")
        print(f"   Database Path: {self.config.knowledge.db_path or 'Default (knowledge_index.db)'}")
        print(f"   Auto Update: {self.config.knowledge.auto_update}")
        print(f"   Max Search Results: {self.config.knowledge.max_search_results}")
        print(f"   Export Format: {self.config.knowledge.export_format}")


def get_config(config_path: Optional[str] = None) -> AIConfig:
    """Get configuration instance."""
    manager = ConfigManager(config_path)
    return manager.config


def create_config_command() -> None:
    """Command-line interface for configuration management."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Paper2Txt Configuration Manager"
    )
    parser.add_argument(
        "--create-example", 
        help="Create example configuration file",
        choices=["json", "yaml"]
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path for example config"
    )
    parser.add_argument(
        "--show", action="store_true",
        help="Show current configuration"
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    if args.create_example:
        manager = ConfigManager()
        example_config = manager.create_example_config(args.create_example)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(example_config)
            print(f"✅ Example configuration saved to: {args.output}")
        else:
            print("📋 Example Configuration:")
            print("=" * 30)
            print(example_config)
    
    elif args.show:
        manager = ConfigManager(args.config)
        manager.print_config()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    create_config_command()
