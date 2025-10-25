const fs = require('fs');
const path = require('path');

let translations = {};
let currentLang = 'en'; // This is the default language
const DEFAULT_LANG = 'en';

/*** Loads the translation file from the project root.*/
function loadTranslations() {
    try {
        // Build a safe path to the file
        const resolvedPath = path.resolve(__dirname, '../translations.json');
        
        // Read the file's content
        const fileContent = fs.readFileSync(resolvedPath, 'utf-8');
        
        // Convert the text content into a JavaScript object
        translations = JSON.parse(fileContent);

    } catch (error) {
        // If the file is missing or broken, print a warning
        console.warn(`[i18n] WARNING: Could not load translations.json. Error: ${error.message}`);
    }
}

/**
 * Sets the active language for the session.
 */
function setLanguage(langCode) {
    // Check if the language (e.g., "es") exists in our file
    if (langCode && translations[langCode]) {
        currentLang = langCode;
    } else {
        // If not, just use the default (English)
        currentLang = DEFAULT_LANG;
    }
}

/**
 * Gets the translated string for a given key.
 */
function t(key, variables = {}) {
    /**
     * Translates a key, replacing placeholders with variables.
     * e.g., t('greeting', { name: 'User' })
     */
    
    // 1. Try to get the message in the current language
    let message = translations[currentLang]?.[key];
    
    // 2. If not found, fall back to default language (English)
    if (message === undefined) {
        message = translations[DEFAULT_LANG]?.[key];
    }
    
    // 3. If still not found, return the key as a clear warning
    if (message === undefined) {
        return `MISSING_KEY: ${key}`;
    }

    // --- THIS IS THE NEW PART ---
    // 4. Loop through all variables and replace placeholders
    // It will find "{command}" and replace it with the value of variables.command
    for (const varName in variables) {
        const placeholder = `{${varName}}`;
        // Use a loop to replace all instances, in case it appears more than once
        while(message.includes(placeholder)) {
            message = message.replace(placeholder, variables[varName]);
        }
    }
    
    return message;
}

// --- Run the loading function as soon as this file is loaded ---
loadTranslations();

// --- Make the 'setLanguage' and 't' functions usable by other files ---
module.exports = {
    setLanguage,
    t
};