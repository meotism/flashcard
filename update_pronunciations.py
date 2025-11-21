"""
Update existing vocabulary words with IPA pronunciation and audio from Cambridge Dictionary
Run this script to add pronunciation data to words that don't have it yet
"""

from app import app, db
from models import Vocabulary
from cambridge_api import fetch_pronunciation_data
import time

def update_pronunciations():
    with app.app_context():
        # Get all words without pronunciation data
        words_without_pronunciation = Vocabulary.query.filter(
            (Vocabulary.ipa_us.is_(None)) | (Vocabulary.ipa_uk.is_(None))
        ).all()
        
        total = len(words_without_pronunciation)
        
        if total == 0:
            print("All words already have pronunciation data!")
            return
        
        print(f"Found {total} words without pronunciation data")
        print("Fetching data from Cambridge Dictionary...")
        print("=" * 70)
        
        updated_count = 0
        failed_count = 0
        
        for i, word in enumerate(words_without_pronunciation, 1):
            print(f"\n[{i}/{total}] Processing: '{word.word}'")
            
            try:
                # Fetch pronunciation data
                pronunciation_data = fetch_pronunciation_data(word.word)
                
                if pronunciation_data and any(pronunciation_data.values()):
                    # Update the word
                    word.ipa_us = pronunciation_data.get('ipa_us')
                    word.ipa_uk = pronunciation_data.get('ipa_uk')
                    word.audio_us = pronunciation_data.get('audio_us')
                    word.audio_uk = pronunciation_data.get('audio_uk')
                    
                    db.session.commit()
                    
                    print(f"  ✓ Updated")
                    if pronunciation_data.get('ipa_uk'):
                        print(f"    UK: /{pronunciation_data.get('ipa_uk')}/")
                    if pronunciation_data.get('ipa_us'):
                        print(f"    US: /{pronunciation_data.get('ipa_us')}/")
                    
                    updated_count += 1
                else:
                    print(f"  ⊘ No data found")
                    failed_count += 1
                
                # Be polite to the server - add delay between requests
                if i < total:
                    time.sleep(1)  # 1 second delay between requests
                    
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                failed_count += 1
                continue
        
        print("\n" + "=" * 70)
        print(f"✓ Successfully updated {updated_count} words")
        if failed_count > 0:
            print(f"⊘ Failed to fetch data for {failed_count} words")
        print(f"\nTotal words with pronunciation: {Vocabulary.query.filter(Vocabulary.ipa_uk.isnot(None) | Vocabulary.ipa_us.isnot(None)).count()}")

if __name__ == '__main__':
    print("Cambridge Dictionary Pronunciation Updater")
    print("=" * 70)
    print("This will fetch IPA pronunciation and audio URLs for existing words")
    print("Note: This process may take several minutes depending on word count")
    print()
    
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        update_pronunciations()
    else:
        print("Operation cancelled.")
