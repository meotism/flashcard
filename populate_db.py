"""
Populate the database with sample vocabulary words from A1 to B2 levels
Run this script after installing dependencies to add initial vocabulary
"""

from app import app, db
from models import Vocabulary
from datetime import datetime, timedelta
import random

# Sample vocabulary words organized by CEFR levels
vocabulary_data = {
    'A1': [
        {'word': 'hello', 'definition': 'A greeting used when meeting someone', 'example': 'Hello, how are you today?', 'translation': '你好'},
        {'word': 'book', 'definition': 'A set of printed pages bound together', 'example': 'I am reading a book about history.', 'translation': '书'},
        {'word': 'water', 'definition': 'A clear liquid that falls as rain', 'example': 'Can I have a glass of water, please?', 'translation': '水'},
        {'word': 'happy', 'definition': 'Feeling pleasure or contentment', 'example': 'She is happy with her new job.', 'translation': '快乐的'},
        {'word': 'eat', 'definition': 'To put food in your mouth and swallow it', 'example': 'I eat breakfast every morning.', 'translation': '吃'},
        {'word': 'house', 'definition': 'A building where people live', 'example': 'They bought a new house last year.', 'translation': '房子'},
        {'word': 'friend', 'definition': 'A person you like and enjoy being with', 'example': 'My best friend lives next door.', 'translation': '朋友'},
        {'word': 'learn', 'definition': 'To get knowledge or skill', 'example': 'Children learn quickly when they are young.', 'translation': '学习'},
        {'word': 'work', 'definition': 'Activity involving effort to achieve a purpose', 'example': 'I work in an office downtown.', 'translation': '工作'},
        {'word': 'family', 'definition': 'Parents and their children', 'example': 'My family is very important to me.', 'translation': '家庭'},
    ],
    'A2': [
        {'word': 'improve', 'definition': 'To make or become better', 'example': 'I want to improve my English skills.', 'translation': '改善'},
        {'word': 'journey', 'definition': 'An act of traveling from one place to another', 'example': 'The journey to the city takes two hours.', 'translation': '旅程'},
        {'word': 'comfortable', 'definition': 'Giving physical ease and relaxation', 'example': 'This chair is very comfortable to sit in.', 'translation': '舒适的'},
        {'word': 'decision', 'definition': 'A choice that you make about something', 'example': 'Making the right decision is important.', 'translation': '决定'},
        {'word': 'experience', 'definition': 'Knowledge or skill from doing something', 'example': 'She has a lot of experience in teaching.', 'translation': '经验'},
        {'word': 'exercise', 'definition': 'Physical activity to stay healthy', 'example': 'I exercise three times a week at the gym.', 'translation': '锻炼'},
        {'word': 'explore', 'definition': 'To travel around an area to learn about it', 'example': 'We like to explore new cities on vacation.', 'translation': '探索'},
        {'word': 'prepare', 'definition': 'To make ready for something', 'example': 'I need to prepare for my exam tomorrow.', 'translation': '准备'},
        {'word': 'remember', 'definition': 'To keep something in your memory', 'example': 'I always remember my grandmother\'s birthday.', 'translation': '记得'},
        {'word': 'suggest', 'definition': 'To mention an idea for someone to consider', 'example': 'Can you suggest a good restaurant nearby?', 'translation': '建议'},
    ],
    'B1': [
        {'word': 'accomplish', 'definition': 'To succeed in doing something', 'example': 'She accomplished all her goals this year.', 'translation': '完成'},
        {'word': 'advantage', 'definition': 'Something that helps you succeed', 'example': 'Speaking two languages is a great advantage.', 'translation': '优势'},
        {'word': 'approach', 'definition': 'A way of dealing with something', 'example': 'We need a different approach to solve this problem.', 'translation': '方法'},
        {'word': 'challenge', 'definition': 'A difficult task that tests ability', 'example': 'Learning a new language is a big challenge.', 'translation': '挑战'},
        {'word': 'contribute', 'definition': 'To give something to help achieve a result', 'example': 'Everyone should contribute to the team project.', 'translation': '贡献'},
        {'word': 'demonstrate', 'definition': 'To show clearly by giving proof', 'example': 'The teacher will demonstrate how to solve the equation.', 'translation': '展示'},
        {'word': 'efficient', 'definition': 'Working well without wasting time or energy', 'example': 'This new system is more efficient than the old one.', 'translation': '高效的'},
        {'word': 'maintain', 'definition': 'To keep something in good condition', 'example': 'It is important to maintain a healthy lifestyle.', 'translation': '维持'},
        {'word': 'perspective', 'definition': 'A particular way of viewing things', 'example': 'Travel gives you a new perspective on life.', 'translation': '观点'},
        {'word': 'significant', 'definition': 'Large or important enough to notice', 'example': 'There was a significant improvement in his grades.', 'translation': '重要的'},
    ],
    'B2': [
        {'word': 'acknowledge', 'definition': 'To accept or admit that something is true', 'example': 'He acknowledged that he made a mistake.', 'translation': '承认'},
        {'word': 'comprehensive', 'definition': 'Including everything that is necessary', 'example': 'The report provides a comprehensive analysis of the situation.', 'translation': '全面的'},
        {'word': 'deteriorate', 'definition': 'To become worse in quality or condition', 'example': 'His health began to deteriorate after the accident.', 'translation': '恶化'},
        {'word': 'elaborate', 'definition': 'Developed in great detail; complicated', 'example': 'She presented an elaborate plan for the new project.', 'translation': '详尽的'},
        {'word': 'implement', 'definition': 'To put a plan or system into operation', 'example': 'The company will implement new policies next month.', 'translation': '实施'},
        {'word': 'inevitable', 'definition': 'Certain to happen; unavoidable', 'example': 'Change is inevitable in any organization.', 'translation': '不可避免的'},
        {'word': 'legitimate', 'definition': 'Conforming to the law or rules', 'example': 'She has a legitimate reason for being absent.', 'translation': '合法的'},
        {'word': 'predominant', 'definition': 'Being the most important or noticeable', 'example': 'English is the predominant language in business.', 'translation': '主要的'},
        {'word': 'reluctant', 'definition': 'Unwilling and hesitant', 'example': 'He was reluctant to accept the new position.', 'translation': '不情愿的'},
        {'word': 'substantial', 'definition': 'Of considerable importance or size', 'example': 'They made a substantial investment in the company.', 'translation': '大量的'},
    ]
}

