const textInput = document.getElementById('text-input');
const analyzeBtn = document.getElementById('analyze-btn');
const resetBtn = document.getElementById('reset-btn');
const resultsContainer = document.getElementById('results-container');
const API_BASE_URL = 'http://localhost:8000/api/v1';

analyzeBtn.addEventListener('click', async () => {
    const inputText = textInput.value.trim();
    if (!inputText) return alert("Please provide text to analyze.");

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Synthesizing...';
    resultsContainer.innerHTML = '<div class="text-center text-gray-400 animate-pulse">Running synthesis... this may take a moment.</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/synthesize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: inputText, lenses: ["all"] }),
        });
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        const results = await response.json();
        renderSynthesisResults(results);
    } catch (error) {
        resultsContainer.innerHTML = `<p class="text-center text-red-400">An error occurred: ${error.message}</p>`;
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Synthesize';
    }
});

resetBtn.addEventListener('click', () => {
    textInput.value = '';
    resultsContainer.innerHTML = '';
});

function renderSynthesisResults(results) {
    resultsContainer.innerHTML = '';

    // 1. Render Foundational Assumptions
    if (results.foundational_assumptions && results.foundational_assumptions.length > 0) {
        const assumptionsContainer = createAssumptionsSection(results.foundational_assumptions);
        resultsContainer.appendChild(assumptionsContainer);
    }

    // 2. Render the main Synthesized Text
    const synthesizedTextContainer = createSynthesizedTextSection(results.synthesized_text);
    resultsContainer.appendChild(synthesizedTextContainer);

    // 3. Render Omissions
    if (results.omissions && results.omissions.length > 0) {
        const omissionsContainer = createOmissionsSection(results.omissions);
        resultsContainer.appendChild(omissionsContainer);
    }
}

function createAssumptionsSection(assumptions) {
    const container = document.createElement('div');
    container.className = 'mb-8';

    const title = document.createElement('h2');
    title.className = 'text-2xl font-bold mb-4 text-gray-100 border-b-2 border-gray-700 pb-2';
    title.textContent = 'Foundational Assumptions';

    const content = document.createElement('div');
    content.className = 'bg-gray-900 p-4 rounded-md border border-gray-700';

    const description = document.createElement('p');
    description.className = 'text-gray-400 mb-3';
    description.textContent = 'The author appears to take these core beliefs for granted:';
    content.appendChild(description);

    assumptions.forEach(assumption => {
        const assumptionDiv = document.createElement('div');
        assumptionDiv.className = 'bg-gray-800 p-3 rounded-md border border-gray-600 mb-2';

        const assumptionText = document.createElement('p');
        assumptionText.className = 'text-lg text-orange-400';
        assumptionText.textContent = `• ${assumption}`;
        assumptionDiv.appendChild(assumptionText);

        content.appendChild(assumptionDiv);
    });

    container.appendChild(title);
    container.appendChild(content);
    return container;
}

function createSynthesizedTextSection(synthesizedText) {
    const container = document.createElement('div');

    const title = document.createElement('h2');
    title.className = 'text-2xl font-bold mb-4 text-gray-100 border-b-2 border-gray-700 pb-2';
    title.textContent = 'Synthesized Text Analysis';

    const mainContent = document.createElement('div');
    mainContent.className = 'bg-gray-900 p-4 rounded-md border border-gray-700 text-base leading-relaxed';

    synthesizedText.forEach(item => {
        const sentenceElement = createSentenceElement(item);
        mainContent.appendChild(sentenceElement);
    });

    container.appendChild(title);
    container.appendChild(mainContent);
    return container;
}

function createSentenceElement(item) {
    const sentenceSpan = document.createElement('span');
    sentenceSpan.className = 'tooltip';

    // Apply bias heatmap
    const score = item.bias_score;
    let backgroundColor = 'transparent';
    if (score > 0.1) {
        backgroundColor = `rgba(239, 68, 68, ${0.1 + score * 0.6})`;
    } else if (score < -0.1) {
        backgroundColor = `rgba(59, 130, 246, ${0.1 + Math.abs(score) * 0.6})`;
    }
    sentenceSpan.style.backgroundColor = backgroundColor;

    // Apply tactical highlights
    let innerHTML = item.sentence;
    if (item.tactics && item.tactics.length > 0) {
        // Sort by phrase length (descending) to avoid substring replacement issues
        item.tactics.sort((a, b) => b.phrase.length - a.phrase.length).forEach(tactic => {
            const escapedPhrase = escapeRegExp(tactic.phrase);
            const regex = new RegExp(escapedPhrase, 'gi');
            const tacticClass = `tactic-${tactic.tactic.toLowerCase().replace(' ', '_')}`;
            innerHTML = innerHTML.replace(regex, match =>
                `<span class="tactic-highlight ${tacticClass}">${match}</span>`
            );
        });
    }
    sentenceSpan.innerHTML = innerHTML + ' ';

    // Create comprehensive tooltip
    const tooltip = createTooltip(item);
    sentenceSpan.appendChild(tooltip);

    return sentenceSpan;
}

function createTooltip(item) {
    const tooltipText = document.createElement('span');
    tooltipText.className = 'tooltiptext';

    // Bias score section
    const biasSection = document.createElement('div');
    biasSection.className = 'mb-2';
    biasSection.innerHTML = `<strong class="text-yellow-400">Bias Score: ${item.bias_score.toFixed(2)}</strong><br><span class="text-gray-400">${item.justification}</span>`;
    tooltipText.appendChild(biasSection);

    // Tactics section
    if (item.tactics && item.tactics.length > 0) {
        const hr = document.createElement('hr');
        hr.className = 'border-gray-600 my-2';
        tooltipText.appendChild(hr);

        const tacticsTitle = document.createElement('div');
        tacticsTitle.innerHTML = '<strong class="text-yellow-400">Tactics Detected:</strong>';
        tooltipText.appendChild(tacticsTitle);

        item.tactics.forEach(tactic => {
            const tacticDiv = document.createElement('div');
            tacticDiv.className = 'mt-1';
            tacticDiv.innerHTML = `<strong class="font-semibold">${tactic.phrase}</strong>: (${tactic.type}) ${tactic.explanation}`;
            tooltipText.appendChild(tacticDiv);
        });
    }

    return tooltipText;
}

function createOmissionsSection(omissions) {
    const container = document.createElement('div');
    container.className = 'mt-8';

    const title = document.createElement('h2');
    title.className = 'text-2xl font-bold mb-4 text-gray-100 border-b-2 border-gray-700 pb-2';
    title.textContent = 'Omission Analysis';

    container.appendChild(title);

    omissions.forEach(item => {
        const omissionDiv = document.createElement('div');
        omissionDiv.className = 'bg-gray-800 p-4 rounded-md border border-gray-700 mb-3';

        const perspective = document.createElement('p');
        perspective.className = 'text-lg font-semibold text-purple-400';
        perspective.textContent = `Missing Perspective: ${item.omitted_perspective}`;

        const impact = document.createElement('p');
        impact.className = 'text-gray-300 mt-1';
        impact.innerHTML = `<span class="font-medium">Potential Impact:</span> ${item.potential_impact}`;

        omissionDiv.appendChild(perspective);
        omissionDiv.appendChild(impact);
        container.appendChild(omissionDiv);
    });

    return container;
}

function escapeRegExp(string) {
    return string.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
}
