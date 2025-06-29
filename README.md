# Narrative Deconstruction Toolkit
## Or, "Yet Another LLM Proxy"
---

Look, I built a thing. It’s a simple, maybe even stupid, web app that pokes Azure OpenAI with a stick to see what falls out. You give it some text, and it tries to tell you about the sneaky rhetorical tricks, biases, and what the author conveniently forgot to mention.

Don't expect miracles. It's just a fancy frontend for an API call.

### What It Supposedly Does

-   **Finds Hidden Stuff**: Tries to sniff out unstated assumptions, bias, and rhetorical shenanigans.
-   **Makes It Look Pretty**: You get some flashy heatmaps and tooltips when you hover over the text. Ooooh, colors.
-   **The Code Isn't a Complete Dumpster Fire**: I tried to keep things from getting too messy. There are separate folders for the API, services, and other bits.

### The Guts of the Operation (Project Structure)

If you dare to look under the hood, this is what you'll find.

```
deconstruction_toolkit/
├── main.py                    # The FastAPI thing that starts it all
├── index.html                 # The one and only HTML page
├── requirements.txt           # All the stuff you need to pip install
├── .env.template              # Copy this to .env, or nothing will work
├── start.sh                   # A lazy way to run it
├── api/
│   └── v1/
│       └── analyze.py         # The single, lonely API endpoint
├── core/
│   ├── config.py              # Handles the .env stuff
│   ├── dspy_program.py        # Where the DSPy magic/mess happens
│   └── prompts.py             # The magic words I send to the AI
├── models/
│   └── analysis.py            # Pydantic models to pretend we're organized
├── services/
│   └── analyzer.py            # The main brain that orchestrates the analysis
```

### What You'll Need to Run This Mess

-   Python 3.13+ (because why not?) 
    - If you are still using Python <3.9, how did you get your time machine to work? Seriously, upgrade.
-   An Azure OpenAI key and endpoint. Or swap it out for another provider in the DSPy config if you're feeling adventurous. I only tested Azure because it gave me some free credits.
    - I also hate azure but money is money, right?
-   A web browser. Obviously.

### Getting This Thing to Run

**1. Set Up Your Lair**

```bash
# Go to wherever you cloned this
cd /path/to/deconstruction_toolkit

# Make a virtual environment so you don't pollute your system
python -m venv .venv
source .venv/bin/activate
```

**2. Install the Junk**

```bash
pip install -r requirements.txt
```

