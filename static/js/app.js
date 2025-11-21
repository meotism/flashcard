const API_URL = 'http://localhost:5000/api';
let currentFlashcard = null;
let currentFillBlank = null;
let socket = null;

// ==================== UTILITY FUNCTIONS ====================

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// ==================== NAVIGATION ====================

function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(`${sectionName}-section`).classList.add('active');
    
    // Load data for the section
    if (sectionName === 'vocabulary') {
        loadVocabulary();
    } else if (sectionName === 'statistics') {
        loadStatistics();
    }
}

// ==================== VOCABULARY MANAGEMENT ====================

// Add new word
document.getElementById('add-word-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        word: document.getElementById('word').value,
        definition: document.getElementById('definition').value,
        example: document.getElementById('example').value,
        translation: document.getElementById('translation').value
    };
    
    try {
        const response = await fetch(`${API_URL}/vocabulary`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showNotification('Word added successfully!', 'success');
            document.getElementById('add-word-form').reset();
            loadVocabulary();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to add word', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to add word: ' + error.message, 'error');
    }
});

// Pagination state
let currentPage = 1;
const perPage = 20;
let searchTimeout = null;

// Handle search with debounce
function handleSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        currentPage = 1; // Reset to first page on new search
        loadVocabulary();
    }, 500); // Wait 500ms after user stops typing
}

