let currentLegislation = [];

document.addEventListener('DOMContentLoaded', function() {
    feather.replace();
    loadLegislation();
});

async function loadLegislation() {
    try {
        showLoading(true);
        const data = await PolisAPI.getLegislation();
        currentLegislation = data.legislation;
        renderLegislationCards(currentLegislation);
        showLoading(false);
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to load legislation');
        showLoading(false);
    }
}

function renderLegislationCards(legislation) {
    const container = document.getElementById('legislation-container');
    
    if (!legislation.length) {
        container.innerHTML = '<div class="col-span-2 text-center py-12"><p class="text-gray-600">No legislation available</p></div>';
        return;
    }
    
    container.innerHTML = legislation.map(leg => {
        const supportPercent = ((leg.avg_sentiment + 1) / 2) * 100;
        return `
            <div class="bg-white rounded-xl shadow-md overflow-hidden card-hover">
                <div class="p-6">
                    <h3 class="text-xl font-semibold mb-2">${leg.title}</h3>
                    <p class="text-gray-600 text-sm mb-3">${leg.description}</p>
                    
                    <div class="mb-6">
                        <div class="flex justify-between text-sm text-gray-500 mb-2">
                            <span>Support</span>
                            <span>Oppose</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-3">
                            <div class="bg-gradient-to-r from-green-400 to-blue-500 h-3 rounded-full" style="width: ${supportPercent}%"></div>
                        </div>
                        <div class="text-center text-sm text-gray-600 mt-1">${Math.round(supportPercent)}% Supportive</div>
                    </div>
                    
                    <button onclick="viewLegislationDetail(${leg.id})" class="w-full bg-blue-600 text-white px-4 py-3 rounded-xl font-medium hover:bg-blue-700 transition">
                        View Details & Provide Feedback
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    feather.replace();
}

async function viewLegislationDetail(legId) {
    try {
        const data = await PolisAPI.getLegislationDetail(legId);
        openFeedbackModal(data);
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to load details');
    }
}

function openFeedbackModal(legislationData) {
    const leg = legislationData.legislation;
    document.getElementById('modal-title').textContent = `Feedback: ${leg.title}`;
    
    document.getElementById('modal-content').innerHTML = `
        <div class="space-y-6">
            <div class="bg-gray-50 p-4 rounded-lg">
                <h4 class="font-semibold mb-2">Summary</h4>
                <p class="text-gray-700">${leg.summary}</p>
            </div>
            
            <form onsubmit="submitFeedback(event)" class="space-y-4">
                <input type="hidden" name="legislation_id" value="${leg.id}">
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Your Stance</label>
                    <div class="flex items-center space-x-4">
                        <span class="text-red-600">Oppose</span>
                        <input type="range" name="sentiment_score" min="-1" max="1" step="0.1" value="0" class="w-full" oninput="updateSentimentDisplay(this.value)">
                        <span class="text-green-600">Support</span>
                    </div>
                    <div id="sentiment-display" class="text-center text-sm text-gray-600 mt-2">Neutral</div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Tags</label>
                    <div class="grid grid-cols-2 gap-2">
                        <label class="flex items-center"><input type="checkbox" name="tags" value="#EnvironmentalImpact" class="mr-2"> Environmental Impact</label>
                        <label class="flex items-center"><input type="checkbox" name="tags" value="#CostConcern" class="mr-2"> Cost Concern</label>
                    </div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Comments</label>
                    <textarea name="comment" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md" placeholder="Share your thoughts..."></textarea>
                </div>
                
                <div class="flex space-x-3 pt-4">
                    <button type="button" onclick="closeModal()" class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">Cancel</button>
                    <button type="submit" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Submit Feedback</button>
                </div>
            </form>
        </div>
    `;
    
    document.getElementById('feedback-modal').classList.remove('hidden');
}

async function submitFeedback(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    const feedbackData = {
        legislation_id: parseInt(formData.get('legislation_id')),
        sentiment_score: parseFloat(formData.get('sentiment_score')),
        tags: Array.from(event.target.querySelectorAll('input[name="tags"]:checked')).map(cb => cb.value),
        comment: formData.get('comment')
    };
    
    try {
        await PolisAPI.submitFeedback(feedbackData);
        showSuccess('Feedback submitted!');
        closeModal();
        await loadLegislation();
    } catch (error) {
        showError('Failed to submit feedback');
    }
}

function updateSentimentDisplay(value) {
    const display = document.getElementById('sentiment-display');
    const numValue = parseFloat(value);
    if (numValue > 0.3) display.textContent = `Strongly Support (${numValue.toFixed(1)})`;
    else if (numValue > 0) display.textContent = `Support (${numValue.toFixed(1)})`;
    else if (numValue < -0.3) display.textContent = `Strongly Oppose (${numValue.toFixed(1)})`;
    else if (numValue < 0) display.textContent = `Oppose (${numValue.toFixed(1)})`;
    else display.textContent = 'Neutral (0.0)';
}

function closeModal() {
    document.getElementById('feedback-modal').classList.add('hidden');
}

function scrollToSection(sectionId) {
    document.getElementById(sectionId).scrollIntoView({behavior: 'smooth'});
}

function showLoading(show) {
    document.getElementById('loading-spinner').style.display = show ? 'flex' : 'none';
}

function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    alert('Success: ' + message);
}

// Global functions
window.viewLegislationDetail = viewLegislationDetail;
window.closeModal = closeModal;
window.submitFeedback = submitFeedback;
window.scrollToSection = scrollToSection;