# app.py - Python Flask Backend
from flask import Flask, render_template, request, jsonify
import requests
import json
from urllib.parse import quote

app = Flask(__name__)

class TranslationService:
    def __init__(self):
        self.base_url = "https://api.mymemory.translated.net/get"
        
    def translate_text(self, text, source_lang, target_lang):
        """
        Translate text using MyMemory API
        """
        try:
            # Encode the text for URL
            encoded_text = quote(text)
            
            # Build the API URL
            url = f"{self.base_url}?q={encoded_text}&langpair={source_lang}|{target_lang}"
            
            # Make the API request
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            if data.get('responseStatus') == 200:
                return {
                    'success': True,
                    'translated_text': data['responseData']['translatedText'],
                    'source_lang': source_lang,
                    'target_lang': target_lang
                }
            else:
                return {
                    'success': False,
                    'error': data.get('responseDetails', 'Translation failed')
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Translation error: {str(e)}'
            }
    
    def get_supported_languages(self):
        """
        Return list of supported languages
        """
        return {
            'auto': 'Auto-detect',
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese (Simplified)',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'no': 'Norwegian',
            'da': 'Danish',
            'fi': 'Finnish',
            'pl': 'Polish',
            
        }

# Initialize translation service
translator = TranslationService()

@app.route('/')
def index():
    """
    Render the main translation page
    """
    languages = translator.get_supported_languages()
    return render_template('index.html', languages=languages)

@app.route('/translate', methods=['POST'])
def translate():
    """
    Handle translation requests
    """
    try:
        # Get data from the request
        data = request.get_json()
        
        # Validate input
        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': 'No text provided'})
        
        text = data['text'].strip()
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'en')
        
        if not text:
            return jsonify({'success': False, 'error': 'Please enter text to translate'})
        
        if len(text) > 5000:
            return jsonify({'success': False, 'error': 'Text too long (max 5000 characters)'})
        
        if source_lang == target_lang and source_lang != 'auto':
            return jsonify({'success': False, 'error': 'Source and target languages cannot be the same'})
        
        # Perform translation
        result = translator.translate_text(text, source_lang, target_lang)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@app.route('/languages')
def get_languages():
    """
    Get supported languages
    """
    return jsonify(translator.get_supported_languages())

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print(" Starting Translation Server...")
    print(" Open http://localhost:5000 in your browser")
    print(" Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)