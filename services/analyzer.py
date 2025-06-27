import dspy
import asyncio
from core import config
from core.dspy_program import DeconstructionPipeline
from models.analysis import SynthesisResult, SynthesizedSentence, Omission
from typing import List


def _configure_dspy() -> None:
    """
    Configure DSPy with Azure OpenAI settings.
    This ensures proper LM configuration for the current context.
    """
    try:
        lm = dspy.LM(
            model=f"azure/{config.AZURE_OPENAI_DEPLOYMENT_NAME}",
            api_key=config.AZURE_OPENAI_KEY,
            api_base=config.AZURE_OPENAI_ENDPOINT,
            api_version=config.AZURE_OPENAI_API_VERSION,
            max_tokens=4096,
            temperature=0.0
        )

        dspy.settings.configure(lm=lm)
        print("DSPy configured successfully with Azure OpenAI")

    except Exception as e:
        print(f"Error configuring DSPy: {e}")
        raise


# Global pipeline instance (created after configuration)
_pipeline = None


def _get_pipeline() -> DeconstructionPipeline:
    """Get or create the global pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _configure_dspy()
        _pipeline = DeconstructionPipeline()
    return _pipeline


async def run_synthesis_analysis(text: str, lenses: List[str]) -> SynthesisResult:
    """
    Runs the DSPy-based deconstruction analysis pipeline asynchronously.

    Uses DSPy's native async support with the latest version (2.6.27+)
    which includes proper acall() methods and asyncify utility.

    Args:
        text: The text to analyze
        lenses: Analysis lenses (maintained for API compatibility)

    Returns:
        SynthesisResult containing the complete analysis
    """
    try:
        print("Starting async DSPy analysis with native support...")

        # Get the configured pipeline
        pipeline = _get_pipeline()

        # Use the pipeline's native aforward method for async execution
        # This leverages DSPy 2.6+ async capabilities
        result = await pipeline.aforward(text=text)

        # Convert to SynthesisResult Pydantic model
        synthesis_result = SynthesisResult(**result)

        print("Successfully completed async DSPy analysis")
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
        basic_sentences.append(SynthesizedSentence(
            sentence=sentence,
            bias_score=0.0,
            justification="Analysis unavailable due to system error",
            tactics=[]
        ))

    return SynthesisResult(
        foundational_assumptions=[f"Analysis failed: {error_message}"],
        synthesized_text=basic_sentences,
        omissions=[Omission(
            omitted_perspective="Complete analysis unavailable",
            potential_impact=f"System error prevented full analysis: {error_message}"
        )]
    )
