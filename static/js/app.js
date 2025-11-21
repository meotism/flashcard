const API_URL = 'http://localhost:5000/api';
let currentFlashcard = null;
let currentFillBlank = null;

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
            alert('Word added successfully!');
            document.getElementById('add-word-form').reset();
            loadVocabulary();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to add word');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to add word');
    }
});

// Load vocabulary list
async function loadVocabulary() {
    const status = document.getElementById('status-filter').value;
    
    try {
        const response = await fetch(`${API_URL}/vocabulary?status=${status}`);
        const words = await response.json();
        
        const listContainer = document.getElementById('vocabulary-list');
        
        if (words.length === 0) {
            listContainer.innerHTML = '<p class="instruction">No words found. Add some vocabulary!</p>';
            return;
        }
        
        listContainer.innerHTML = words.map(word => `
            <div class="vocab-item">
                <div class="vocab-header">
                    <span class="vocab-word">${word.word}</span>
                    <span class="vocab-status status-${word.status}">${word.status}</span>
                </div>
                <div class="vocab-definition"><strong>Definition:</strong> ${word.definition}</div>
                ${word.example ? `<div class="vocab-example"><strong>Example:</strong> ${word.example}</div>` : ''}
                ${word.translation ? `<div class="vocab-translation"><strong>Translation:</strong> ${word.translation}</div>` : ''}
                <div style="font-size: 0.85rem; color: #999; margin-top: 0.5rem;">
                    Practiced: ${word.times_practiced} times
                </div>
                <div class="vocab-actions">
                    ${word.status === 'learning' ? 
                        `<button onclick="markAsLearned(${word.id})" class="btn btn-success">Mark as Learned</button>` :
                        `<button onclick="markAsLearning(${word.id})" class="btn btn-secondary">Mark as Learning</button>`
                    }
                    <button onclick="deleteWord(${word.id})" class="btn btn-danger">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

// Mark word as learned
async function markAsLearned(id) {
    try {
        await fetch(`${API_URL}/vocabulary/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'learned' })
        });
        loadVocabulary();
    } catch (error) {
        console.error('Error:', error);
    }
}

// Mark word as learning
async function markAsLearning(id) {
    try {
        await fetch(`${API_URL}/vocabulary/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'learning' })
        });
        loadVocabulary();
    } catch (error) {
        console.error('Error:', error);
    }
}

// Delete word
async function deleteWord(id) {
    if (!confirm('Are you sure you want to delete this word?')) {
        return;
    }
    
    try {
        await fetch(`${API_URL}/vocabulary/${id}`, {
            method: 'DELETE'
        });
        loadVocabulary();
    } catch (error) {
        console.error('Error:', error);
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
        
        // Update content
        document.getElementById('flashcard-word').textContent = currentFlashcard.word;
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

// ==================== INITIALIZATION ====================

// Load vocabulary on page load
document.addEventListener('DOMContentLoaded', () => {
    loadVocabulary();
});
