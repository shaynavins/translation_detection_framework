from langgraph.graph import StateGraph, START, END
from core.models import MTState
from agents.agent_factory import(
    make_error_agent_stage1,
    make_error_agent_stage2,
    make_error_agent_stage3,
    make_missing_errors_audit_agent
)
from prompts.stage1_prompts import (
    ACCURACY_PROMPT, 
    FLUENCY_PROMPT, 
    TERMINOLOGY_PROMPT, 
    STYLE_PROMPT,
)
from prompts.missing_errors_prompt import MISSING_ERRORS_PROMPT
from prompts.stage2_prompts import (
    #Accuracy 
    ADDITION_PROMPT,
    OMISSION_PROMPT,
    MISTRANSLATION_PROMPT,
    UNTRANSLATED_TEXT_PROMPT,
    #Fluency 
    PUNCTUATION_PROMPT,
    SPELLING_PROMPT,
    GRAMMAR_PROMPT,
    REGISTER_PROMPT,
    INCONSISTENCY_PROMPT,
    CHARACTER_ENCODING_PROMPT,
    #Terminology
    INAPPROPRIATE_FOR_CONTEXT_PROMPT,
    INCONSISTENT_USE_PROMPT,
    #Style
    AWKWARD_PROMPT
)
from prompts.stage3_prompts import (
    ACCURACY_STAGE3_PROMPT,
    FLUENCY_STAGE3_PROMPT,
    TERMINOLOGY_STAGE3_PROMPT,
    STYLE_STAGE3_PROMPT
)
from core.aggregation import aggregate_mt_quality


#parallel
accuracy_agent = make_error_agent_stage1(ACCURACY_PROMPT, "accuracyStage1")
fluency_agent = make_error_agent_stage1(FLUENCY_PROMPT, "fluencyStage1")
terminology_agent = make_error_agent_stage1(TERMINOLOGY_PROMPT, "terminologyStage1")
style_agent = make_error_agent_stage1(STYLE_PROMPT, "styleStage1")


addition_agent = make_error_agent_stage2(ADDITION_PROMPT, "addition", "accuracyStage1")
omission_agent = make_error_agent_stage2(OMISSION_PROMPT, "omission", "accuracyStage1")
mistranslation_agent = make_error_agent_stage2(MISTRANSLATION_PROMPT, "mistranslation", "accuracyStage1")
untranslated_text_agent = make_error_agent_stage2(UNTRANSLATED_TEXT_PROMPT, "untranslated_text", "accuracyStage1")

punctuation_agent = make_error_agent_stage2(PUNCTUATION_PROMPT, "punctuation", "fluencyStage1")
spelling_agent = make_error_agent_stage2(SPELLING_PROMPT, "spelling", "fluencyStage1")
grammar_agent = make_error_agent_stage2(GRAMMAR_PROMPT, "grammar", "fluencyStage1")
register_agent = make_error_agent_stage2(REGISTER_PROMPT, "register", "fluencyStage1")
inconsistency_agent = make_error_agent_stage2(INCONSISTENCY_PROMPT, "inconsistency", "fluencyStage1")
characterEncoding_agent = make_error_agent_stage2(CHARACTER_ENCODING_PROMPT, "characterEncoding", "fluencyStage1")

inappropriate_for_context_agent = make_error_agent_stage2(INAPPROPRIATE_FOR_CONTEXT_PROMPT, "inappropriate_for_context", "terminologyStage1")
inconsistent_use_agent = make_error_agent_stage2(INCONSISTENT_USE_PROMPT, "inconsistent_use", "terminologyStage1")

awkward_agent = make_error_agent_stage2(AWKWARD_PROMPT, "awkward", "styleStage1")



accuracy_stage3_agent = make_error_agent_stage3(ACCURACY_STAGE3_PROMPT, "accuracyStage3", "accuracyStage1")
fluency_stage3_agent = make_error_agent_stage3(FLUENCY_STAGE3_PROMPT, "fluencyStage3", "fluencyStage1")
terminology_stage3_agent = make_error_agent_stage3(TERMINOLOGY_STAGE3_PROMPT, "terminologyStage3", "terminologyStage1")
style_stage3_agent = make_error_agent_stage3(STYLE_STAGE3_PROMPT, "styleStage3", "styleStage1")



def loop_controller(state: MTState) -> dict:
    current = state.get("round") or 1
    return {"round": current + 1}

def should_loop(state: MTState) -> str:
    missing = state.get("missingErrors")
    round_ = state.get("round") or 1
    max_rounds = state.get("max_rounds") or 1

    if missing and getattr(missing, "missingErrorsExists", None) == "YES" and round_ < max_rounds:
        return "loop"
    return "done"

