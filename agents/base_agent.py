import os
import json
from abc import ABC, abstractmethod
from core.error_instance import ErrorInstance


class BaseAgent(ABC):

    def __init__(self, llm_client, prompts_dir):
        self.llm_client = llm_client
        self.prompts_dir = prompts_dir
        self.prompts = self._load_prompts()


    def _load_prompts(self):
        prompts = {}

        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.prompts_dir, filename)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                error_type = filename.replace(".json", "")
                prompts[error_type] = data

        return prompts

    def build_prompt(self, error_type, source, translation):
        config = self.prompts.get(error_type)

        if not config:
            raise ValueError(f"No prompt config found for {error_type}")

        error_definition = config.get("definition", "")
        examples = config.get("examples", [])

        examples_text = ""

        for ex in examples:
            label = "Error Exists" if ex.get("error_exists") else "No Error"
            severity = ex.get("severity", "")
            explanation = ex.get("explanation", "")
            examples_text += f"\nSource: {ex['source']}\nTranslation: {ex['translation']}\nError Exist: {label}\nSeverity: {severity}\nExplanation: {explanation}\n"

        user_prompt = f"""
                You are evaluating translation accuracy.

                Error Type: {error_type}

                Definition:
                {error_definition}

                Examples:
                {examples_text}

                Now evaluate the following:

                Source:
                {source}

                Translation:
                {translation}

                Reply strictly in this format:

                Error Exist: Yes/No
                Severity: Major/Minor/Neutral
                Explanation: <explanation>
                """

        return user_prompt.strip()


    def evaluate_single(self, error_type, source, translation):
        system_prompt = "You are a professional machine translation evaluator."

        user_prompt = self.build_prompt(error_type, source, translation)

        response = self.llm_client.call(system_prompt, user_prompt)

        return self._parse_response(error_type, response)

   
    def _parse_response(self, error_type, response_text):

        lines = response_text.split("\n")

        error_exist = None
        severity = None
        explanation = ""

        for line in lines:
            if line.lower().startswith("error exist"):
                if "yes" in line.lower():
                    error_exist = True
                else:
                    error_exist = False

            elif line.lower().startswith("severity"):
                severity = line.split(":")[-1].strip()

            elif line.lower().startswith("explanation"):
                explanation = line.split(":", 1)[-1].strip()

        if not error_exist:
            return None

        return ErrorInstance(
            span="Full sentence",   
            subtype=error_type,
            confidence=1.0,       
            explanation=explanation
        )

   
    @abstractmethod
    def evaluate(self, translation_instance):
        pass