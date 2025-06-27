# Narrative Deconstruction Toolkit

A prototype web application that uses AI to identify loaded language, persuasive techniques, and manipulative rhetoric in text.

## Features

- **Real-time Analysis**: Powered by Azure OpenAI to identify rhetorical techniques
- **Interactive Interface**: Hover over highlighted phrases to see explanations
- **Comprehensive Detection**: Identifies various forms of loaded language including:
  - Emotional manipulation
  - False assertions as facts
  - Ad hominem attacks
  - Appeal to authority
  - Fear-based rhetoric
  - And more...

## Prerequisites

- Python 3.8+
- Azure OpenAI API access with deployment
- Modern web browser

## Setup Instructions

### 1. Clone and Navigate
```bash
cd /path/to/deconstruction_toolkit
```

### 2. Set up Python Virtual Environment
The virtual environment should already be configured. If not:
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Azure OpenAI
Edit the `.env` file with your Azure OpenAI credentials:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_KEY=your-32-character-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01
```

### 5. Start the Application
```bash
# Option 1: Use the startup script
./start.sh

# Option 2: Run directly
python main.py

# Option 3: Use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Access the Application
Open your browser and navigate to: `http://localhost:8000`

## API Endpoints

- `GET /` - Main application interface
- `POST /api/deconstruct` - Analyze text for loaded language
- `GET /api/health` - Health check

## Usage

1. Paste text into the input area
2. Click "Deconstruct" to analyze
3. View highlighted phrases in the processed text
4. Hover over highlights to see explanations
5. Review the analysis breakdown below

## Example Analysis

The system can identify phrases like:
- "Common sense tells us..." (Assertion as fact)
- "So-called experts..." (Character discrediting)
- "Hard-working families..." (Emotional manipulation)
- "Obviously..." (False certainty)

## Development

### Project Structure
```
.
├── main.py              # FastAPI backend
├── index.html           # Frontend interface
├── requirements.txt     # Python dependencies
├── .env                # Configuration (not in git)
├── start.sh            # Startup script
└── README.md           # This file
```

### Key Components

**Backend (`main.py`)**:
- FastAPI application with CORS support
- Azure OpenAI integration
- Structured prompt for rhetorical analysis
- JSON API for text processing

**Frontend (`index.html`)**:
- Responsive design with Tailwind CSS
- Interactive highlighting with tooltips
- Real-time API communication
- Clean, modern interface

## Contributing

This is a prototype for educational and experimental purposes. Contributions welcome!

## License

For educational and experimental purposes only.

---

**Note**: Make sure to keep your Azure OpenAI credentials secure and never commit the `.env` file to version control.