// Load vocabulary list
async function loadVocabulary(page = 1) {
    const status = document.getElementById('status-filter').value;
    const search = document.getElementById('search-input').value;
    currentPage = page;
    
    try {
        let url = `${API_URL}/vocabulary?status=${status}&page=${page}&per_page=${perPage}`;
        if (search) {
            url += `&search=${encodeURIComponent(search)}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        const listContainer = document.getElementById('vocabulary-list');
        
        if (data.words.length === 0) {
            const searchValue = document.getElementById('search-input').value;
            if (searchValue) {
                listContainer.innerHTML = `<p class="instruction">No words found matching "${searchValue}"</p>`;
            } else {
                listContainer.innerHTML = '<p class="instruction">No words found. Add some vocabulary!</p>';
            }
            return;
        }
        
        listContainer.innerHTML = data.words.map(word => `
            <div class="vocab-item">
                <div class="vocab-header">
                    <span class="vocab-word">${word.word || ''}</span>
                    <span class="vocab-status status-${word.status || 'learning'}">${word.status || 'learning'}</span>
                </div>
                ${word.ipa_uk || word.ipa_us ? `
                    <div class="vocab-pronunciation">
                        ${word.ipa_uk ? `
                            <span class="pronunciation-item">
                                <span class="pronunciation-label">UK:</span>
                                <span class="ipa-text">/${word.ipa_uk}/</span>
                                ${word.audio_uk ? `<button class="btn-audio" onclick="playAudio('${word.audio_uk}', event)">🔊</button>` : ''}
                            </span>
                        ` : ''}
                        ${word.ipa_us ? `
                            <span class="pronunciation-item">
                                <span class="pronunciation-label">US:</span>
                                <span class="ipa-text">/${word.ipa_us}/</span>
                                ${word.audio_us ? `<button class="btn-audio" onclick="playAudio('${word.audio_us}', event)">🔊</button>` : ''}
                            </span>
                        ` : ''}
                    </div>
                ` : ''}
                <div class="vocab-definition"><strong>Definition:</strong> ${word.definition || ''}</div>
                ${word.example ? `<div class="vocab-example"><strong>Example:</strong> ${word.example}</div>` : ''}
                ${word.translation ? `<div class="vocab-translation"><strong>Translation:</strong> ${word.translation}</div>` : ''}
                <div style="font-size: 0.85rem; color: #999; margin-top: 0.5rem;">
                    Practiced: ${word.times_practiced || 0} times
                </div>
                <div class="vocab-actions">
                    ${word.status === 'learning' ? 
                        `<button onclick="markAsLearned(${word.id}); return false;" class="btn btn-success">Mark as Learned</button>` :
                        `<button onclick="markAsLearning(${word.id}); return false;" class="btn btn-secondary">Mark as Learning</button>`
                    }
                    <button onclick="deleteWord(${word.id}); return false;" class="btn btn-danger">Delete</button>
                </div>
            </div>
        `).join('');
        
        // Add pagination controls
        if (data.pages > 1) {
            listContainer.innerHTML += `
                <div class="pagination">
                    <button onclick="loadVocabulary(${page - 1})" class="btn btn-secondary" ${!data.has_prev ? 'disabled' : ''}>
                        ← Previous
                    </button>
                    <span class="pagination-info">
                        Page ${data.current_page} of ${data.pages} (${data.total} words)
                    </span>
                    <button onclick="loadVocabulary(${page + 1})" class="btn btn-secondary" ${!data.has_next ? 'disabled' : ''}>
                        Next →
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Mark word as learned
async function markAsLearned(id) {
    try {
        const response = await fetch(`${API_URL}/vocabulary/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'learned' })
        });
        
        if (response.ok) {
            showNotification('Word marked as learned!', 'success');
            loadVocabulary(currentPage);
        } else {
            showNotification('Failed to update word status', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to update word: ' + error.message, 'error');
    }
}

// Mark word as learning
async function markAsLearning(id) {
    try {
        const response = await fetch(`${API_URL}/vocabulary/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'learning' })
        });
        
        if (response.ok) {
            showNotification('Word marked as learning', 'info');
            loadVocabulary(currentPage);
        } else {
            showNotification('Failed to update word status', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to update word: ' + error.message, 'error');
    }
}

// Delete word
async function deleteWord(id) {
    if (!confirm('Are you sure you want to delete this word?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/vocabulary/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Word deleted successfully', 'success');
            loadVocabulary(currentPage);
        } else {
            showNotification('Failed to delete word', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to delete word: ' + error.message, 'error');
    }
}

// ==================== FLASHCARD GAME ====================

async function loadFlashcard() {
    const status = document.getElementById('flashcard-filter').value;
    
    try {
        const response = await fetch(`${API_URL}/games/flashcard/random?status=${status}`);
        
        if (!response.ok) {
            alert('No words available for practice!');
            return;
        }
        
        currentFlashcard = await response.json();
        
        // Reset card to front
        document.getElementById('flashcard').classList.remove('flipped');
        
        // Update content - front side
        let frontContent = `<h3 id="flashcard-word">${currentFlashcard.word}</h3>`;
        if (currentFlashcard.ipa_uk || currentFlashcard.ipa_us) {
            frontContent += '<div class="flashcard-pronunciation">';
            if (currentFlashcard.ipa_uk) {
                frontContent += `
                    <div class="pronunciation-item">
                        <span class="pronunciation-label">UK:</span>
                        <span class="ipa-text">/${currentFlashcard.ipa_uk}/</span>
                        ${currentFlashcard.audio_uk ? `<button class="btn-audio-small" onclick="playAudio('${currentFlashcard.audio_uk}', event)">🔊</button>` : ''}
                    </div>
                `;
            }
            if (currentFlashcard.ipa_us) {
                frontContent += `
                    <div class="pronunciation-item">
                        <span class="pronunciation-label">US:</span>
                        <span class="ipa-text">/${currentFlashcard.ipa_us}/</span>
                        ${currentFlashcard.audio_us ? `<button class="btn-audio-small" onclick="playAudio('${currentFlashcard.audio_us}', event)">🔊</button>` : ''}
                    </div>
                `;
            }
            frontContent += '</div>';
        }
        frontContent += '<p class="hint">Click to flip</p>';
        
        document.querySelector('.flashcard-front').innerHTML = frontContent;
        
        // Update content - back side
        document.getElementById('flashcard-definition').innerHTML = 
            `<strong>Definition:</strong><br>${currentFlashcard.definition}`;
        document.getElementById('flashcard-example').innerHTML = 
            currentFlashcard.example ? `<br><strong>Example:</strong><br>${currentFlashcard.example}` : '';
        document.getElementById('flashcard-translation').innerHTML = 
            currentFlashcard.translation ? `<br><strong>Translation:</strong><br>${currentFlashcard.translation}` : '';
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load flashcard');
    }
}

function flipCard() {
    if (currentFlashcard) {
        document.getElementById('flashcard').classList.toggle('flipped');
    }
}

async function markFlashcard(correct) {
    if (!currentFlashcard) {
        alert('Please load a flashcard first!');
        return;
    }
    
    try {
        await fetch(`${API_URL}/games/flashcard/practice`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vocabulary_id: currentFlashcard.id,
                correct: correct
            })
        });
        
        // Load next card
        loadFlashcard();
    } catch (error) {
        console.error('Error:', error);
    }
}

// ==================== FILL IN THE BLANK GAME ====================

async function loadFillBlank() {
    const status = document.getElementById('fill-blank-filter').value;
    
    try {
        const response = await fetch(`${API_URL}/games/fill-blank/question?status=${status}`);
        
        if (!response.ok) {
            alert('No words with examples available for practice!');
            return;
        }
        
        currentFillBlank = await response.json();
        
        const gameContainer = document.getElementById('fill-blank-game');
        gameContainer.innerHTML = `
            <div class="fill-blank-question">
                <strong>Fill in the blank:</strong><br><br>
                ${currentFillBlank.question}
            </div>
            <div class="fill-blank-hint">
                <strong>Hint:</strong> ${currentFillBlank.hint}
            </div>
            <input type="text" id="fill-blank-answer" class="fill-blank-input" 
                   placeholder="Type your answer here..." onkeypress="if(event.key==='Enter') checkFillBlank()">
            <br>
            <button onclick="checkFillBlank()" class="btn btn-primary">Check Answer</button>
            <div id="fill-blank-result"></div>
        `;
        
        document.getElementById('fill-blank-answer').focus();
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load question');
    }
}

