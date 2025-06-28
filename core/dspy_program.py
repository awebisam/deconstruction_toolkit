"""
DSPy-based program for the Narrative Deconstruction Toolkit.
"""

import dspy
import asyncio
from typing import List, Dict, Any
from models.analysis import SynthesizedSentence, Omission


class FoundationalAssumptionsSignature(dspy.Signature):
    """
    You are an expert in critical theory and logical reasoning. Your task is to
    identify the foundational, unstated assumptions embedded in a given text.

    A foundational assumption is a core belief the author takes for granted,
    assuming the reader will accept it without question. These are often invisible
    pillars supporting the entire argument. Do not identify surface-level claims.
    Instead, dig deeper for the fundamental beliefs about the world, society,
    human nature, or morality that *must* be true for the author's argument to hold.

    Consider these categories:
    - **Epistemological:** What does the author assume about the nature of knowledge and truth?
    - **Metaphysical/Ontological:** What does the author assume about the nature of reality?
    - **Ethical/Moral:** What does the author assume about what is right and wrong?
    - **Social/Political:** What does the author assume about how society or power works?

    Identify upto 6 of the most significant foundational assumptions.
    """
    text: str = dspy.InputField(
        desc="The text to analyze for its foundational assumptions."
    )
    assumptions_json: list[str] = dspy.OutputField(
        desc="array of 3-5 core assumptions as strings: [\"assumption1\", \"assumption2\", ...]"
    )


class SentenceAnalysisSignature(dspy.Signature):
    """
    You are a meticulous rhetorical analyst and linguistics expert. Your task is to
    dissect a given text sentence by sentence. For EACH sentence, you will
    provide a structured analysis covering its bias and any embedded rhetorical tactics.

    **Instructions:**
    1.  Go through the text and analyze every single sentence.
    2.  For each sentence, create a `SynthesizedSentence` object.
    3.  **Bias Score:** Assign a `bias_score` from -1.0 to 1.0.
        - **-1.0:** Represents extremely negative, hostile, or derogatory bias.
        - **0.0:** Represents neutral, objective, or purely factual language.
        - **1.0:** Represents extremely positive, laudatory, or promotional bias.
        - Provide a concise `justification` for your score, quoting the specific
          words that signal the bias.
    4.  **Rhetorical Tactics:** Identify all `tactics` within the sentence.
        - For each tactic, the `phrase` must be the *exact* substring from the sentence.
        - Name the `tactic` (e.g., "Appeal to Fear," "Loaded Language," "False Dichotomy").
        - Provide a clear `explanation` of how the tactic functions in this context.
        - Classify the `type` of tactic (e.g., 'Emotional Appeal', 'Logical Fallacy', 'Framing').
    """
    text: str = dspy.InputField(
        desc="The text to be analyzed sentence by sentence for bias and tactics."
    )
    analysis_json: list[SynthesizedSentence] = dspy.OutputField(
        desc="array of sentence analysis objects with structure: [{\"sentence\": \"...\", \"bias_score\": 0.0, \"justification\": \"...\", \"tactics\": [{\"phrase\": \"...\", \"tactic\": \"...\", \"explanation\": \"...\", \"type\": \"...\"}]}]"
    )


class OmissionsAnalysisSignature(dspy.Signature):
    """
    You are an investigative journalist and strategic analyst. Your task is to
    identify the most significant omissions in a given text.

    Think about what is NOT being said. What perspectives are missing? What crucial
    data is absent? What counterarguments are conveniently ignored? An omission
    is a gap in the narrative that, if filled, could significantly alter a
    reader's perception.

    Focus on identifying 3 to 5 major omissions by considering:
    - **Missing Perspectives:** Which relevant stakeholders or affected groups have no voice?
    - **Missing Data/Evidence:** What claims lack supporting evidence that should exist?
    - **Missing Counterarguments:** What are the most compelling arguments against the
      author's position that are not addressed?
    - **Missing Context:** Is there historical, social, or economic context that is
      left out, making the narrative misleading?
    - **Missing Consequences:** Are potential negative outcomes or downsides of the
      proposed ideas ignored?

    For each omission, describe its potential impact on the reader's understanding.
    """
    text: str = dspy.InputField(
        desc="The text to analyze for significant omissions."
    )
    omissions_json: list[Omission] = dspy.OutputField(
        desc="array of omission objects: [{\"omitted_perspective\": \"...\", \"potential_impact\": \"...\"}]"
    )


class DeconstructionPipeline(dspy.Module):
    """
    DSPy module implementing narrative deconstruction.
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
            assumptions = result.assumptions_json
            if isinstance(assumptions, list):
                return assumptions
            elif isinstance(assumptions, str):
                return [assumptions]
            else:
                return [str(assumptions)]
        return ["Analysis temporarily unavailable"]

    def _process_sentence_analysis(self, result, original_text: str) -> List[SynthesizedSentence]:
        """Process sentence analysis output with fallback."""
        if hasattr(result, 'analysis_json'):
            analysis_data = result.analysis_json

            if isinstance(analysis_data, list):
                sentences = []
                for item in analysis_data:
                    if isinstance(item, SynthesizedSentence):
                        sentences.append(item)
                    elif isinstance(item, dict):
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
            omissions_data = result.omissions_json

            if isinstance(omissions_data, list):
                omissions = []
                for item in omissions_data:
                    if isinstance(item, Omission):
                        omissions.append(item)
                    elif isinstance(item, dict):
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
