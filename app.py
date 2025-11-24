from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from models import db, Vocabulary, LearningHistory
from cambridge_api import fetch_pronunciation_data
from offline_pronunciation import fetch_offline_pronunciation
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random
import os

app = Flask(__name__, instance_relative_config=True)

# Ensure instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'vocabulary.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Feature flags - Set DISABLE_PRONUNCIATION_FETCH=1 to skip external API calls
DISABLE_PRONUNCIATION_FETCH = os.environ.get('DISABLE_PRONUNCIATION_FETCH', '0') == '1'
if DISABLE_PRONUNCIATION_FETCH:
    print("⚠ Pronunciation fetching is DISABLED (server mode)")

# CORS configuration for production
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

db.init_app(app)

# Initialize database
with app.app_context():
    db.create_all()

# ==================== VOCABULARY MANAGEMENT ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vocabulary', methods=['GET'])
def get_vocabulary():
    """Get all vocabulary words with optional filtering, search, and pagination"""
    status = request.args.get('status')  # learning, learned, or all
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Vocabulary.query
    
    # Filter by status
    if status and status != 'all':
        query = query.filter_by(status=status)
    
    # Search by word, definition, or translation
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Vocabulary.word.ilike(search_pattern),
                Vocabulary.definition.ilike(search_pattern),
                Vocabulary.translation.ilike(search_pattern),
                Vocabulary.example.ilike(search_pattern)
            )
        )
    
    # Paginate results
    pagination = query.order_by(Vocabulary.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'words': [word.to_dict() for word in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })

@app.route('/api/vocabulary/latest', methods=['GET'])
def get_latest_update():
    """Get timestamp of the most recent vocabulary change"""
    latest_word = Vocabulary.query.order_by(Vocabulary.created_at.desc()).first()
    
    if latest_word:
        return jsonify({
            'latest_timestamp': latest_word.created_at.isoformat(),
            'total_count': Vocabulary.query.count()
        })
    
    return jsonify({
        'latest_timestamp': None,
        'total_count': 0
    })

