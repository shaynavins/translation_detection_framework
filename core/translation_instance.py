class TranslationInstance:
    def __init__(self, source_text, translated_text):
        self.source_text = source_text
        self.translated_text = translated_text
        self.detected_errors = []