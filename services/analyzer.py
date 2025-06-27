import dspy
from core import config
from core.dspy_program import DeconstructionPipeline
from models.analysis import SynthesisResult
from typing import List


async def run_synthesis_analysis(text: str, lenses: List[str]) -> SynthesisResult:
    """
    Runs the DSPy-based deconstruction analysis pipeline.

    Args:
        text: The text to analyze
        lenses: Analysis lenses (maintained for API compatibility but not used in DSPy version)

    Returns:
        SynthesisResult containing the complete analysis
    """
    try:
        print("Starting DSPy-based synthesis analysis...")

        # Configure DSPy language model using the newer dspy.LM interface
        lm = dspy.LM(
            model=f"azure/{config.AZURE_OPENAI_DEPLOYMENT_NAME}",
            api_key=config.AZURE_OPENAI_KEY,
            api_base=config.AZURE_OPENAI_ENDPOINT,
            api_version=config.AZURE_OPENAI_API_VERSION,
            max_tokens=4096,
            temperature=0.0
        )
        dspy.settings.configure(lm=lm)

        # Instantiate and run the DSPy pipeline
        pipeline = DeconstructionPipeline()
        result = pipeline(text=text)

        # Convert to SynthesisResult Pydantic model
        synthesis_result = SynthesisResult(**result)

        print("Successfully completed DSPy-based analysis")
        return synthesis_result

    except Exception as e:
        print(f"Error during DSPy synthesis analysis: {e}")
        return _create_error_response(text, str(e))


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