async function checkFillBlank() {
    if (!currentFillBlank) {
        return;
    }
    
    const answer = document.getElementById('fill-blank-answer').value.trim();
    
    if (!answer) {
        alert('Please enter an answer!');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/games/fill-blank/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vocabulary_id: currentFillBlank.id,
                answer: answer
            })
        });
        
        const result = await response.json();
        const resultDiv = document.getElementById('fill-blank-result');
        
        if (result.correct) {
            resultDiv.innerHTML = `
                <div class="fill-blank-result result-correct">
                    ✓ Correct! Great job!
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="fill-blank-result result-incorrect">
                    ✗ Incorrect. The correct answer is: <strong>${result.correct_answer}</strong>
                </div>
            `;
        }
        
        // Auto-load next question after 2 seconds
        setTimeout(() => {
            loadFillBlank();
        }, 2000);
    } catch (error) {
        console.error('Error:', error);
    }
}

// ==================== STATISTICS ====================

async function loadStatistics() {
    try {
        // Load summary stats
        const summaryResponse = await fetch(`${API_URL}/stats/summary`);
        const summary = await summaryResponse.json();
        
        document.getElementById('stat-total').textContent = summary.total_words;
        document.getElementById('stat-learning').textContent = summary.learning_words;
        document.getElementById('stat-learned').textContent = summary.learned_words;
        document.getElementById('stat-month-added').textContent = summary.words_added_this_month;
        document.getElementById('stat-month-learned').textContent = summary.words_learned_this_month;
        document.getElementById('stat-month-practice').textContent = summary.practices_this_month;
        
        // Load monthly stats
        const monthlyResponse = await fetch(`${API_URL}/stats/monthly`);
        const monthly = await monthlyResponse.json();
        
        const monthlyContainer = document.getElementById('monthly-stats');
        monthlyContainer.innerHTML = monthly.map(stat => `
            <div class="month-stat">
                <h4>${stat.month_name}</h4>
                <div class="stat-row">
                    <span class="stat-label">Words Added:</span>
                    <span class="stat-value">${stat.words_added}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Words Learned:</span>
                    <span class="stat-value">${stat.words_learned}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Practice Sessions:</span>
                    <span class="stat-value">${stat.practices}</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

// ==================== AUDIO PLAYBACK ====================

let currentAudio = null;

function playAudio(audioUrl, event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    
    // Stop current audio if playing
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    
    // Play new audio
    currentAudio = new Audio(audioUrl);
    currentAudio.play().catch(error => {
        console.error('Error playing audio:', error);
        alert('Unable to play audio. Please check your connection.');
    });
}

// ==================== WEBSOCKET CONNECTION ====================

function initializeSocket() {
    // Connect to Socket.IO server
    socket = io('http://localhost:5000');
    
    socket.on('connect', () => {
        console.log('✓ Connected to vocabulary server');
    });
    
    socket.on('connected', (data) => {
        console.log(data.message);
    });
    
    socket.on('vocabulary_added', (word) => {
        console.log('New word added:', word);
        
        // Show notification - with safety check
        if (word && word.word) {
            showNotification(`New word added: ${word.word}`, 'success');
        } else {
            showNotification('New word added', 'success');
        }
        
        // Reload vocabulary list if on vocabulary section
        const vocabSection = document.getElementById('vocabulary-section');
        if (vocabSection && vocabSection.classList.contains('active')) {
            loadVocabulary(currentPage);
        }
    });
    
    socket.on('vocabulary_updated', (word) => {
        console.log('Word updated:', word.word);
        
        // Show notification
        showNotification(`Word updated: ${word.word}`, 'info');
        
        // Reload vocabulary list if on vocabulary section
        const vocabSection = document.getElementById('vocabulary-section');
        if (vocabSection && vocabSection.classList.contains('active')) {
            loadVocabulary(currentPage);
        }
    });
    
    socket.on('vocabulary_deleted', (data) => {
        console.log('Word deleted:', data.id);
        
        // Show notification
        showNotification('Word deleted', 'warning');
        
        // Reload vocabulary list if on vocabulary section
        const vocabSection = document.getElementById('vocabulary-section');
        if (vocabSection && vocabSection.classList.contains('active')) {
            loadVocabulary(currentPage);
        }
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });
}

// ==================== INITIALIZATION ====================

// Load vocabulary on page load
document.addEventListener('DOMContentLoaded', () => {
    loadVocabulary();
    initializeSocket();
});
