"""
Dummy data service to provide sample analysis results when USE_DUMMY_DATA=True.
This allows users to see the functionality without making expensive LLM API calls.
"""

from models.analysis import SynthesisResult, SynthesizedSentence, EmbeddedTactic, Omission
from typing import List


def get_dummy_synthesis_result(text: str) -> SynthesisResult:
    """
    Returns a comprehensive dummy analysis result for demonstration purposes.

    Args:
        text: The input text (used for context but actual analysis is mocked)

    Returns:
        SynthesisResult with realistic dummy data
    """

    # Create dummy tactics
    dummy_tactics = [
        EmbeddedTactic(
            phrase="external hands start extracting",
            tactic="Loaded Language",
            explanation="Uses emotionally charged language to frame resource extraction as inherently exploitative",
            type="framing"
        ),
        EmbeddedTactic(
            phrase="boom, the whole balance shatters",
            tactic="Dramatic Escalation",
            explanation="Uses dramatic language to amplify the perceived consequences",
            type="emotional manipulation"
        ),
        EmbeddedTactic(
            phrase="Now let's play fair",
            tactic="False Fairness Appeal",
            explanation="Presents a biased premise as if it's the fair or reasonable position",
            type="false premise"
        ),
        EmbeddedTactic(
            phrase="That's the common-sense view, right?",
            tactic="Rhetorical Validation",
            explanation="Uses rhetorical questions to make contested claims seem obvious",
            type="consensus manipulation"
        ),
        EmbeddedTactic(
            phrase="things get spicy",
            tactic="Casual Metaphor",
            explanation="Uses informal language to normalize complex political-economic conflicts",
            type="minimization"
        ),
        EmbeddedTactic(
            phrase="mass-producing aspirations",
            tactic="Industrial Metaphor",
            explanation="Frames human desires and goals as manufactured products to suggest manipulation",
            type="mechanistic framing"
        )
    ]

    # Create dummy synthesized sentences with varied bias scores and tactics
    dummy_sentences = [
        SynthesizedSentence(
            sentence="Every country, every piece of land, has the raw potential for a happy, satisfied life.",
            bias_score=0.3,
            justification="Presents an idealistic view that oversimplifies complex geopolitical realities and assumes universal definitions of 'happiness' and 'satisfaction'",
            tactics=[]
        ),
        SynthesizedSentence(
            sentence="But the moment external hands start extracting resources without contributing to local development.. boom, the whole balance shatters.",
            bias_score=-0.7,
            justification="Uses loaded language and dramatic framing to portray all external resource extraction as inherently destructive, ignoring potential benefits or collaborative arrangements",
            tactics=[dummy_tactics[0], dummy_tactics[1]]
        ),
        SynthesizedSentence(
            sentence="Now let's play fair.",
            bias_score=-0.4,
            justification="Frames the following argument as inherently fair while actually introducing contested political premises",
            tactics=[dummy_tactics[2]]
        ),
        SynthesizedSentence(
            sentence="Assume nation-states are real.",
            bias_score=0.1,
            justification="While seemingly neutral, this assumption privileges the Westphalian state system over other forms of political organization",
            tactics=[]
        ),
        SynthesizedSentence(
            sentence="Tangible.",
            bias_score=0.2,
            justification="Emphasizes the material reality of borders while ignoring their constructed and contested nature",
            tactics=[]
        ),
        SynthesizedSentence(
            sentence="The rightful owners of the land within their borders.",
            bias_score=-0.6,
            justification="Presents a highly contested claim about territorial sovereignty as fact, ignoring indigenous rights and historical complexities",
            tactics=[]
        ),
        SynthesizedSentence(
            sentence="That's the common-sense view, right?",
            bias_score=-0.5,
            justification="Uses rhetorical validation to make a contested political position seem like obvious common sense",
            tactics=[dummy_tactics[3]]
        ),
        SynthesizedSentence(
            sentence="So if \"progress\" exists, it's only valid under the assumption that nations are using their resources well and running their ideologies efficiently.",
            bias_score=0.4,
            justification="Makes progress conditional on national efficiency while putting 'progress' in scare quotes, suggesting skepticism about the concept itself",
            tactics=[]
        ),
        SynthesizedSentence(
            sentence="But that's where things get spicy because not everyone wants the same life.",
            bias_score=-0.3,
            justification="Uses casual language to minimize serious ideological conflicts and cultural differences",
            tactics=[dummy_tactics[4]]
        ),
        SynthesizedSentence(
            sentence="Cue the arrival of economic and political ideology.",
            bias_score=0.2,
            justification="Presents ideology as something external that 'arrives' rather than something inherent to all political systems",
            tactics=[]
        ),
        SynthesizedSentence(
            sentence="And when ideals start mass-producing aspirations, you've got yourself a system of control.",
            bias_score=-0.8,
            justification="Uses industrial metaphors to frame all ideological influence as manipulative control, ignoring legitimate political mobilization",
            tactics=[dummy_tactics[5]]
        )
    ]

    # Create dummy foundational assumptions
    dummy_assumptions = [
        "Nation-states are the primary legitimate political units for organizing society",
        "External resource extraction is inherently exploitative rather than potentially beneficial",
        "There exists an objective measure of how well nations 'use their resources'",
        "Political ideologies are primarily systems of control rather than genuine belief systems",
        "Progress is a questionable concept that may not exist in any meaningful sense",
        "All aspirations created by ideological systems are artificially manufactured rather than authentic"
    ]

    # Create dummy omissions
    dummy_omissions = [
        Omission(
            omitted_perspective="Indigenous sovereignty and land rights",
            potential_impact="Fails to acknowledge that many current nation-state borders were established through colonization, ignoring indigenous claims and alternative concepts of territorial sovereignty"
        ),
        Omission(
            omitted_perspective="Benefits of international trade and cooperation",
            potential_impact="The framing of all external involvement as extractive ignores mutual benefits, technology transfer, and collaborative development that can result from international engagement"
        ),
        Omission(
            omitted_perspective="Historical context of resource extraction",
            potential_impact="Lacks discussion of how colonial histories shape current resource relationships, missing important context for understanding contemporary dynamics"
        ),
        Omission(
            omitted_perspective="Alternative political organization models",
            potential_impact="By assuming nation-states as the natural unit, it ignores federal systems, supranational governance, and other forms of political organization"
        ),
        Omission(
            omitted_perspective="Positive aspects of ideological mobilization",
            potential_impact="Framing all ideology as control mechanisms ignores how shared values and ideals can enable positive social movements and democratic participation"
        )
    ]

    return SynthesisResult(
        foundational_assumptions=dummy_assumptions,
        synthesized_text=dummy_sentences,
        omissions=dummy_omissions
    )


