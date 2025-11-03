import os

import yaml
from jinja2 import Environment, FileSystemLoader


class PromptManager:
    def __init__(self, prompts_dir: str = "prompts"):
        """
        Initialize the prompt manager with Jinja2 templates.

        :param prompts_dir: Directory containing prompt templates
        """
        self.prompts_dir = prompts_dir
        self.env = Environment(loader=FileSystemLoader(prompts_dir))
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from config.yaml"""
        config_path = os.path.join(self.prompts_dir, "config.yaml")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {"default": {}}

    def load_system_prompt(self) -> str:
        """Load the system prompt"""
        system_prompt_path = os.path.join(self.prompts_dir, "system_prompt.txt")
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def render_component_analysis_prompt(
        self, analysis_mode: str = "default", **kwargs
    ) -> str:
        """
        Render the component analysis prompt with variables.

        :param analysis_mode: Analysis mode from config (default, power_quality, etc.)
        :param kwargs: Additional template variables
        :return: Rendered prompt text
        """
        template = self.env.get_template("component_analysis.j2")

        # Get config for the specified mode
        mode_config = self.config.get(analysis_mode, self.config.get("default", {}))

        # Merge mode config with kwargs
        template_vars = {**mode_config, **kwargs}

        return template.render(**template_vars)
