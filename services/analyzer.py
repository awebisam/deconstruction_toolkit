import json
from openai import AzureOpenAI
from core import config, prompts
from models.analysis import SynthesisResult
from typing import List
import asyncio
import re

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
            max_tokens=8192  # Increased to handle longer responses
        )

        raw_response = response.choices[0].message.content
        print("Raw AI response (first 500 chars):")
        print(raw_response[:500])
        print("Raw AI response (last 500 chars):")
        print(raw_response[-500:])

        # Check if response was truncated
        if not raw_response.strip().endswith('}'):
            print("WARNING: Response appears to be truncated!")
            # Try to fix truncation by adding closing braces
            raw_response = fix_truncated_json(raw_response)

        try:
            analysis_data = json.loads(raw_response)
        except json.JSONDecodeError as json_error:
            print(f"JSON parsing error: {json_error}")
            print(
                f"Error at line {json_error.lineno}, column {json_error.colno}")
            print("Attempting to fix common JSON issues...")

            # Try to fix common JSON issues
            fixed_response = fix_json_issues(raw_response)
            try:
                analysis_data = json.loads(fixed_response)
                print("Successfully fixed JSON issues!")
            except json.JSONDecodeError as second_error:
                print(f"Could not fix JSON: {second_error}")
                print("Response was likely truncated. Attempting fallback strategy...")
                # Use fallback strategy for truncated responses
                analysis_data = create_fallback_response(text)

        # Debug: Print the structure to understand what's coming back
        print("Successfully parsed JSON structure")

        # Try to clean up the data before passing to Pydantic
        cleaned_data = clean_synthesis_data(analysis_data)
        return SynthesisResult(**cleaned_data)
    except Exception as e:
        print(f"Error during synthesis analysis: {e}")
        return SynthesisResult(foundational_assumptions=[], synthesized_text=[], omissions=[])


def clean_synthesis_data(data):
    """Clean and normalize the AI response data to match our Pydantic models."""
    cleaned = {}

    # Handle foundational_assumptions
    cleaned["foundational_assumptions"] = data.get(
        "foundational_assumptions", [])

    # Handle synthesized_text
    cleaned_sentences = []
    for sentence_data in data.get("synthesized_text", []):
        cleaned_sentence = {
            "sentence": sentence_data.get("sentence", ""),
            "bias_score": sentence_data.get("bias_score", 0.0),
            "justification": sentence_data.get("justification", ""),
            "tactics": []
        }

        # Clean tactics
        for tactic_data in sentence_data.get("tactics", []):
            cleaned_tactic = {
                "phrase": tactic_data.get("phrase", ""),
                "tactic": tactic_data.get("tactic", "Unknown"),
                "explanation": tactic_data.get("explanation", ""),
                "type": tactic_data.get("type", "unknown")
            }
            cleaned_sentence["tactics"].append(cleaned_tactic)

        cleaned_sentences.append(cleaned_sentence)

    cleaned["synthesized_text"] = cleaned_sentences

    # Handle omissions
    cleaned_omissions = []
    for omission_data in data.get("omissions", []):
        cleaned_omission = {
            "omitted_perspective": omission_data.get("omitted_perspective", omission_data.get("perspective", "Unknown")),
            "potential_impact": omission_data.get("potential_impact", omission_data.get("impact", ""))
        }
        cleaned_omissions.append(cleaned_omission)

    cleaned["omissions"] = cleaned_omissions

    return cleaned


def fix_json_issues(json_string):
    """Attempt to fix common JSON formatting issues."""

    # Remove any text before the first {
    start_idx = json_string.find('{')
    if start_idx > 0:
        json_string = json_string[start_idx:]

    # Remove any text after the last }
    end_idx = json_string.rfind('}')
    if end_idx > 0:
        json_string = json_string[:end_idx + 1]

    # If the JSON doesn't end with }, it's likely truncated
    if not json_string.strip().endswith('}'):
        json_string = fix_truncated_json(json_string)

    # Fix common issues:
    # 1. Remove trailing commas before closing brackets/braces
    json_string = re.sub(r',(\s*[}\]])', r'\1', json_string)

    # 2. Fix missing commas between objects (simple case)
    json_string = re.sub(r'}\s*{', r'},{', json_string)

    # 3. Fix unterminated strings at the end
    if json_string.count('"') % 2 == 1:
        # Find the last quote and see if it's at the end
        last_quote = json_string.rfind('"')
        if last_quote > len(json_string) - 10:  # If quote is near the end
            json_string += '"'

    return json_string


def fix_truncated_json(json_string):
    """Attempt to fix a truncated JSON response by properly closing it."""
    print("Attempting to fix truncated JSON...")

    # Count open vs closed braces and brackets
    open_braces = json_string.count('{') - json_string.count('}')
    open_brackets = json_string.count('[') - json_string.count(']')

    # Check if we're in the middle of a string
    if json_string.count('"') % 2 == 1:
        # Close the unterminated string
        json_string += '"'

    # Close any open arrays
    json_string += ']' * open_brackets

    # Close any open objects
    json_string += '}' * open_braces

    print(
        f"Added {open_brackets} closing brackets and {open_braces} closing braces")
    return json_string


def create_fallback_response(text):
    """Create a minimal fallback response when JSON parsing completely fails."""
    print("Creating fallback response...")

    # Split text into sentences for basic analysis
    sentences = [s.strip() for s in text.split('.') if s.strip()]

    synthesized_sentences = []
    for sentence in sentences[:10]:  # Limit to first 10 sentences
        synthesized_sentences.append({
            "sentence": sentence + ".",
            "bias_score": 0.0,
            "justification": "Analysis unavailable due to response truncation",
            "tactics": []
        })

    return {
        "foundational_assumptions": ["Analysis unavailable due to response truncation"],
        "synthesized_text": synthesized_sentences,
        "omissions": [{
            "omitted_perspective": "Complete analysis unavailable",
            "potential_impact": "Full synthesis could not be completed due to response length limitations"
        }]
    }
