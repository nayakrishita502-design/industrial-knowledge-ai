from typing import Dict, Optional
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from datetime import datetime


class RootCauseAnalysisAgent:
    """AI agent for root cause analysis of industrial failures."""
    
    RCA_PROMPT = PromptTemplate(
        input_variables=["failure_description", "equipment", "history"],
        template="""You are an expert industrial failure analyst with 20+ years of experience 
in root cause analysis for industrial equipment. Analyze this equipment failure using 
systematic RCA methodology.

## Equipment Information
**Equipment:** {equipment}

## Failure Description
{failure_description}

## Historical Context
{history}

## Required Analysis

Provide a comprehensive root cause analysis following this structure:

### 1. IMMEDIATE CAUSE
What directly caused the failure? (The trigger event)

### 2. ROOT CAUSE(S)
Why did that condition exist? Use the 5-Why technique to identify underlying causes.
- Why #1:
- Why #2:
- Why #3:
- Why #4:
- Why #5 (Root Cause):

### 3. CONTRIBUTING FACTORS
What other factors contributed to the failure?
- Human factors:
- Environmental factors:
- Maintenance factors:
- Design factors:

### 4. FAILURE MODE ANALYSIS
- Failure mode:
- Failure mechanism:
- Failure effect:

### 5. PREVENTIVE ACTIONS
Recommend specific actions to prevent recurrence:

#### Immediate Actions (0-7 days):
- 

#### Short-term Actions (1-4 weeks):
- 

#### Long-term Actions (1-3 months):
- 

### 6. LESSONS LEARNED
Key takeaways that should be documented and shared:
- 

Provide specific, actionable recommendations based on industrial best practices."""
    )
    
    QUICK_RCA_PROMPT = PromptTemplate(
        input_variables=["failure_description", "equipment"],
        template="""Analyze this industrial equipment failure briefly:

Equipment: {equipment}
Failure: {failure_description}

Provide:
1. Most likely root cause (1-2 sentences)
2. Immediate recommended action (1-2 sentences)
3. Key preventive measure (1-2 sentences)

Be specific and actionable."""
    )
    
    def __init__(self, google_api_key: str):
        """Initialize RCA agent."""
        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=google_api_key
        )
    
    def analyze_failure(
        self, 
        failure_description: str, 
        equipment: str, 
        historical_context: str = ""
    ) -> Dict:
        """Perform full root cause analysis."""
        if not failure_description.strip():
            return {"status": "error", "message": "Failure description is required"}
        
        if not equipment.strip():
            return {"status": "error", "message": "Equipment identifier is required"}
        
        try:
            prompt = self.RCA_PROMPT.format(
                failure_description=failure_description,
                equipment=equipment,
                history=historical_context or "No historical context provided."
            )
            
            analysis = self.llm.invoke(prompt)
            
            return {
                "status": "success",
                "equipment": equipment,
                "analysis": analysis,
                "analysis_type": "FULL_RCA",
                "timestamp": datetime.now().isoformat(),
                "methodology": "5-Why Analysis with Failure Mode Analysis"
            }
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def quick_analysis(self, failure_description: str, equipment: str) -> Dict:
        """Perform quick root cause analysis."""
        if not failure_description.strip() or not equipment.strip():
            return {"status": "error", "message": "Both failure description and equipment are required"}
        
        try:
            prompt = self.QUICK_RCA_PROMPT.format(
                failure_description=failure_description,
                equipment=equipment
            )
            
            analysis = self.llm.invoke(prompt)
            
            return {
                "status": "success",
                "equipment": equipment,
                "analysis": analysis,
                "analysis_type": "QUICK_RCA",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def suggest_investigation_questions(self, failure_description: str) -> Dict:
        """Suggest investigation questions for RCA."""
        prompt = f"""Based on this industrial failure, suggest 10 key investigation 
questions that should be answered during root cause analysis:

Failure: {failure_description}

Provide questions that cover:
- Timeline of events
- Equipment condition before failure
- Maintenance history
- Operating conditions
- Human factors
- Environmental factors

Format as numbered list."""
        
        try:
            questions = self.llm.invoke(prompt)
            return {
                "status": "success",
                "questions": questions,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}