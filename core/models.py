from pydantic import BaseModel, Field
from typing import Optional, Literal
from typing_extensions import TypedDict

class AgentOutputStage1(BaseModel):
   
   #not binary but bayesian score
    probability: float = Field(
        ..., 
        description = "probability that error is present",
        ge =0.0,
        le=1.0
    )
    reason: str = Field(
        ..., 
        description="explanation pointing to thee concreete words or phrases that justify the probability"
    )
    confidence: float = Field(
        ..., 
        description="Score out of 100 on how confident you are that this error is present in the sentence.", 
        ge=0.0, 
        le=100.0
    )

class AgentOutputStage2(BaseModel):
  
    reEvaluatedProb: float = Field(
        ...,
        description="Based on your evaluation re-evaluate the probability while considering the probability given by the previous agent.",
        ge=0.0,
        le=1.0,
    )
    thoughtsOnStage1: str = Field(
        ...,
        description="Based on your evaluations, what are your thoughts on evaluations of the previous agent?",
    )
    reason: str = Field(
        ...,
        description="Give a brief explanation of your thoughts on the previous agent's evaluations. If you agree or disagree with the previous evaluation give concrete evidence for your specific error.",
    )
    reEvaluatedConfidence: float = Field(
        ...,
        description="Based on your evaluations score out of 100 on how confident you are that this error is present in the sentence and that your thoughts and explanations are valid",
        ge=0.0,
        le=100.0,
    )

class AgentOutputStage3(BaseModel):
   
    consistencyScore: float = Field(
        ..., 
        description="Based on the evaluations of the previous agents, generate a score out of 100 on how consistent the agents are with each other.",
        ge=0.0,
        le=100.0
    )
    errorsExists: Literal["NO", "YES"] = Field(
        ..., 
        description="Based on the evaluations of the previous agents verify whether these errors exist or not. Search whether the error flagged by the previous agents exists. If it exists then return 'YES' otherwise return 'NO'"
    )
    existanceReasoning: str = Field(
        ..., 
        description="Give brief explanation on your verification of the existence of the errors."
    )

#not pydantic, deteerministic program
#scoring layer
class AggregationOutput(TypedDict):
    
    accuracy_error: float
    fluency_error: float
    terminology_error: float
    style_error: float
    overall_error_probability: float
    final_quality_score_100: float


class MissingErrorsOutput(BaseModel):
    missingErrorsExists: Literal["NO", "YES"] = Field(...)
    missingErrorTypes: List[str] = Field(default_factory=list)
    reasoning: str = Field(...)

#global shared memory object, graph state   
class MTState(TypedDict):
    
    source: str              
    mt: str                  
    reference: str           
    
    accuracyStage1: Optional[AgentOutputStage1]
    fluencyStage1: Optional[AgentOutputStage1]
    terminologyStage1: Optional[AgentOutputStage1]
    styleStage1: Optional[AgentOutputStage1]
    
    addition: Optional[AgentOutputStage2]
    omission: Optional[AgentOutputStage2]
    mistranslation: Optional[AgentOutputStage2]
    untranslated_text: Optional[AgentOutputStage2]
    
    punctuation: Optional[AgentOutputStage2]
    spelling: Optional[AgentOutputStage2]
    grammar: Optional[AgentOutputStage2]
    register: Optional[AgentOutputStage2]
    inconsistency: Optional[AgentOutputStage2]
    characterEncoding: Optional[AgentOutputStage2]
    
    inappropriate_for_context: Optional[AgentOutputStage2]
    inconsistent_use: Optional[AgentOutputStage2]
    
    awkward: Optional[AgentOutputStage2]
    
    accuracyStage3: Optional[AgentOutputStage3]
    fluencyStage3: Optional[AgentOutputStage3]
    terminologyStage3: Optional[AgentOutputStage3]
    styleStage3: Optional[AgentOutputStage3]
    
    aggregation: Optional[AggregationOutput]

    round: Optional[int]
    max_rounds: Optional[int]
    missingErrors: Optional[MissingErrorsOutput]

