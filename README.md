# English Learning Application

A comprehensive Flask-based English learning application with vocabulary management and interactive games.

## Features

### 📚 Vocabulary Management
- Add new words with definitions, examples, and translations
- Track words as "Learning" or "Learned"
- View and filter your vocabulary list
- Delete or update word status

### 🎮 Interactive Games

#### Flashcard Game
- Practice vocabulary with interactive flashcards
- Flip cards to see definitions, examples, and translations
- Mark words based on your confidence level
- Filter by word status (learning/learned/all)

#### Fill in the Blank
- Test your knowledge with fill-in-the-blank exercises
- Get hints from word definitions
- Instant feedback on your answers
- Automatic progression to next question

### 📊 Learning Statistics
- Track total vocabulary count
- Monitor learning vs. learned words
- View monthly progress:
  - Words added this month
  - Words learned this month
  - Practice sessions completed
- 6-month historical data

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Steps

1. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```powershell
   python app.py
   ```

3. **Access the Application**
   - Open your browser and navigate to: `http://localhost:5000`
   - The database will be created automatically on first run

## Project Structure

```
flashcard/
├── app.py                 # Main Flask application with API endpoints
├── models.py              # SQLAlchemy database models
├── requirements.txt       # Python dependencies
├── vocabulary.db          # SQLite database (created automatically)
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Application styling
    └── js/
        └── app.js        # Frontend JavaScript logic
```

## Usage Guide

### Adding Vocabulary
1. Navigate to the "Vocabulary" tab
2. Fill in the word form:
   - **Word**: The English word (required)
   - **Definition**: Clear definition (required)
   - **Example**: Sentence using the word (optional, needed for Fill the Blank game)
   - **Translation**: Translation to your native language (optional)
3. Click "Add Word"

### Playing Flashcard Game
1. Go to the "Flashcard" tab
2. Select which words to practice (Learning/Learned/All)
3. Click "Start/Next" to begin
4. Click the card to flip and see the definition
5. Rate yourself:
   - "Need Practice" - if you're still learning
   - "Got It!" - if you know it well

### Playing Fill in the Blank
1. Go to the "Fill the Blank" tab
2. Select word difficulty level
3. Click "Start/Next"
4. Read the sentence and type the missing word
5. Press Enter or click "Check Answer"
6. New question loads automatically after 2 seconds

### Viewing Statistics
1. Navigate to the "Statistics" tab
2. View your overall progress:
   - Total words in your vocabulary
   - Words currently learning vs. learned
   - This month's achievements
3. Scroll down for monthly historical data (past 6 months)

## API Endpoints

### Vocabulary Management
- `GET /api/vocabulary` - Get all vocabulary (optional: ?status=learning|learned|all)
- `POST /api/vocabulary` - Add new word
- `PUT /api/vocabulary/<id>` - Update word
- `DELETE /api/vocabulary/<id>` - Delete word

### Flashcard Game
- `GET /api/games/flashcard/random` - Get random flashcard (optional: ?status=learning|learned|all)
- `POST /api/games/flashcard/practice` - Record practice session

### Fill in the Blank Game
- `GET /api/games/fill-blank/question` - Get new question (optional: ?status=learning|learned|all)
- `POST /api/games/fill-blank/check` - Check answer

### Statistics
- `GET /api/stats/summary` - Get overall statistics
- `GET /api/stats/monthly` - Get 6-month historical data

## Database Schema

### Vocabulary Table
- `id`: Primary key
- `word`: Vocabulary word (unique)
- `definition`: Word definition
- `example`: Example sentence
- `translation`: Native language translation
- `status`: learning/learned
- `created_at`: When word was added
- `learned_at`: When marked as learned
- `times_practiced`: Practice count

### LearningHistory Table
- `id`: Primary key
- `vocabulary_id`: Foreign key to Vocabulary
- `activity_type`: flashcard/fill_blank/review
- `correct`: Boolean for correctness
- `practiced_at`: Timestamp

## Tips for Best Results

1. **Add Example Sentences**: Required for Fill in the Blank game
2. **Regular Practice**: Use both games to reinforce learning
3. **Mark Progress**: Update word status as you learn
4. **Review Statistics**: Track your monthly progress to stay motivated
5. **Mix Difficulty**: Practice both learning and learned words

## Troubleshooting

**Application won't start:**
- Ensure Python 3.7+ is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`

**Database errors:**
- Delete `vocabulary.db` and restart the app
- Database will be recreated automatically

**Port already in use:**
- Change port in `app.py`: `app.run(debug=True, port=5001)`

**Browser can't connect:**
- Make sure Flask is running
- Check firewall settings
- Try `http://127.0.0.1:5000` instead

## License

This project is open source and available for educational purposes.

## Future Enhancements

Potential features to add:
- Multiple choice quiz game
- Spaced repetition algorithm
- Audio pronunciation
- Word categories/tags
- Export/import vocabulary
- User accounts and authentication
- Mobile responsive improvements
- Dark mode

Enjoy learning English! 🎓
