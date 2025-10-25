import json
import os
import sys

# These are our "global" variables, just like in the JS file.
_translations = {}
_current_lang = 'en'  # This is the default language
_DEFAULT_LANG = 'en'

def load_translations():
    """Loads the translation file from the project root."""
    
    # This 'global' keyword lets us modify the _translations variable
    global _translations
    
    try:
        # Get the absolute path to *this* file (i18n.py)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Build a safe path from this file up to the root
        file_path = os.path.join(base_dir, '..', 'translations.json')
        
        # Open the file for reading with 'utf-8' encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            _translations = json.load(f)
            
    except Exception as e:
        # If anything goes wrong (file not found, bad JSON),
        print(f"[i18n] WARNING: Could not load translations.json. Error: {e}", file=sys.stderr)

def set_language(lang_code: str):
    """Sets the active language for the session."""
    
    global _current_lang
    
    # Check if the lang_code is valid AND exists in our dictionary
    if lang_code and lang_code in _translations:
        _current_lang = lang_code
    else:
        _current_lang = _DEFAULT_LANG

def t(key: str, variables: dict = None) -> str:
    """
    Gets the translated string, replacing placeholders with variables.
    e.g., t('greeting', {'name': 'User'})
    """
    
    if variables is None:
        variables = {}

    # 1. Try to find the key in the current language
    message = _translations.get(_current_lang, {}).get(key)
    
    # 2. If not found, fall back to English
    if message is None:
        message = _translations.get(_DEFAULT_LANG, {}).get(key)
        
    # 3. If still not found, return a warning
    if message is None:
        return f"MISSING_KEY: {key}"
        
    # --- THIS IS THE NEW PART ---
    # 4. Loop through all variables and replace placeholders
    # It will find "{command}" and replace it with the value of variables['command']
    for var_name, value in variables.items():
        message = message.replace(f"{{{var_name}}}", str(value))
    
    return message


load_translations()