@app.route('/api/vocabulary', methods=['POST'])
def add_vocabulary():
    """Add a new vocabulary word"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('word') or not data.get('definition'):
            return jsonify({'error': 'Word and definition are required'}), 400
        
        # Check if word already exists
        existing = Vocabulary.query.filter_by(word=data['word'].lower()).first()
        if existing:
            return jsonify({'error': 'Word already exists'}), 409
        
        # Fetch pronunciation data (try offline first, then Cambridge if available)
        word_text = data['word'].strip()
        pronunciation_data = {'ipa_us': None, 'ipa_uk': None, 'audio_us': None, 'audio_uk': None}
        
        # Try offline pronunciation first (always works, no internet needed for IPA)
        try:
            print(f"Fetching offline pronunciation for: {word_text}")
            offline_data = fetch_offline_pronunciation(word_text)
            if offline_data and any(offline_data.values()):
                pronunciation_data = offline_data
                print(f"✓ Offline pronunciation: IPA={pronunciation_data.get('ipa_us')}")
        except Exception as e:
            print(f"⚠ Offline pronunciation failed: {str(e)}")
        
        # Optionally try Cambridge Dictionary if online (better audio quality)
        if not DISABLE_PRONUNCIATION_FETCH and not pronunciation_data.get('audio_us'):
            try:
                print(f"Trying Cambridge Dictionary for: {word_text}")
                cambridge_data = fetch_pronunciation_data(word_text, skip_fetch=False)
                if cambridge_data:
                    # Use Cambridge audio if available (better quality)
                    if cambridge_data.get('audio_us'):
                        pronunciation_data['audio_us'] = cambridge_data['audio_us']
                    if cambridge_data.get('audio_uk'):
                        pronunciation_data['audio_uk'] = cambridge_data['audio_uk']
                    # Use Cambridge IPA if offline didn't work
                    if cambridge_data.get('ipa_us') and not pronunciation_data.get('ipa_us'):
                        pronunciation_data['ipa_us'] = cambridge_data['ipa_us']
                    if cambridge_data.get('ipa_uk') and not pronunciation_data.get('ipa_uk'):
                        pronunciation_data['ipa_uk'] = cambridge_data['ipa_uk']
            except Exception as e:
                print(f"⚠ Cambridge Dictionary failed: {str(e)}")
        
        new_word = Vocabulary(
            word=word_text.lower(),
            definition=data['definition'],
            example=data.get('example', ''),
            translation=data.get('translation', ''),
            ipa_us=pronunciation_data.get('ipa_us'),
            ipa_uk=pronunciation_data.get('ipa_uk'),
            audio_us=pronunciation_data.get('audio_us'),
            audio_uk=pronunciation_data.get('audio_uk'),
            status='learning'
        )
        
        db.session.add(new_word)
        db.session.commit()
        
        return jsonify(new_word.to_dict()), 201
    
    except Exception as e:
        print(f"Error adding vocabulary: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Failed to add word: {str(e)}'}), 500

@app.route('/api/vocabulary/<int:id>', methods=['PUT'])
def update_vocabulary(id):
    """Update a vocabulary word"""
    word = Vocabulary.query.get_or_404(id)
    data = request.json
    
    if 'word' in data:
        word.word = data['word'].lower()
    if 'definition' in data:
        word.definition = data['definition']
    if 'example' in data:
        word.example = data['example']
    if 'translation' in data:
        word.translation = data['translation']
    if 'status' in data:
        word.status = data['status']
        if data['status'] == 'learned' and not word.learned_at:
            word.learned_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(word.to_dict())

@app.route('/api/vocabulary/<int:id>', methods=['DELETE'])
def delete_vocabulary(id):
    """Delete a vocabulary word"""
    try:
        word = Vocabulary.query.get_or_404(id)
        word_id = word.id
        print(f"[DELETE] Deleting word ID: {word_id} - {word.word}")
        
        # Delete related learning history records first (if cascade doesn't work)
        from models import LearningHistory
        LearningHistory.query.filter_by(vocabulary_id=word_id).delete()
        
        # Delete the vocabulary word
        db.session.delete(word)
        db.session.commit()
        
        print(f"[DELETE] Successfully deleted word ID: {word_id}")
        return jsonify({'message': 'Word deleted successfully', 'id': word_id}), 200
    except Exception as e:
        print(f"[DELETE] Error deleting word ID {id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== GAME: FLASHCARD ====================

@app.route('/api/games/flashcard/random', methods=['GET'])
def get_random_flashcard():
    """Get a random word for flashcard practice"""
    status = request.args.get('status', 'learning')
    
    query = Vocabulary.query
    if status != 'all':
        query = query.filter_by(status=status)
    
    words = query.all()
    if not words:
        return jsonify({'error': 'No words available'}), 404
    
    word = random.choice(words)
    return jsonify(word.to_dict())

@app.route('/api/games/flashcard/practice', methods=['POST'])
def practice_flashcard():
    """Record flashcard practice"""
    data = request.json
    vocabulary_id = data.get('vocabulary_id')
    correct = data.get('correct', True)
    
    word = Vocabulary.query.get_or_404(vocabulary_id)
    word.times_practiced += 1
    
    history = LearningHistory(
        vocabulary_id=vocabulary_id,
        activity_type='flashcard',
        correct=correct
    )
    
    db.session.add(history)
    db.session.commit()
    
    return jsonify({'message': 'Practice recorded', 'times_practiced': word.times_practiced})

# ==================== GAME: FILL IN THE BLANK ====================

@app.route('/api/games/fill-blank/question', methods=['GET'])
def get_fill_blank_question():
    """Generate a fill-in-the-blank question"""
    status = request.args.get('status', 'learning')
    
    query = Vocabulary.query.filter(Vocabulary.example.isnot(None), Vocabulary.example != '')
    if status != 'all':
        query = query.filter_by(status=status)
    
    words = query.all()
    if not words:
        return jsonify({'error': 'No words with examples available'}), 404
    
    word = random.choice(words)
    
    # Create blank in the example sentence
    example = word.example
    word_to_blank = word.word
    
    # Replace the word with a blank (case insensitive)
    import re
    blanked_sentence = re.sub(
        r'\b' + re.escape(word_to_blank) + r'\b',
        '_____',
        example,
        flags=re.IGNORECASE
    )
    
    # If word wasn't found, use the whole example
    if blanked_sentence == example:
        blanked_sentence = '_____ : ' + word.definition
    
    return jsonify({
        'id': word.id,
        'question': blanked_sentence,
        'hint': word.definition,
        'word': word.word
    })

@app.route('/api/games/fill-blank/check', methods=['POST'])
def check_fill_blank_answer():
    """Check fill-in-the-blank answer"""
    data = request.json
    vocabulary_id = data.get('vocabulary_id')
    user_answer = data.get('answer', '').strip().lower()
    
    word = Vocabulary.query.get_or_404(vocabulary_id)
    correct = user_answer == word.word.lower()
    
    word.times_practiced += 1
    
    history = LearningHistory(
        vocabulary_id=vocabulary_id,
        activity_type='fill_blank',
        correct=correct
    )
    
    db.session.add(history)
    db.session.commit()
    
    return jsonify({
        'correct': correct,
        'correct_answer': word.word,
        'times_practiced': word.times_practiced
    })

# ==================== STATISTICS ====================

@app.route('/api/stats/summary', methods=['GET'])
def get_stats_summary():
    """Get learning statistics summary"""
    # Total words
    total_words = Vocabulary.query.count()
    learning_words = Vocabulary.query.filter_by(status='learning').count()
    learned_words = Vocabulary.query.filter_by(status='learned').count()
    
    # This month stats
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    words_added_this_month = Vocabulary.query.filter(
        Vocabulary.created_at >= month_start
    ).count()
    
    words_learned_this_month = Vocabulary.query.filter(
        Vocabulary.learned_at >= month_start
    ).count()
    
    # Practice stats this month
    practices_this_month = LearningHistory.query.filter(
        LearningHistory.practiced_at >= month_start
    ).count()
    
    return jsonify({
        'total_words': total_words,
        'learning_words': learning_words,
        'learned_words': learned_words,
        'words_added_this_month': words_added_this_month,
        'words_learned_this_month': words_learned_this_month,
        'practices_this_month': practices_this_month
    })

@app.route('/api/stats/monthly', methods=['GET'])
def get_monthly_stats():
    """Get monthly statistics for the past 6 months"""
    stats = []
    now = datetime.utcnow()
    
    for i in range(6):
        # Calculate month start and end
        month_date = now - relativedelta(months=i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = month_start + relativedelta(months=1)
        
        # Count words added in this month
        words_added = Vocabulary.query.filter(
            Vocabulary.created_at >= month_start,
            Vocabulary.created_at < next_month
        ).count()
        
        # Count words learned in this month
        words_learned = Vocabulary.query.filter(
            Vocabulary.learned_at >= month_start,
            Vocabulary.learned_at < next_month
        ).count()
        
        # Count practices in this month
        practices = LearningHistory.query.filter(
            LearningHistory.practiced_at >= month_start,
            LearningHistory.practiced_at < next_month
        ).count()
        
        stats.append({
            'month': month_start.strftime('%Y-%m'),
            'month_name': month_start.strftime('%B %Y'),
            'words_added': words_added,
            'words_learned': words_learned,
            'practices': practices
        })
    
    return jsonify(stats)

# ==================== PRONUNCIATION API ====================

@app.route('/api/vocabulary/<int:id>/fetch-pronunciation', methods=['POST'])
def fetch_word_pronunciation(id):
    """Fetch and update pronunciation data for an existing word"""
    word = Vocabulary.query.get_or_404(id)
    
    pronunciation_data = fetch_pronunciation_data(word.word)
    
    word.ipa_us = pronunciation_data.get('ipa_us')
    word.ipa_uk = pronunciation_data.get('ipa_uk')
    word.audio_us = pronunciation_data.get('audio_us')
    word.audio_uk = pronunciation_data.get('audio_uk')
    
    db.session.commit()
    
    return jsonify({
        'message': 'Pronunciation data updated',
        'data': {
            'ipa_us': word.ipa_us,
            'ipa_uk': word.ipa_uk,
            'audio_us': word.audio_us,
            'audio_uk': word.audio_uk
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
