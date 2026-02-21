"""
Agent Factory Functions

Creates agent functions for the 3-stage hierarchical evaluation pipeline.
Each factory returns a callable that:
1. Takes MTState as input
2. Invokes LLM with structured output
3. Returns dict to update state

Three factory types:
- make_error_agent_stage1: Super category agents (Accuracy, Fluency, Terminology, Style)
- make_error_agent_stage2: Sub-category agents (13 total) - critically evaluate Stage 1
- make_error_agent_stage3: Verification agents (4 total) - check consistency
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from core.models import AgentOutputStage1, AgentOutputStage2, AgentOutputStage3, MTState, MissingErrorsOutput
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)


def make_error_agent_stage1(system_prompt: str, state_key: str):
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """
            SOURCE SENTENCE: {source}

            MACHINE TRANSLATED SENTENCE: {translated}

            REFERENCE SENTENCE: {reference}""")
        ])
    
    chain = prompt_template | llm.with_structured_output(AgentOutputStage1)
    
    def agent_fn(state: MTState) -> Dict[str, AgentOutputStage1]:
       
        output = chain.invoke({
            "source": state["source"],
            "translated": state["mt"],
            "reference": state["reference"],
        })
        
        return {state_key: output}
    
    return agent_fn


def make_error_agent_stage2(system_prompt: str, state_key: str, super_category: str):
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """
        SOURCE SENTENCE: {source}

        MACHINE TRANSLATED SENTENCE: {translated}

        REFERENCE SENTENCE: {reference}

        PREVIOUS AGENT EVALUATIONS (Stage-1): {previous_agent}

        ROUND: {round}

        MISSING-ERRORS AUDIT (from previous round, may be empty):
        {missing_errors}
        """)
    ])
    
    chain = prompt_template | llm.with_structured_output(AgentOutputStage2)
    
    def agent_fn_stage2(state: MTState) -> Dict[str, AgentOutputStage2]:
       
        missing_errors = state.get("missingErrors")
        if missing_errors is None:
            missing_errors_payload = "None"
        elif hasattr(missing_errors, "model_dump"):
            missing_errors_payload = missing_errors.model_dump()
        else:
            missing_errors_payload = missing_errors

        output = chain.invoke({
            "source": state["source"],
            "translated": state["mt"],
            "reference": state["reference"],
            "previous_agent": state[super_category],
            "round": state.get("round", 1),
            "missing_errors": missing_errors_payload,
        })
        
        return {state_key: output}
    
    return agent_fn_stage2


def make_error_agent_stage3(system_prompt: str, state_key: str, super_category: str):
    
    # Create prompt template that includes both Stage 1 and Stage 2 evaluations
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """
        SOURCE SENTENCE: {source}

        MACHINE TRANSLATED SENTENCE: {translated}

        REFERENCE SENTENCE: {reference}

        SUPER CATEGORY AGENT EVALUATIONS (Stage-1): {previous_agent}

        SUB CATEGORY AGENTS EVALUATIONS (Stage-2): {sub_category_agent}

        ROUND: {round}

        MISSING-ERRORS AUDIT (from previous round, may be empty):
        {missing_errors}
        """)
    ])
    
    chain = prompt_template | llm.with_structured_output(AgentOutputStage3)
    
    def agent_fn_stage3(state: MTState) -> Dict[str, AgentOutputStage3]:
        
        if super_category == "accuracyStage1":
            sub_keys = ["addition", "omission", "mistranslation", "untranslated_text"]
        elif super_category == "fluencyStage1":
            sub_keys = ["punctuation", "spelling", "grammar", "register", "inconsistency", "characterEncoding"]
        elif super_category == "terminologyStage1":
            sub_keys = ["inappropriate_for_context", "inconsistent_use"]
        elif super_category == "styleStage1":
            sub_keys = ["awkward"]
        else:
            sub_keys = []
        
        combined_sub_category = [state[s] for s in sub_keys if state.get(s) is not None]
        
        missing_errors = state.get("missingErrors")
        if missing_errors is None:
            missing_errors_payload = "None"
        elif hasattr(missing_errors, "model_dump"):
            missing_errors_payload = missing_errors.model_dump()
        else:
            missing_errors_payload = missing_errors

        output = chain.invoke({
            "source": state["source"],
            "translated": state["mt"],
            "reference": state["reference"],
            "previous_agent": state[super_category],
            "sub_category_agent": combined_sub_category,
            "round": state.get("round", 1),
            "missing_errors": missing_errors_payload,
        })
        
        return {state_key: output}
    
    return agent_fn_stage3

def make_missing_errors_audit_agent(system_prompt: str, state_key: str = "missingErrors"):
    prompt_temp = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Source sentnce: {source} machine translated sentence: {translated} round: {round} prior pipeline outputs: {prior_state}""")
    ])

    chain = prompt_temp | llm.with_structured_output(MissingErrorsOutput)
    def fn(state: MTState):
        prior_state = {
            # stage 1
            "accuracyStage1": state.get("accuracyStage1"),
            "fluencyStage1": state.get("fluencyStage1"),
            "terminologyStage1": state.get("terminologyStage1"),
            "styleStage1": state.get("styleStage1"),
            # stage 2
            "addition": state.get("addition"),
            "omission": state.get("omission"),
            "mistranslation": state.get("mistranslation"),
            "untranslated_text": state.get("untranslated_text"),
            "punctuation": state.get("punctuation"),
            "spelling": state.get("spelling"),
            "grammar": state.get("grammar"),
            "register": state.get("register"),
            "inconsistency": state.get("inconsistency"),
            "characterEncoding": state.get("characterEncoding"),
            "inappropriate_for_context": state.get("inappropriate_for_context"),
            "inconsistent_use": state.get("inconsistent_use"),
            "awkward": state.get("awkward"),
            # stage 3
            "accuracyStage3": state.get("accuracyStage3"),
            "fluencyStage3": state.get("fluencyStage3"),
            "terminologyStage3": state.get("terminologyStage3"),
            "styleStage3": state.get("styleStage3"),
        }

        output = chain.invoke({
            "source": state["source"],
            "translated": state["mt"],
            "reference": state["reference"],
            "round": state.get("round", 1),
            "prior_state": str(prior_state), 
        })

        return {state_key: output}

    return fn

def test_agent(agent_fn, test_state: MTState):
    
    try:
        result = agent_fn(test_state)
        return result
    except Exception as e:
        print(f"Error testing agent: {e}")
        raise
