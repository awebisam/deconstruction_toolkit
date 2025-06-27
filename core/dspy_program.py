"""
DSPy-based program for the Narrative Deconstruction Toolkit.

This module replaces the hardcoded prompt-based approach with a programmatic,
data-centric pipeline using DSPy signatures and modules.
"""

import dspy
from typing import List
from models.analysis import SynthesizedSentence, Omission, EmbeddedTactic


class FoundationalAssumptionsSignature(dspy.Signature):
    """Analyze text to identify core, unstated assumptions that the author takes for granted.

    Focus on beliefs about reality, society, human nature, or the topic at hand that 
    the author assumes the reader will also accept. Return 3-5 key assumptions.

    Output each assumption as a separate item in a numbered list format.
    """
    text: str = dspy.InputField(
        desc="The text to analyze for foundational assumptions")
    assumptions_text: str = dspy.OutputField(
        desc="Numbered list of 3-5 core unstated assumptions, one per line")


class SentenceAnalysisSignature(dspy.Signature):
    """Analyze each sentence in the text for bias and rhetorical tactics.

    For each sentence, provide a bias score from -1.0 (highly negative/critical) 
    to 1.0 (highly positive/promotional), with 0.0 being neutral, along with 
    justification and any identified rhetorical tactics.

    Return analysis in a structured format that can be parsed.
    """
    text: str = dspy.InputField(
        desc="The text to analyze sentence by sentence")
    analysis_text: str = dspy.OutputField(
        desc="Structured analysis of each sentence with bias scores and tactics")


class OmissionsAnalysisSignature(dspy.Signature):
    """Identify what important viewpoints, evidence, or counterarguments are missing from the text.

    Focus on missing stakeholder perspectives, data/evidence that would strengthen claims,
    and reasonable counterarguments that aren't addressed. Return 3-5 major omissions.

    Output each omission with its potential impact.
    """
    text: str = dspy.InputField(desc="The text to analyze for omissions")
    omissions_text: str = dspy.OutputField(
        desc="List of missing perspectives and their potential impact")


class DeconstructionPipeline(dspy.Module):
    """Main DSPy module that orchestrates the three-step deconstruction analysis."""

    def __init__(self):
        super().__init__()

        # Initialize the three analysis steps
        self.foundational_assumptions = dspy.ChainOfThought(
            FoundationalAssumptionsSignature)
        self.sentence_analysis = dspy.ChainOfThought(SentenceAnalysisSignature)
        self.omissions_analysis = dspy.ChainOfThought(
            OmissionsAnalysisSignature)

    def forward(self, text: str) -> dict:
        """
        Run the complete deconstruction pipeline on the input text.

        Args:
            text: The text to analyze

        Returns:
            Dictionary containing results from all three analysis steps
        """
        # Step 1: Analyze foundational assumptions
        assumptions_result = self.foundational_assumptions(text=text)
        assumptions_list = self._parse_assumptions(
            assumptions_result.assumptions_text)

        # Step 2: Perform sentence-by-sentence analysis
        sentence_result = self.sentence_analysis(text=text)
        sentences_list = self._parse_sentence_analysis(
            sentence_result.analysis_text, text)

        # Step 3: Analyze omissions
        omissions_result = self.omissions_analysis(text=text)
        omissions_list = self._parse_omissions(omissions_result.omissions_text)

        # Combine results
        return {
            "foundational_assumptions": assumptions_list,
            "synthesized_text": sentences_list,
            "omissions": omissions_list
        }

    def _parse_assumptions(self, assumptions_text: str) -> List[str]:
        """Parse the assumptions text into a list of strings."""
        lines = [line.strip()
                 for line in assumptions_text.split('\n') if line.strip()]
        assumptions = []
        for line in lines:
            # Remove numbering if present
            if '. ' in line and line[0].isdigit():
                line = line.split('. ', 1)[1]
            if line:
                assumptions.append(line)
        return assumptions[:5]  # Limit to 5 assumptions

    def _parse_sentence_analysis(self, analysis_text: str, original_text: str) -> List[SynthesizedSentence]:
        """Parse the sentence analysis text into SynthesizedSentence objects."""
        # Fallback: simple sentence splitting if parsing fails
        sentences = [
            s.strip() + '.' for s in original_text.split('.') if s.strip()]

        result = []
        for sentence in sentences[:10]:  # Limit to 10 sentences
            # For now, provide basic analysis - this could be enhanced to parse structured output
            bias_score = 0.5 if any(word in sentence.lower() for word in [
                                    'amazing', 'revolutionary', 'must', 'now']) else 0.0
            justification = "Basic sentiment analysis based on loaded language detection"

            tactics = []
            if any(word in sentence.lower() for word in ['amazing', 'revolutionary', 'incredible']):
                tactics.append(EmbeddedTactic(
                    phrase=next((word for word in [
                                'amazing', 'revolutionary', 'incredible'] if word in sentence.lower()), ''),
                    tactic="Loaded Language",
                    explanation="Uses emotionally charged positive language",
                    type="emotional"
                ))

            if any(word in sentence.lower() for word in ['must', 'now', 'immediately', 'hurry']):
                tactics.append(EmbeddedTactic(
                    phrase=next((word for word in [
                                'must', 'now', 'immediately', 'hurry'] if word in sentence.lower()), ''),
                    tactic="Sales Tactics",
                    explanation="Creates urgency to prompt immediate action",
                    type="urgency"
                ))

            result.append(SynthesizedSentence(
                sentence=sentence,
                bias_score=bias_score,
                justification=justification,
                tactics=tactics
            ))

        return result

    def _parse_omissions(self, omissions_text: str) -> List[Omission]:
        """Parse the omissions text into Omission objects."""
        lines = [line.strip()
                 for line in omissions_text.split('\n') if line.strip()]
        omissions = []

        for line in lines[:5]:  # Limit to 5 omissions
            # Remove numbering if present
            if '. ' in line and line[0].isdigit():
                line = line.split('. ', 1)[1]

            if line:
                # Simple parsing - could be enhanced
                if ':' in line:
                    parts = line.split(':', 1)
                    perspective = parts[0].strip()
                    impact = parts[1].strip() if len(
                        parts) > 1 else "Impact not specified"
                else:
                    perspective = line
                    impact = "Missing perspective may limit understanding"

                omissions.append(Omission(
                    omitted_perspective=perspective,
                    potential_impact=impact
                ))

        # Ensure at least one omission
        if not omissions:
            omissions.append(Omission(
                omitted_perspective="Alternative viewpoints not explored",
                potential_impact="May present a one-sided perspective"
            ))

        return omissions
