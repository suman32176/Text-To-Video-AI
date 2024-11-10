from googletrans import Translator

def translate_script(script, source_lang, target_lang):
    translator = Translator()
    translated_script = translator.translate(script, src=source_lang, dest=target_lang).text
    return translated_script
