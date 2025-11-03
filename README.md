# Electrical Component Analyzer

A Streamlit web application for analyzing electrical diagrams and generating Bills of Materials (BOM) using AI-powered component recognition.

## Features

- **Multi-format Support**: Upload electrical diagrams in PDF, PNG, or JPEG formats
- **AI-Powered Analysis**: Uses Claude Sonnet AI to identify electrical components
- **Multiple Analysis Modes**: Default, Power Quality, Load Analysis, and Fault Detection
- **BOM Generation**: Automatically generates formatted Bills of Materials
- **Responsive Web Interface**: Modern, mobile-friendly Streamlit application

## Installation

### Prerequisites

1. **Python 3.8+** - Make sure you have Python installed
2. **Poppler** (for PDF processing on Windows):
   - Download from: https://blog.alivate.com.au/poppler-windows/
   - Extract to `C:\poppler\`
   - Add `C:\poppler\bin` to your system PATH

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd scanner
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API settings**:
   - Edit `settings.py` with your API credentials
   - Set `LLM_API_KEY`, `LLM_API_BASE`, and `LLM_MODEL`

## Usage

### Running the Application

```bash
streamlit run server.py
```

The application will open in your default web browser at `http://localhost:8501`

### Using the App

1. **Select Analysis Mode**: Choose from the sidebar (Default, Power Quality, etc.)
2. **Upload Diagram**: Drag and drop or browse for electrical diagram files
3. **View Results**: The app will analyze the diagram and display:
   - Raw component analysis
   - Formatted Bill of Materials
   - Component count and details

## Project Structure

```
scanner/
├── client.py              # LLM client for AI analysis
├── server.py              # Streamlit web application
├── settings.py            # API configuration
├── requirements.txt       # Python dependencies
├── lib/
│   └── promt_manager.py   # Template management system
└── prompts/               # Jinja2 prompt templates
    ├── system_prompt.txt
    ├── component_analysis.j2
    ├── config.yaml
    └── README.md
```

## Dependencies

- **streamlit**: Web framework
- **openai**: Claude AI API client
- **pdf2image**: PDF to image conversion
- **Pillow**: Image processing
- **Jinja2**: Template engine
- **PyYAML**: Configuration management

## API Configuration

Update `settings.py` with your API credentials:

```python
LLM_API_KEY = "your-api-key-here"
LLM_API_BASE = "https://api.anthropic.com"
LLM_MODEL = "claude-3-sonnet-20240229"
```

## Development

### Code Formatting
```bash
pip install black
black .
```

### Linting
```bash
pip install ruff
ruff check .
```

## License

[Add your license information here]

## Support

For support and questions, contact the development team at Brainium Information Technologies Pvt. Ltd.