**2.1. Unsolicited Advice**
- Try out [uv](https://github.com/astral-sh/uv), it’s a nice tool for managing Python environments and dependencies. 
    - It’s not required, but it makes life easier. `pip` is here because it's the default and everyone knows it, but `uv` is like the cool kid on the block.

**3. Feed the Beast (Configure .env)**

Copy the template to a new `.env` file.

```bash
cp .env.template .env
```

Now, open `.env` and fill in your Azure secrets(might have to pay $$$). Don't commit this file unless you enjoy leaking credentials, you might as well post it on reddit for fun.

```env
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_KEY=your-super-secret-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01
```

### Fire It Up

You've got options. Pick your poison.

```bash
# The easy way
./start.sh

# The slightly less easy way
python main.py

# The "I want to see all the logs" way
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### See the "Magic"

Open your browser and go to `http://localhost:8000`. Prepare to be mildly whelmed.

### Live Demo (For Now)

I've thrown this thing up on Azure, so you can poke it without having to install anything.

**[https://narrativedoomer.azurewebsites.net/](https://narrativedoomer.azurewebsites.net/)**

A word of warning: LLM calls cost money, and I'm not made of it. If this thing gets used even by some people (unlikely) or I find something more interesting to waste my free credits (likely), the site will go down. Send me your condolences if it does.

### APIs

-   `POST /api/v1/synthesize`: The main endpoint that does all the work.
-   `GET /`: Serves the webpage.
-   `GET /api/health`: To check if it's alive.

**Request:**
```json
{
    "text": "Your text to analyze..."
}
```

**Response (if it doesn't crash):**
```json
{
    "foundational_assumptions": [
        "The author assumes the reader is familiar with the basic concepts of the topic."
    ],
    "synthesized_text": [
        {
            "sentence": "This new product is a revolutionary step forward for the industry.",
            "bias_score": 0.8,
            "justification": "The sentence uses strong positive language ('revolutionary', 'step forward') without providing evidence, indicating a strong positive bias.",
            "tactics": [
                {
                    "phrase": "revolutionary step forward",
                    "tactic": "Loaded Language",
                    "explanation": "Uses emotionally charged words to influence the reader's perception.",
                    "type": "framing"
                }
            ]
        }
    ],
    "omissions": [
        {
            "omitted_perspective": "Potential downsides or risks of the new product.",
            "potential_impact": "The reader may get an incomplete and overly optimistic view of the product."
        }
    ]
}
```

### Demo Mode / Dummy Data

Perfect for showing off without burning through your API credits. This is especially useful when deploying to places where you want people to see the functionality without allowing new API calls.

**Enable Demo Mode:**

Set this in your `.env` file:
```env
USE_DUMMY_DATA=True
```

**What happens in Demo Mode:**
- The input box gets disabled with a clear "Demo Mode" banner
- Pre-generated, comprehensive analysis results are automatically loaded
- No API calls are made to Azure OpenAI (saves money!)
- Users can explore the full functionality without cost

**API Key Protection:**

When demo mode is disabled (`USE_DUMMY_DATA=False`), you can protect the API with a key:

```env
USE_DUMMY_DATA=False
API_KEY=your-secret-api-key-here
```

With API key protection enabled:
- Users must provide the API key in the `Authorization` header as `Bearer token`
- Frontend will prompt for the API key when needed
- Prevents unauthorized usage when deployed publicly

**Configuration Examples:**

```env
# For public demos (recommended for Azure deployments)
USE_DUMMY_DATA=True
API_KEY=your-secret-api-key-here

# For protected production use
USE_DUMMY_DATA=False  
API_KEY=your-secret-api-key-here

# For local development (no protection)
USE_DUMMY_DATA=False
# API_KEY= (leave empty or comment out)
```

**Demo Data Features:**

The dummy data includes realistic examples of:
- Sentence-level bias analysis with scores (-1.0 to 1.0)
- Rhetorical tactic identification (loaded language, false premises, etc.)
- Foundational assumption extraction
- Significant omission analysis
- Interactive tooltips with detailed explanations

### Azure Deployment Recommendations

For cost-effective Azure deployment:

**1. Use Demo Mode by Default**
```env
USE_DUMMY_DATA=True
API_KEY=strong-random-key-here
```

**2. Container Deployment (Azure Container Instances)**
```dockerfile
# Dockerfile (create this in your project root)
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

**3. Environment Variables in Azure**
Set these in your Azure Container Instance or App Service:
- `USE_DUMMY_DATA=True`
- `API_KEY=your-secret-key`
- `HOST=0.0.0.0`
- `PORT=8000`

**4. For Production Use (with real LLM calls)**
- Set `USE_DUMMY_DATA=False`
- Configure all Azure OpenAI variables
- Set a strong `API_KEY`
- Monitor costs closely!

**Cost Savings:**
- Demo mode = $0 per analysis
- Real mode = ~$0.01-0.05 per analysis (depending on text length and model)

### You Want to Contribute? Seriously?

Fine. If you find a bug or have an idea, open an issue or a pull request. I'll ignore it proudly. But why not fix it yourself? I mean, it's not like I'm paying you but vibecoding is free, right?

### License? What License?

Let's be real, this isn't going to be the next big thing. It's a weekend project that got a little out of hand.

So, here's the deal: **Do whatever you want with it.** Use it, break it, fix it, claim you wrote it—I don't care. 

If you're actually using this for something interesting, I'd be curious to hear about it. Not to stop you, but just to understand what weirdass shit you're working on.

### Coded with vibes by Claude 4, documented by Gemini 2.5 Pro with a little bit of my wit. <br/> I am also wondering why it is in my github LOL.
