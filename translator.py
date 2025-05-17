from deep_translator import GoogleTranslator

# Read the original file
with open("/regulations/greek.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Translate to English
translator = GoogleTranslator(source='auto', target='en')
translated = translator.translate(text)

# Write to output file
with open("translated_document.txt", "w", encoding="utf-8") as f:
    f.write(translated)

print("✅ Translation complete.")
