"""
DSPy-based program for the Narrative Deconstruction Toolkit.

This module implements a robust, production-ready pipeline using DSPy's latest
best practices: class-based Signatures with proper type hints, Predict modules
for structured outputs, and native async support through acall() methods.
All brittle string parsing has been eliminated in favor of structured JSON outputs.
"""

import dspy
import json
import asyncio
from typing import List, Dict, Any
from models.analysis import SynthesizedSentence, Omission


class FoundationalAssumptionsSignature(dspy.Signature):
    """
    Identify foundational, unstated assumptions embedded in a text.

    A foundational assumption is a core belief the author takes for granted,
    assuming the reader will accept it without question. These are often invisible
    pillars supporting the entire argument.

    Consider epistemological, metaphysical, ethical, and social/political assumptions.
    Focus on 3-5 of the most significant foundational assumptions.
    """
    text: str = dspy.InputField(
        desc="The text to analyze for its foundational assumptions."
    )
    assumptions_json: str = dspy.OutputField(
        desc="JSON array of 3-5 core assumptions as strings: [\"assumption1\", \"assumption2\", ...]"
    )


class SentenceAnalysisSignature(dspy.Signature):
    """
    Analyze each sentence in text for bias and rhetorical tactics.

    For each sentence, provide:
    1. Bias score (-1.0 to 1.0): -1.0 = extremely negative, 0.0 = neutral, 1.0 = extremely positive
    2. Justification for the bias score
    3. Rhetorical tactics with exact phrases, tactic names, explanations, and types
    """
    text: str = dspy.InputField(
        desc="The text to be analyzed sentence by sentence for bias and tactics."
    )
    analysis_json: str = dspy.OutputField(
        desc="JSON array of sentence analysis objects with structure: [{\"sentence\": \"...\", \"bias_score\": 0.0, \"justification\": \"...\", \"tactics\": [{\"phrase\": \"...\", \"tactic\": \"...\", \"explanation\": \"...\", \"type\": \"...\"}]}]"
    )


class OmissionsAnalysisSignature(dspy.Signature):
    """
    Identify significant omissions in the text - what is NOT being said.

    Focus on missing perspectives, data/evidence, counterarguments, context,
    and potential consequences. For each omission, describe its potential impact.
    Identify 3-5 major omissions.
    """
    text: str = dspy.InputField(
        desc="The text to analyze for significant omissions."
    )
    omissions_json: str = dspy.OutputField(
        desc="JSON array of omission objects: [{\"omitted_perspective\": \"...\", \"potential_impact\": \"...\"}]"
    )


def _parse_json_with_fallback(json_str: str, fallback_value: Any, field_name: str) -> Any:
    """
    Safely parse JSON output from LLM with fallback handling.

    Args:
        json_str: The JSON string to parse
        fallback_value: Value to return if parsing fails
        field_name: Name of the field for logging

    Returns:
        Parsed JSON data or fallback value
    """
    try:
        # Clean up common LLM output issues
        cleaned = json_str.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        result = json.loads(cleaned)
        return result

    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Warning: Failed to parse {field_name} JSON: {e}")
        print(f"Raw output: {json_str[:200]}...")
        return fallback_value


