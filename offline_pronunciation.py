"""
Offline pronunciation fetcher using eng_to_ipa and pyttsx3
Works 100% offline without internet connection
"""
import eng_to_ipa as ipa
import pyttsx3
import os

def get_ipa_pronunciation(word):
    """
    Get IPA pronunciation using offline library
    Returns US IPA format
    """
    try:
        # Convert to IPA (American English)
        ipa_text = ipa.convert(word)
        return ipa_text if ipa_text else None
    except Exception as e:
        print(f"[IPA] Error converting '{word}': {str(e)}")
        return None

def generate_audio_url(word):
    """
    Generate audio using pyttsx3 (100% offline, no internet needed)
    Saves to static folder and returns URL path
    """
    try:
        # Create static/audio directory if not exists
        audio_dir = os.path.join(os.path.dirname(__file__), 'static', 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        
        # Create filename from word (sanitize)
        safe_word = "".join(c for c in word if c.isalnum() or c in (' ', '-', '_')).strip()
        audio_filename = f"{safe_word}_{hash(word) % 10000}.wav"
        audio_path = os.path.join(audio_dir, audio_filename)
        
        # Check if audio already exists
        if os.path.exists(audio_path):
            return f"/static/audio/{audio_filename}"
        
        # Initialize pyttsx3 engine (offline TTS)
        engine = pyttsx3.init()
        
        # Set properties for US English voice
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Try to set US English voice if available
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'english' in voice.name.lower() and 'us' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        
        # Save audio to file in static/audio directory
        engine.save_to_file(word, audio_path)
        engine.runAndWait()
        
        # Return URL path (WAV format - widely supported)
        return f"/static/audio/{audio_filename}"
    
    except Exception as e:
        print(f"[Audio] Error generating audio for '{word}': {str(e)}")
        return None

def fetch_offline_pronunciation(word):
    """
    Fetch pronunciation data using offline methods
    Returns dict with ipa_us and audio_us
    """
    print(f"[Offline Pronunciation] Fetching data for: {word}")
    
    result = {
        'ipa_us': None,
        'ipa_uk': None,  # Same as US for this library
        'audio_us': None,
        'audio_uk': None
    }
    
    # Get IPA (offline, always works)
    ipa_us = get_ipa_pronunciation(word)
    if ipa_us:
        result['ipa_us'] = ipa_us
        result['ipa_uk'] = ipa_us  # Use same for UK
        print(f"[Offline Pronunciation] IPA found: {ipa_us}")
    
    # Try to generate audio (requires internet but lightweight)
    try:
        audio = generate_audio_url(word)
        if audio:
            result['audio_us'] = audio
            result['audio_uk'] = audio
            print(f"[Offline Pronunciation] Audio generated successfully")
    except Exception as e:
        print(f"[Offline Pronunciation] Audio generation failed: {str(e)}")
    
    return result
