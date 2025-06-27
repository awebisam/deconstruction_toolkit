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
    """
    Orchestrates a multi-step analysis approach that breaks down the complex task
    into simpler, more focused API calls to improve reliability and reduce truncation issues.
    """
    try:
        print("Starting multi-step synthesis analysis...")

        # Step 1: Get foundational assumptions
        print("Step 1: Analyzing foundational assumptions...")
        assumptions_data = await _get_foundational_assumptions(text)

        # Step 2: Get sentence-by-sentence analysis
        print("Step 2: Performing sentence analysis...")
        sentence_data = await _get_sentence_analysis(text)

        # Step 3: Get omissions analysis
        print("Step 3: Analyzing omissions...")
        omissions_data = await _get_omissions_analysis(text)

        # Combine the results
        combined_result = {
            "foundational_assumptions": assumptions_data.get("foundational_assumptions", []),
            "synthesized_text": sentence_data.get("sentence_analysis", []),
            "omissions": omissions_data.get("omissions", [])
        }

        print("Successfully completed multi-step analysis")
        return SynthesisResult(**combined_result)

    except Exception as e:
        print(f"Error during synthesis analysis: {e}")
        return _create_error_response(text, str(e))


async def _get_foundational_assumptions(text: str) -> dict:
    """Step 1: Extract foundational assumptions using a focused prompt."""
    try:
        response = client.chat.completions.create(
            model=config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompts.FOUNDATIONAL_ASSUMPTIONS_PROMPT},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=2048
        )

        result = _safe_json_parse(
            response.choices[0].message.content, "foundational assumptions")
        print(
            f"Found {len(result.get('foundational_assumptions', []))} foundational assumptions")
        return result

    except Exception as e:
        print(f"Error in foundational assumptions analysis: {e}")
        return {"foundational_assumptions": [f"Analysis error: {str(e)}"]}


async def _get_sentence_analysis(text: str) -> dict:
    """Step 2: Analyze sentences for bias and tactics using a focused prompt."""
    try:
        response = client.chat.completions.create(
            model=config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompts.SENTENCE_ANALYSIS_PROMPT},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=4096
        )

        result = _safe_json_parse(
            response.choices[0].message.content, "sentence analysis")

        # Validate and clean the sentence analysis data
        cleaned_result = _clean_sentence_analysis_data(result)
        sentence_count = len(cleaned_result.get('sentence_analysis', []))
        print(f"Analyzed {sentence_count} sentences")
        return cleaned_result

    except Exception as e:
        print(f"Error in sentence analysis: {e}")
        # Create a fallback response with basic sentence breakdown
        sentences = [s.strip() + "." for s in text.split('.') if s.strip()]
        fallback_analysis = []
        # Limit to prevent overwhelming response
        for sentence in sentences[:10]:
            fallback_analysis.append({
                "sentence": sentence,
                "bias_score": 0.0,
                "justification": f"Analysis error: {str(e)}",
                "tactics": []
            })
        return {"sentence_analysis": fallback_analysis}


async def _get_omissions_analysis(text: str) -> dict:
    """Step 3: Analyze what perspectives or evidence are missing."""
    try:
        response = client.chat.completions.create(
            model=config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompts.OMISSIONS_ANALYSIS_PROMPT},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=2048
        )

        result = _safe_json_parse(
            response.choices[0].message.content, "omissions analysis")

        # Validate and clean the omissions data
        cleaned_result = _clean_omissions_data(result)
        omission_count = len(cleaned_result.get('omissions', []))
        print(f"Identified {omission_count} potential omissions")
        return cleaned_result

    except Exception as e:
        print(f"Error in omissions analysis: {e}")
        return {
            "omissions": [{
                "omitted_perspective": "Analysis incomplete due to error",
                "potential_impact": f"Could not complete omissions analysis: {str(e)}"
            }]
        }


def _create_error_response(text: str, error_message: str) -> SynthesisResult:
    """Create a minimal error response when the entire analysis fails."""
    print(f"Creating error response for: {error_message}")

    # At minimum, provide a basic sentence breakdown
    sentences = [s.strip() + "." for s in text.split('.') if s.strip()]
    basic_sentences = []

    for sentence in sentences[:5]:  # Limit to first 5 sentences
        basic_sentences.append({
            "sentence": sentence,
            "bias_score": 0.0,
            "justification": "Analysis unavailable due to system error",
            "tactics": []
        })

    return SynthesisResult(
        foundational_assumptions=[f"Analysis failed: {error_message}"],
        synthesized_text=basic_sentences,
        omissions=[{
            "omitted_perspective": "Complete analysis unavailable",
            "potential_impact": f"System error prevented full analysis: {error_message}"
        }]
    )


def _clean_sentence_analysis_data(data: dict) -> dict:
    """Clean and validate sentence analysis data to ensure proper structure."""
    if 'sentence_analysis' not in data:
        return {'sentence_analysis': []}

    cleaned_sentences = []
    for item in data['sentence_analysis']:
        if isinstance(item, dict) and 'sentence' in item:
            cleaned_item = {
                'sentence': str(item.get('sentence', '')),
                'bias_score': float(item.get('bias_score', 0.0)),
                'justification': str(item.get('justification', '')),
                'tactics': []
            }

            # Clean tactics array
            tactics = item.get('tactics', [])
            if isinstance(tactics, list):
                for tactic in tactics:
                    if isinstance(tactic, dict):
                        cleaned_tactic = {
                            'phrase': str(tactic.get('phrase', '')),
                            'tactic': str(tactic.get('tactic', 'Unknown')),
                            'explanation': str(tactic.get('explanation', '')),
                            'type': str(tactic.get('type', 'unknown'))
                        }
                        cleaned_item['tactics'].append(cleaned_tactic)

            cleaned_sentences.append(cleaned_item)

    return {'sentence_analysis': cleaned_sentences}


def _clean_omissions_data(data: dict) -> dict:
    """Clean and validate omissions data to ensure proper Pydantic structure."""
    if 'omissions' not in data:
        return {'omissions': []}

    cleaned_omissions = []
    for item in data['omissions']:
        if isinstance(item, dict):
            # Handle different possible structures from AI response
            omitted_perspective = item.get('omitted_perspective') or item.get(
                'perspective') or item.get('missing_perspective') or 'Unknown perspective'
            potential_impact = item.get('potential_impact') or item.get(
                'impact') or item.get('effect') or 'Impact unknown'

            cleaned_omission = {
                'omitted_perspective': str(omitted_perspective),
                'potential_impact': str(potential_impact)
            }
            cleaned_omissions.append(cleaned_omission)

    return {'omissions': cleaned_omissions}


def _safe_json_parse(response_content: str, step_name: str) -> dict:
    """Safely parse JSON with better error handling for malformed responses."""
    try:
        return json.loads(response_content)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error in {step_name}: {e}")
        print(f"Response content (first 500 chars): {response_content[:500]}")
        print(f"Response content (last 500 chars): {response_content[-500:]}")

        # Try to fix common JSON issues
        try:
            # Remove any text before the first {
            start_idx = response_content.find('{')
            if start_idx > 0:
                response_content = response_content[start_idx:]

            # Remove any text after the last }
            end_idx = response_content.rfind('}')
            if end_idx > 0:
                response_content = response_content[:end_idx + 1]

            # Try parsing again
            return json.loads(response_content)
        except json.JSONDecodeError:
            print(f"Could not fix JSON parsing error in {step_name}")
            return {}
