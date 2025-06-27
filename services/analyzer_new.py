import json
from openai import AzureOpenAI
from core import config, prompts
from models.analysis import SynthesisResult
from typing import List
import asyncio

client = AzureOpenAI(
    azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
    api_key=config.AZURE_OPENAI_KEY,
    api_version=config.AZURE_OPENAI_API_VERSION,
)


async def run_synthesis_analysis(text: str, lenses: List[str]) -> SynthesisResult:
    # Note: The 'lenses' parameter is kept for future-proofing, but for now,
    # the single prompt performs all analyses. We could use it to conditionally
    # remove parts of the JSON from the final output if needed.
    try:
        response = client.chat.completions.create(
            model=config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompts.SYNTHESIS_PROMPT},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=4096  # Increase max tokens for complex, combined analysis
        )
        analysis_data = json.loads(response.choices[0].message.content)
        return SynthesisResult(**analysis_data)
    except Exception as e:
        print(f"Error during synthesis analysis: {e}")
        return SynthesisResult(synthesized_text=[], omissions=[])