missing_errors_agent = make_missing_errors_audit_agent(MISSING_ERRORS_PROMPT, "missingErrors")
graph = StateGraph(MTState)



graph.add_node("accuracyStage1_node", accuracy_agent)
graph.add_node("fluencyStage1_node", fluency_agent)
graph.add_node("terminologyStage1_node", terminology_agent)
graph.add_node("styleStage1_node", style_agent)

graph.add_node("addition_node", addition_agent)
graph.add_node("omission_node", omission_agent)
graph.add_node("mistranslation_node", mistranslation_agent)
graph.add_node("untranslated_text_node", untranslated_text_agent)

graph.add_node("punctuation_node", punctuation_agent)
graph.add_node("spelling_node", spelling_agent)
graph.add_node("grammar_node", grammar_agent)
graph.add_node("register_node", register_agent)
graph.add_node("inconsistency_node", inconsistency_agent)
graph.add_node("characterEncoding_node", characterEncoding_agent)

graph.add_node("inappropriate_for_context_node", inappropriate_for_context_agent)
graph.add_node("inconsistent_use_node", inconsistent_use_agent)

graph.add_node("awkward_node", awkward_agent)

graph.add_node("accuracyStage3_node", accuracy_stage3_agent)
graph.add_node("fluencyStage3_node", fluency_stage3_agent)
graph.add_node("terminologyStage3_node", terminology_stage3_agent)
graph.add_node("styleStage3_node", style_stage3_agent)

graph.add_node("aggregation_node", aggregate_mt_quality)

graph.add_node("missing_errors_node", missing_errors_agent)
graph.add_node("loop_controller_node", loop_controller)


graph.add_edge(START, "accuracyStage1_node")
graph.add_edge(START, "fluencyStage1_node")
graph.add_edge(START, "terminologyStage1_node")
graph.add_edge(START, "styleStage1_node")

graph.add_edge("accuracyStage1_node", "addition_node")
graph.add_edge("accuracyStage1_node", "omission_node")
graph.add_edge("accuracyStage1_node", "mistranslation_node")
graph.add_edge("accuracyStage1_node", "untranslated_text_node")

graph.add_edge("fluencyStage1_node", "punctuation_node")
graph.add_edge("fluencyStage1_node", "spelling_node")
graph.add_edge("fluencyStage1_node", "grammar_node")
graph.add_edge("fluencyStage1_node", "register_node")
graph.add_edge("fluencyStage1_node", "inconsistency_node")
graph.add_edge("fluencyStage1_node", "characterEncoding_node")

graph.add_edge("terminologyStage1_node", "inappropriate_for_context_node")
graph.add_edge("terminologyStage1_node", "inconsistent_use_node")


graph.add_edge("styleStage1_node", "awkward_node")


graph.add_edge("addition_node", "accuracyStage3_node")
graph.add_edge("omission_node", "accuracyStage3_node")
graph.add_edge("mistranslation_node", "accuracyStage3_node")
graph.add_edge("untranslated_text_node", "accuracyStage3_node")

graph.add_edge("punctuation_node", "fluencyStage3_node")
graph.add_edge("spelling_node", "fluencyStage3_node")
graph.add_edge("grammar_node", "fluencyStage3_node")
graph.add_edge("register_node", "fluencyStage3_node")
graph.add_edge("inconsistency_node", "fluencyStage3_node")
graph.add_edge("characterEncoding_node", "fluencyStage3_node")

graph.add_edge("inappropriate_for_context_node", "terminologyStage3_node")
graph.add_edge("inconsistent_use_node", "terminologyStage3_node")

graph.add_edge("awkward_node", "styleStage3_node")

graph.add_edge("accuracyStage3_node", "missing_errors_node")
graph.add_edge("fluencyStage3_node", "missing_errors_node")
graph.add_edge("terminologyStage3_node", "missing_errors_node")
graph.add_edge("styleStage3_node", "missing_errors_node")

graph.add_edge("aggregation_node", END)

graph.add_conditional_edges(
    "missing_errors_node",
    should_loop,
    {
        "loop": "loop_controller_node",
        "done": "aggregation_node",

    },
)
graph.add_edge("loop_controller_node", "accuracyStage1_node")
graph.add_edge("loop_controller_node", "fluencyStage1_node")
graph.add_edge("loop_controller_node", "terminologyStage1_node")
graph.add_edge("loop_controller_node", "styleStage1_node")



app = graph.compile()
print("Graph compiled successfully!")