def populate_database():
    with app.app_context():
        # Check if database already has data
        existing_count = Vocabulary.query.count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} words.")
            response = input("Do you want to add more words anyway? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Operation cancelled.")
                return
        
        added_count = 0
        skipped_count = 0
        
        print("Adding vocabulary words to database...")
        print("=" * 60)
        
        for level, words in vocabulary_data.items():
            print(f"\nAdding {level} level words...")
            
            for word_data in words:
                # Check if word already exists
                existing = Vocabulary.query.filter_by(word=word_data['word'].lower()).first()
                
                if existing:
                    print(f"  ⊘ Skipped: '{word_data['word']}' (already exists)")
                    skipped_count += 1
                    continue
                
                # Create new vocabulary entry
                new_word = Vocabulary(
                    word=word_data['word'].lower(),
                    definition=word_data['definition'],
                    example=word_data['example'],
                    translation=word_data.get('translation', ''),
                    status='learning',
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                
                db.session.add(new_word)
                print(f"  ✓ Added: '{word_data['word']}'")
                added_count += 1
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"✓ Successfully added {added_count} words")
        if skipped_count > 0:
            print(f"⊘ Skipped {skipped_count} words (already in database)")
        print(f"Total words in database: {Vocabulary.query.count()}")
        print("\nYou can now start the application with: python app.py")

if __name__ == '__main__':
    populate_database()
