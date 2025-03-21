from PyQt6.QtCore import QObject, pyqtSignal
import json
import os
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LanguageManager(QObject):
    _instance = None
    language_changed = pyqtSignal(str)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        super().__init__()
        self._initialized = True
        self._current_language = 'en'
        self._translations = {}
        self._settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'settings.json')
        self._load_settings()
        self._load_translations()
    
    def _load_settings(self):
        """Load language setting from settings file."""
        try:
            if os.path.exists(self._settings_file):
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'language' in settings:
                        old_language = self._current_language
                        self._current_language = settings['language']
                        # Emit signal if language changed during startup
                        if old_language != self._current_language:
                            self.language_changed.emit(self._current_language)
                        logger.info(f"Loaded language setting: {self._current_language}")
        except Exception as e:
            logger.error(f"Failed to load language setting: {str(e)}")
    
    def _save_settings(self):
        """Save language setting to settings file."""
        try:
            settings = {}
            if os.path.exists(self._settings_file):
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            settings['language'] = self._current_language
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self._settings_file), exist_ok=True)
            
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            logger.info(f"Saved language setting: {self._current_language}")
        except Exception as e:
            logger.error(f"Failed to save language setting: {str(e)}")
            # Try to create settings directory and retry
            try:
                os.makedirs(os.path.dirname(self._settings_file), exist_ok=True)
                with open(self._settings_file, 'w', encoding='utf-8') as f:
                    json.dump({'language': self._current_language}, f, indent=4, ensure_ascii=False)
                logger.info(f"Successfully created new settings file with language: {self._current_language}")
            except Exception as e2:
                logger.error(f"Failed to create new settings file: {str(e2)}")
    
    def _load_translations(self):
        """Load translations from JSON files."""
        try:
            translations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'translations')
            
            # Load English translations (default)
            en_file = os.path.join(translations_dir, 'en.json')
            if os.path.exists(en_file):
                with open(en_file, 'r', encoding='utf-8') as f:
                    self._translations['en'] = json.load(f)
            
            # Load Persian translations
            fa_file = os.path.join(translations_dir, 'fa.json')
            if os.path.exists(fa_file):
                with open(fa_file, 'r', encoding='utf-8') as f:
                    self._translations['fa'] = json.load(f)
            
            logger.info("Translations loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load translations: {str(e)}")
    
    def get_current_language(self):
        """Get the current language code."""
        return self._current_language
    
    def set_language(self, language_code):
        """Set the current language and emit change signal."""
        if language_code in self._translations and language_code != self._current_language:
            old_language = self._current_language
            self._current_language = language_code
            self._save_settings()
            # Only emit if language actually changed
            if old_language != language_code:
                self.language_changed.emit(language_code)
                logger.info(f"Language changed from {old_language} to {language_code}")
        else:
            logger.warning(f"Invalid or unchanged language code: {language_code}")
    
    def translate(self, key):
        """Get translation for a key in the current language."""
        try:
            # Split the key into parts
            parts = key.split('.')
            
            # Get the translation dictionary for current language
            translation = self._translations.get(self._current_language, self._translations['en'])
            
            # Navigate through the nested dictionary
            for part in parts:
                translation = translation[part]
            
            return translation
        except KeyError:
            logger.warning(f"Translation key not found: {key}")
            # Fallback to English
            try:
                translation = self._translations['en']
                for part in parts:
                    translation = translation[part]
                return translation
            except KeyError:
                logger.error(f"Translation key not found in fallback language: {key}")
                return key
        except Exception as e:
            logger.error(f"Translation error for key {key}: {str(e)}")
            return key 