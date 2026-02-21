import os
from agents.base_agent import BaseAgent
from core.error_instance import ErrorInstance

class FluencyAgent(BaseAgent):
    def __init__(self, llm_client):
        prompts_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "fluency"
        )

        super().__init__(llm_client, prompts_dir)

        self.error_subtypes = [
            "grammar",
            "spelling",
            "punctuation",
            "inconsistency"
        ]
    def evaluate(self, translation_instance):
        source = translation_instance.source_text
        translation = translation_instance.translated_text

        errors = []

        for subtype in self.error_subtypes:
            result = self.evaluate_single(subtype, source, translation)

            if result is not None:
                errors.append(result)
        return errors
    

    def get_error_subtypes(self):
        return self.error_subtypes