class DeconstructionPipeline(dspy.Module):
    """
    Modern DSPy module implementing narrative deconstruction with best practices.

    Uses Predict modules with JSON output parsing, native async support through
    acall(), and proper error handling. Eliminates all brittle string parsing
    by using structured JSON outputs with robust fallback logic.
    """

    def __init__(self):
        super().__init__()
        # Use Predict modules for reliable structured outputs
        self.foundational_assumptions = dspy.Predict(
            FoundationalAssumptionsSignature)
        self.sentence_analysis = dspy.Predict(SentenceAnalysisSignature)
        self.omissions_analysis = dspy.Predict(OmissionsAnalysisSignature)

    def _process_assumptions(self, result) -> List[str]:
        """Process assumptions output with fallback."""
        if hasattr(result, 'assumptions_json'):
            assumptions = _parse_json_with_fallback(
                result.assumptions_json,
                ["Analysis temporarily unavailable"],
                "assumptions"
            )
            return assumptions if isinstance(assumptions, list) else [str(assumptions)]
        return ["Analysis temporarily unavailable"]

    def _process_sentence_analysis(self, result, original_text: str) -> List[SynthesizedSentence]:
        """Process sentence analysis output with fallback."""
        if hasattr(result, 'analysis_json'):
            analysis_data = _parse_json_with_fallback(
                result.analysis_json,
                [],
                "sentence_analysis"
            )

            if isinstance(analysis_data, list):
                sentences = []
                for item in analysis_data:
                    if isinstance(item, dict):
                        try:
                            sentences.append(SynthesizedSentence(**item))
                        except Exception as e:
                            print(
                                f"Warning: Invalid sentence analysis item: {e}")
                            # Create a basic fallback sentence
                            sentences.append(SynthesizedSentence(
                                sentence=item.get(
                                    'sentence', 'Unknown sentence'),
                                bias_score=0.0,
                                justification="Analysis format error",
                                tactics=[]
                            ))
                return sentences

        # Fallback: create basic sentence breakdown
        basic_sentences = [
            s.strip() + '.' for s in original_text.split('.') if s.strip()]
        return [
            SynthesizedSentence(
                sentence=sentence,
                bias_score=0.0,
                justification="Analysis temporarily unavailable",
                tactics=[]
            ) for sentence in basic_sentences[:5]
        ]

    def _process_omissions(self, result) -> List[Omission]:
        """Process omissions output with fallback."""
        if hasattr(result, 'omissions_json'):
            omissions_data = _parse_json_with_fallback(
                result.omissions_json,
                [],
                "omissions"
            )

            if isinstance(omissions_data, list):
                omissions = []
                for item in omissions_data:
                    if isinstance(item, dict):
                        try:
                            omissions.append(Omission(**item))
                        except Exception as e:
                            print(f"Warning: Invalid omission item: {e}")
                            # Create a basic fallback omission
                            omissions.append(Omission(
                                omitted_perspective=item.get(
                                    'omitted_perspective', 'Unknown omission'),
                                potential_impact="Analysis format error"
                            ))
                return omissions

        # Fallback omission
        return [Omission(
            omitted_perspective="Analysis temporarily unavailable",
            potential_impact="Unable to identify omissions at this time"
        )]

    def forward(self, text: str) -> Dict[str, Any]:
        """
        Run the complete deconstruction pipeline synchronously.

        Args:
            text: The text to analyze.

        Returns:
            Dictionary with structured results from all three analysis steps.
        """
        try:
            # Execute analyses sequentially for predictable results
            assumptions_result = self.foundational_assumptions(text=text)
            sentence_result = self.sentence_analysis(text=text)
            omissions_result = self.omissions_analysis(text=text)

            return {
                "foundational_assumptions": self._process_assumptions(assumptions_result),
                "synthesized_text": self._process_sentence_analysis(sentence_result, text),
                "omissions": self._process_omissions(omissions_result)
            }

        except Exception as e:
            print(f"Error in DSPy pipeline forward: {e}")
            return self._create_error_response(text, str(e))

    async def aforward(self, text: str) -> Dict[str, Any]:
        """
        Run the complete deconstruction pipeline asynchronously using DSPy's native async support.

        Args:
            text: The text to analyze.

        Returns:
            Dictionary with structured results from all three analysis steps.
        """
        try:
            # Use DSPy's native async support through acall()
            # Execute in parallel for better performance
            assumptions_task = self.foundational_assumptions.acall(text=text)
            sentence_task = self.sentence_analysis.acall(text=text)
            omissions_task = self.omissions_analysis.acall(text=text)

            # Wait for all analyses to complete
            assumptions_result, sentence_result, omissions_result = await asyncio.gather(
                assumptions_task,
                sentence_task,
                omissions_task,
                return_exceptions=True
            )

            # Handle any exceptions from individual analyses
            if isinstance(assumptions_result, Exception):
                print(f"Assumptions analysis failed: {assumptions_result}")
                assumptions_result = type(
                    'obj', (object,), {'assumptions_json': '[]'})()

            if isinstance(sentence_result, Exception):
                print(f"Sentence analysis failed: {sentence_result}")
                sentence_result = type(
                    'obj', (object,), {'analysis_json': '[]'})()

            if isinstance(omissions_result, Exception):
                print(f"Omissions analysis failed: {omissions_result}")
                omissions_result = type(
                    'obj', (object,), {'omissions_json': '[]'})()

            return {
                "foundational_assumptions": self._process_assumptions(assumptions_result),
                "synthesized_text": self._process_sentence_analysis(sentence_result, text),
                "omissions": self._process_omissions(omissions_result)
            }

        except Exception as e:
            print(f"Error in DSPy pipeline aforward: {e}")
            return self._create_error_response(text, str(e))

    def _create_error_response(self, text: str, error_message: str) -> Dict[str, Any]:
        """Create a structured error response."""
        # Basic sentence breakdown for error case
        sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        error_sentences = [
            SynthesizedSentence(
                sentence=sentence,
                bias_score=0.0,
                justification=f"Analysis failed: {error_message}",
                tactics=[]
            ) for sentence in sentences[:3]
        ]

        return {
            "foundational_assumptions": [f"Analysis failed: {error_message}"],
            "synthesized_text": error_sentences,
            "omissions": [Omission(
                omitted_perspective="Analysis unavailable due to error",
                potential_impact=f"System error prevented analysis: {error_message}"
            )]
        }