def get_dummy_simple_result(text: str) -> SynthesisResult:
    """
    Returns a simpler dummy result for shorter texts or quick demonstrations.

    Args:
        text: The input text

    Returns:
        SynthesisResult with basic dummy data
    """

    # Simple sentence analysis
    sentences = [s.strip() + "." for s in text.split('.')
                 if s.strip()][:3]  # Max 3 sentences

    dummy_sentences = []
    bias_scores = [0.2, -0.4, 0.1]  # Varied scores

    for i, sentence in enumerate(sentences):
        bias_score = bias_scores[i] if i < len(bias_scores) else 0.0

        dummy_sentences.append(SynthesizedSentence(
            sentence=sentence,
            bias_score=bias_score,
            justification=f"Demo analysis: This sentence shows {abs(bias_score):.1f} level of bias {'toward' if bias_score > 0 else 'against'} the presented viewpoint.",
            tactics=[
                EmbeddedTactic(
                    phrase=" ".join(sentence.split()[:3]) if len(
                        sentence.split()) >= 3 else sentence,  # First few words
                    tactic="Sample Tactic",
                    explanation="This is a demonstration of how rhetorical tactics would be identified",
                    type="demo"
                )
            ] if i == 1 else []  # Only add tactics to middle sentence
        ))

    return SynthesisResult(
        foundational_assumptions=[
            "Demo assumption: This is an example of a foundational assumption that would be identified",
            "Demo assumption: Another example assumption underlying the argument"
        ],
        synthesized_text=dummy_sentences,
        omissions=[
            Omission(
                omitted_perspective="Alternative viewpoint demonstration",
                potential_impact="This shows how missing perspectives would be identified in the analysis"
            )
        ]
    )
