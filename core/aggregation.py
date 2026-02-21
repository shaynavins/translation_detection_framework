from typing import Dict, List
from core.models import MTState, AggregationOutput


def weighted_mean(probs: List[float], confs: List[float]) -> float:
   
#epistemic weighting
    if not probs or not confs:
        return 0.0
    
    weights = [c / 100.0 for c in confs]
    total_weight = sum(weights)
    
    if total_weight == 0:
        return 0.0
    
    return sum(p * w for p, w in zip(probs, weights)) / total_weight


def aggregate_super_category(
    state: MTState, 
    sub_keys: List[str], 
    stage3_key: str
) -> float:
    
    probs = []
    confs = []
    
    for key in sub_keys:
        agent_output = state.get(key)
        if agent_output is not None:
            #collect only stage 2 signals because they are the refined version
            probs.append(agent_output.reEvaluatedProb)
            confs.append(agent_output.reEvaluatedConfidence)
    
    base_score = weighted_mean(probs, confs)
    
    stage3 = state.get(stage3_key)
    
    if stage3 is None:
        return base_score
    
    
    if stage3.errorsExists == "NO":
        return base_score * 0.3  
    

    consistency_factor = stage3.consistencyScore / 100.0
    return base_score * consistency_factor


def aggregate_mt_quality(state: MTState) -> Dict[str, AggregationOutput]:
    
    accuracy_subs = ["addition", "omission", "mistranslation", "untranslated_text"]
    fluency_subs = ["punctuation", "spelling", "grammar", "register", "inconsistency", "characterEncoding"]
    terminology_subs = ["inappropriate_for_context", "inconsistent_use"]
    style_subs = ["awkward"]
    
    acc_score = aggregate_super_category(state, accuracy_subs, "accuracyStage3")
    flu_score = aggregate_super_category(state, fluency_subs, "fluencyStage3")
    term_score = aggregate_super_category(state, terminology_subs, "terminologyStage3")
    style_score = aggregate_super_category(state, style_subs, "styleStage3")
    
    weights = {
        "accuracy": 0.4,     
        "fluency": 0.3,       
        "terminology": 0.2,   
        "style": 0.1,        
    }
    
    overall_error_prob = (
        weights["accuracy"] * acc_score +
        weights["fluency"] * flu_score +
        weights["terminology"] * term_score +
        weights["style"] * style_score
    )
    
   
    final_quality_score = (1.0 - overall_error_prob) * 100.0
    
    return {
        "aggregation": {
            "accuracy_error": acc_score,
            "fluency_error": flu_score,
            "terminology_error": term_score,
            "style_error": style_score,
            "overall_error_probability": overall_error_prob,
            "final_quality_score_100": final_quality_score,
        }
    }


def get_error_breakdown(state: MTState) -> Dict[str, Dict[str, float]]:
   
    breakdown = {
        "accuracy": {},
        "fluency": {},
        "terminology": {},
        "style": {}
    }
    
    for key in ["addition", "omission", "mistranslation", "untranslated_text"]:
        if state.get(key):
            breakdown["accuracy"][key] = state[key].reEvaluatedProb
    
    for key in ["punctuation", "spelling", "grammar", "register", "inconsistency", "characterEncoding"]:
        if state.get(key):
            breakdown["fluency"][key] = state[key].reEvaluatedProb
    
    for key in ["inappropriate_for_context", "inconsistent_use"]:
        if state.get(key):
            breakdown["terminology"][key] = state[key].reEvaluatedProb
    
    for key in ["awkward"]:
        if state.get(key):
            breakdown["style"][key] = state[key].reEvaluatedProb
    
    return breakdown


def get_consistency_scores(state: MTState) -> Dict[str, float]:
    
    scores = {}
    
    if state.get("accuracyStage3"):
        scores["accuracy"] = state["accuracyStage3"].consistencyScore
    
    if state.get("fluencyStage3"):
        scores["fluency"] = state["fluencyStage3"].consistencyScore
    
    if state.get("terminologyStage3"):
        scores["terminology"] = state["terminologyStage3"].consistencyScore
    
    if state.get("styleStage3"):
        scores["style"] = state["styleStage3"].consistencyScore
    
    return scores


def get_verified_errors(state: MTState) -> Dict[str, bool]:
    
    verified = {}
    
    if state.get("accuracyStage3"):
        verified["accuracy"] = state["accuracyStage3"].errorsExists == "YES"
    
    if state.get("fluencyStage3"):
        verified["fluency"] = state["fluencyStage3"].errorsExists == "YES"
    
    if state.get("terminologyStage3"):
        verified["terminology"] = state["terminologyStage3"].errorsExists == "YES"
    
    if state.get("styleStage3"):
        verified["style"] = state["styleStage3"].errorsExists == "YES"
    
    return verified
