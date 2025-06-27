# Narrative Deconstruction Toolkit

A robust web application that uses Azure OpenAI to perform multi-layered analysis of text, identifying rhetorical techniques, bias patterns, and missing perspectives through a systematic deconstruction approach.

## Key Features

- **Multi-Step Analysis Engine**: Uses three focused API calls instead of one complex prompt for improved reliability
- **Comprehensive Detection**: Identifies foundational assumptions, bias patterns, and rhetorical tactics
- **Interactive Visualization**: Hover-based tooltips and bias heatmaps for detailed analysis
- **Modern Architecture**: Clean separation of concerns with proper API design

## Project Structure

```
deconstruction_toolkit/
├── main.py                    # FastAPI application entry point
├── index.html                 # Main frontend interface
├── requirements.txt           # Python dependencies
├── .env                      # Environment configuration (create from .env.template)
├── .env.template             # Template for environment variables
├── start.sh                  # Startup script
├── api/
│   └── v1/
│       └── analyze.py        # API endpoints (/api/v1/synthesize)
├── core/
│   ├── config.py            # Configuration management
│   └── prompts.py           # AI prompts for each analysis step
├── models/
│   └── analysis.py          # Pydantic models for request/response
├── services/
│   └── analyzer.py          # Core analysis orchestration
└── static/
    └── js/
        └── synthesis.js     # Frontend JavaScript (separated from HTML)
```

## Prerequisites

- Python 3.8+
- Azure OpenAI API access with GPT-4 deployment
- Modern web browser

## Setup Instructions

### 1. Environment Setup

```bash
# Clone and navigate to the project
cd /path/to/deconstruction_toolkit

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Azure OpenAI

Create a `.env` file from the template:

```bash
cp .env.template .env
```

Edit `.env` with your Azure OpenAI credentials:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_KEY=your-32-character-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01
```

### 4. Start the Application

```bash
# Option 1: Use the startup script
./start.sh

# Option 2: Run directly
python main.py

# Option 3: Use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access the Application

Open your browser and navigate to: `http://localhost:8000`

## API Endpoints

### Analysis Endpoints
- `POST /api/v1/synthesize` - Perform complete text analysis

### System Endpoints  
- `GET /` - Main application interface
- `GET /api/health` - Health check

### API Request Format

```json
{
    "text": "Your text to analyze...",
    "lenses": ["all"]
}
```

### API Response Format

```json
{
    "foundational_assumptions": [
        "Core unstated assumption 1",
        "Core unstated assumption 2"
    ],
    "synthesized_text": [
        {
            "sentence": "Sentence text here.",
            "bias_score": 0.3,
            "justification": "Explanation of bias score",
            "tactics": [
                {
                    "phrase": "specific phrase",
                    "tactic": "Loaded Language",
                    "explanation": "How this tactic works",
                    "type": "emotional"
                }
            ]
        }
    ],
    "omissions": [
        {
            "omitted_perspective": "Missing viewpoint description",
            "potential_impact": "How this affects understanding"
        }
    ]
}
```

## Architecture Improvements (v6.0)

### Multi-Step Analysis Approach
Instead of one complex prompt, the system now uses three focused API calls:

1. **Foundational Assumptions**: Identifies core unstated beliefs
2. **Sentence Analysis**: Analyzes bias and rhetorical tactics per sentence  
3. **Omissions Analysis**: Identifies missing perspectives and evidence

This approach provides:
- Higher reliability (less prone to truncation)
- Better error handling
- More focused, accurate analysis
- Reduced complex JSON parsing issues

### Enhanced Frontend Architecture
- JavaScript separated from HTML into `static/js/synthesis.js`
- Improved DOM manipulation with helper functions
- Better error handling and user feedback
- Cleaner, more maintainable code structure

### Security Improvements
- CORS restricted to localhost during development
- Precise dependency management (no `fastapi[all]`)
- Proper static file serving configuration

## Usage

1. **Input Text**: Paste your text into the analysis area
2. **Run Analysis**: Click "Synthesize" to start the multi-step analysis
3. **Review Results**: 
   - **Foundational Assumptions**: Core beliefs the author takes for granted
   - **Text Analysis**: Sentence-by-sentence breakdown with bias scores and tactical highlights
   - **Omissions**: Missing perspectives and evidence gaps
4. **Interactive Exploration**: Hover over sentences for detailed tooltips showing bias justification and detected tactics

## Example Analysis Capabilities

The system can identify:
- **Bias Patterns**: Scored from -1.0 (negative) to +1.0 (positive)
- **Loaded Language**: "Common sense tells us...", "So-called experts..."
- **Sales Tactics**: Urgency, social proof, authority appeals
- **Missing Perspectives**: Stakeholder viewpoints not represented
- **Evidence Gaps**: Studies, data, or sources needed to validate claims
- **Unaddressed Counterarguments**: Reasonable opposing views ignored

## Development

### Key Components

**Backend (`main.py`)**:
- FastAPI application with proper CORS and static file handling
- Health check and API routing
- Clean separation of concerns

**API Layer (`api/v1/analyze.py`)**:
- RESTful endpoint design
- Request validation with Pydantic models
- Proper error handling

**Analysis Engine (`services/analyzer.py`)**:
- Multi-step orchestration approach
- Individual focused API calls for each analysis type
- Robust error handling and fallback responses

**Frontend (`index.html` + `static/js/synthesis.js`)**:
- Modern responsive design with Tailwind CSS
- Separated JavaScript for maintainability
- Interactive tooltips and bias visualization

### Running in Development Mode

The application supports hot reload for development:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Contributing

This is an educational prototype demonstrating advanced text analysis techniques. Contributions welcome!

## License

For educational and experimental purposes only.

---

**Security Note**: The `.env` file contains sensitive API credentials and should never be committed to version control. Always use the `.env.template` for sharing configuration structure.
