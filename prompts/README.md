# Prompt Templates Configuration

This folder contains Jinja2 templates for various prompts used in the electrical component analysis system.

## Files:

- `system_prompt.txt` - System role prompt for the AI assistant
- `component_analysis.j2` - Main prompt for analyzing electrical diagrams
- `config.yaml` - Configuration for different analysis modes

## Usage:

Templates support variables that can be customized based on the analysis requirements:

- `quantity_format` - Format for quantity field (default: "number")
- `additional_instructions` - Any extra instructions for specific use cases

## Template Variables:

You can customize the prompts by passing variables when rendering:

```python
template_vars = {
    'quantity_format': 'integer',
    'additional_instructions': 'Pay special attention to protection coordination.'
}
```
