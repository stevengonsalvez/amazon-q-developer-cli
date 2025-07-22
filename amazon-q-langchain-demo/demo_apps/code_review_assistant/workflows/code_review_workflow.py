"""
ABOUTME: Advanced code review workflow using LangGraph and Amazon Q
Multi-step agentic workflow for comprehensive code analysis and review
"""

import asyncio
import logging
from typing import TypedDict, List, Optional, Dict, Any
from enum import Enum

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

# Import our Amazon Q integration
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from amazon_q_langchain import ChatAmazonQ

logger = logging.getLogger(__name__)


class ReviewPriority(Enum):
    """Priority levels for review findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CodeReviewState(TypedDict):
    """State for the code review workflow."""
    # Input
    code: str
    language: str
    context: Optional[str]
    
    # Analysis results
    structure_analysis: str
    security_analysis: str
    performance_analysis: str
    maintainability_analysis: str
    
    # Review outputs
    issues: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    documentation: str
    refactored_code: str
    
    # Summary
    executive_summary: str
    priority_actions: List[str]
    effort_estimate: str
    
    # Metadata
    workflow_status: str
    error_messages: List[str]


class CodeReviewWorkflow:
    """Advanced code review workflow using LangGraph."""
    
    def __init__(self):
        """Initialize the workflow."""
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the Amazon Q LLM."""
        try:
            self.llm = ChatAmazonQ()
            logger.info("Amazon Q LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Amazon Q LLM: {e}")
            raise
    
    async def analyze_structure_node(self, state: CodeReviewState) -> CodeReviewState:
        """Analyze code structure and architecture."""
        logger.info("🏗️  Analyzing code structure...")
        
        try:
            prompt = f"""
            Analyze the structure and architecture of this {state['language']} code:
            
            ```{state['language']}
            {state['code']}
            ```
            
            Context: {state.get('context', 'No additional context provided')}
            
            Provide a detailed analysis covering:
            1. **Code Organization**: How well is the code organized and structured?
            2. **Design Patterns**: What design patterns are used (or should be used)?
            3. **Modularity**: How modular and reusable is the code?
            4. **Coupling and Cohesion**: Assessment of dependencies and relationships
            5. **Scalability**: How well will this code scale?
            6. **Architecture Issues**: Any architectural problems or anti-patterns
            
            Format your response as a structured analysis with clear sections.
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            return {
                **state,
                "structure_analysis": response.content,
                "workflow_status": "structure_complete"
            }
            
        except Exception as e:
            logger.error(f"Structure analysis failed: {e}")
            return {
                **state,
                "structure_analysis": f"Analysis failed: {str(e)}",
                "error_messages": state.get("error_messages", []) + [f"Structure analysis: {str(e)}"],
                "workflow_status": "structure_error"
            }
    
    async def analyze_security_node(self, state: CodeReviewState) -> CodeReviewState:
        """Analyze security vulnerabilities and concerns."""
        logger.info("🔒 Analyzing security aspects...")
        
        try:
            prompt = f"""
            Perform a comprehensive security analysis of this {state['language']} code:
            
            ```{state['language']}
            {state['code']}
            ```
            
            Previous structure analysis:
            {state.get('structure_analysis', 'No previous analysis')}
            
            Focus on:
            1. **Input Validation**: Are inputs properly validated and sanitized?
            2. **Authentication & Authorization**: Security controls and access management
            3. **Data Protection**: How is sensitive data handled?
            4. **Injection Vulnerabilities**: SQL injection, XSS, command injection risks
            5. **Error Handling**: Are errors handled securely without information leakage?
            6. **Cryptography**: Proper use of encryption and hashing
            7. **Dependencies**: Security risks from external libraries
            8. **Common Vulnerabilities**: OWASP Top 10 considerations
            
            For each issue found, provide:
            - Severity level (Critical/High/Medium/Low)
            - Description of the vulnerability
            - Potential impact
            - Specific remediation steps
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            return {
                **state,
                "security_analysis": response.content,
                "workflow_status": "security_complete"
            }
            
        except Exception as e:
            logger.error(f"Security analysis failed: {e}")
            return {
                **state,
                "security_analysis": f"Analysis failed: {str(e)}",
                "error_messages": state.get("error_messages", []) + [f"Security analysis: {str(e)}"],
                "workflow_status": "security_error"
            }
    
    async def analyze_performance_node(self, state: CodeReviewState) -> CodeReviewState:
        """Analyze performance characteristics and optimization opportunities."""
        logger.info("⚡ Analyzing performance...")
        
        try:
            prompt = f"""
            Analyze the performance characteristics of this {state['language']} code:
            
            ```{state['language']}
            {state['code']}
            ```
            
            Previous analyses:
            Structure: {state.get('structure_analysis', 'N/A')[:200]}...
            Security: {state.get('security_analysis', 'N/A')[:200]}...
            
            Evaluate:
            1. **Time Complexity**: Big O analysis of algorithms
            2. **Space Complexity**: Memory usage patterns
            3. **Bottlenecks**: Identify performance bottlenecks
            4. **Resource Usage**: CPU, memory, I/O efficiency
            5. **Concurrency**: Threading and async patterns
            6. **Database Performance**: Query optimization (if applicable)
            7. **Caching Opportunities**: Where caching could help
            8. **Optimization Suggestions**: Specific improvements
            
            Provide:
            - Performance rating (Excellent/Good/Fair/Poor)
            - Specific bottlenecks with line numbers
            - Optimization recommendations with expected impact
            - Code examples for improvements
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            return {
                **state,
                "performance_analysis": response.content,
                "workflow_status": "performance_complete"
            }
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {
                **state,
                "performance_analysis": f"Analysis failed: {str(e)}",
                "error_messages": state.get("error_messages", []) + [f"Performance analysis: {str(e)}"],
                "workflow_status": "performance_error"
            }
    
    async def analyze_maintainability_node(self, state: CodeReviewState) -> CodeReviewState:
        """Analyze code maintainability and readability."""
        logger.info("🔧 Analyzing maintainability...")
        
        try:
            prompt = f"""
            Analyze the maintainability and readability of this {state['language']} code:
            
            ```{state['language']}
            {state['code']}
            ```
            
            Consider:
            1. **Code Readability**: How easy is it to understand?
            2. **Documentation**: Quality and completeness of comments/docs
            3. **Naming Conventions**: Variable, function, class names
            4. **Code Complexity**: Cyclomatic complexity, nesting levels
            5. **DRY Principle**: Code duplication issues
            6. **SOLID Principles**: Adherence to SOLID design principles
            7. **Testing**: Testability and test coverage considerations
            8. **Error Handling**: Robustness and error management
            9. **Code Style**: Consistency with language conventions
            10. **Technical Debt**: Areas that need refactoring
            
            Provide:
            - Maintainability score (1-10)
            - Specific issues with line references
            - Refactoring recommendations
            - Best practices to implement
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            return {
                **state,
                "maintainability_analysis": response.content,
                "workflow_status": "maintainability_complete"
            }
            
        except Exception as e:
            logger.error(f"Maintainability analysis failed: {e}")
            return {
                **state,
                "maintainability_analysis": f"Analysis failed: {str(e)}",
                "error_messages": state.get("error_messages", []) + [f"Maintainability analysis: {str(e)}"],
                "workflow_status": "maintainability_error"
            }
    
    async def synthesize_findings_node(self, state: CodeReviewState) -> CodeReviewState:
        """Synthesize all analyses into structured findings."""
        logger.info("🔍 Synthesizing findings...")
        
        try:
            prompt = f"""
            Based on the comprehensive analyses below, synthesize the findings into structured issues and suggestions:
            
            STRUCTURE ANALYSIS:
            {state.get('structure_analysis', 'Not available')}
            
            SECURITY ANALYSIS:
            {state.get('security_analysis', 'Not available')}
            
            PERFORMANCE ANALYSIS:
            {state.get('performance_analysis', 'Not available')}
            
            MAINTAINABILITY ANALYSIS:
            {state.get('maintainability_analysis', 'Not available')}
            
            Create two structured lists:
            
            1. **ISSUES** (Problems that need fixing):
            For each issue, provide:
            - Title: Brief description
            - Priority: Critical/High/Medium/Low
            - Category: Security/Performance/Maintainability/Structure
            - Description: Detailed explanation
            - Location: Line numbers or code sections
            - Impact: What happens if not fixed
            
            2. **SUGGESTIONS** (Improvements and enhancements):
            For each suggestion, provide:
            - Title: Brief description
            - Priority: High/Medium/Low
            - Category: Performance/Readability/Architecture/Best Practices
            - Description: Detailed explanation
            - Benefit: Expected improvement
            - Effort: Low/Medium/High implementation effort
            
            Format as JSON-like structure for easy parsing.
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            # For now, store as text - in production, we'd parse this into structured data
            return {
                **state,
                "issues": [{"raw_analysis": response.content}],
                "suggestions": [{"raw_analysis": response.content}],
                "workflow_status": "synthesis_complete"
            }
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return {
                **state,
                "issues": [{"error": f"Synthesis failed: {str(e)}"}],
                "suggestions": [{"error": f"Synthesis failed: {str(e)}"}],
                "error_messages": state.get("error_messages", []) + [f"Synthesis: {str(e)}"],
                "workflow_status": "synthesis_error"
            }
    
    async def generate_documentation_node(self, state: CodeReviewState) -> CodeReviewState:
        """Generate comprehensive documentation for the code."""
        logger.info("📝 Generating documentation...")
        
        try:
            prompt = f"""
            Generate comprehensive documentation for this {state['language']} code:
            
            ```{state['language']}
            {state['code']}
            ```
            
            Based on the analysis findings, create:
            
            1. **Overview**: What does this code do?
            2. **Architecture**: High-level design and structure
            3. **API Documentation**: Functions, classes, methods with parameters and return values
            4. **Usage Examples**: How to use the code
            5. **Configuration**: Any configuration options
            6. **Dependencies**: External libraries and requirements
            7. **Error Handling**: How errors are handled
            8. **Performance Notes**: Important performance considerations
            9. **Security Notes**: Security considerations and requirements
            10. **Maintenance Guide**: How to maintain and extend the code
            
            Format as proper {state['language']} documentation (docstrings, comments, etc.)
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            return {
                **state,
                "documentation": response.content,
                "workflow_status": "documentation_complete"
            }
            
        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            return {
                **state,
                "documentation": f"Documentation generation failed: {str(e)}",
                "error_messages": state.get("error_messages", []) + [f"Documentation: {str(e)}"],
                "workflow_status": "documentation_error"
            }
    
    async def create_executive_summary_node(self, state: CodeReviewState) -> CodeReviewState:
        """Create executive summary and action plan."""
        logger.info("📊 Creating executive summary...")
        
        try:
            prompt = f"""
            Create an executive summary based on the comprehensive code review:
            
            ORIGINAL CODE ({state['language']}):
            {state['code'][:500]}{'...' if len(state['code']) > 500 else ''}
            
            KEY FINDINGS:
            - Structure: {state.get('structure_analysis', 'N/A')[:200]}...
            - Security: {state.get('security_analysis', 'N/A')[:200]}...
            - Performance: {state.get('performance_analysis', 'N/A')[:200]}...
            - Maintainability: {state.get('maintainability_analysis', 'N/A')[:200]}...
            
            Create an executive summary with:
            
            1. **Overall Assessment**: 
               - Code quality rating (1-10)
               - Production readiness (Ready/Needs Work/Major Issues)
               - Risk level (Low/Medium/High/Critical)
            
            2. **Top 5 Priority Actions**:
               - List the most important things to fix/improve
               - Include estimated effort and impact
            
            3. **Effort Estimation**:
               - Time to address critical issues
               - Time for recommended improvements
               - Resource requirements
            
            4. **Risk Assessment**:
               - What could go wrong if deployed as-is
               - Mitigation strategies
            
            5. **Recommendations**:
               - Next steps
               - Long-term improvements
               - Process recommendations
            
            Keep it concise but comprehensive - suitable for technical leadership.
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            # Extract priority actions (simplified - in production, we'd parse properly)
            priority_actions = [
                "Review and address security vulnerabilities",
                "Optimize performance bottlenecks", 
                "Improve code documentation",
                "Refactor complex functions",
                "Add comprehensive tests"
            ]
            
            return {
                **state,
                "executive_summary": response.content,
                "priority_actions": priority_actions,
                "effort_estimate": "2-4 weeks for critical issues, 1-2 months for full improvements",
                "workflow_status": "complete"
            }
            
        except Exception as e:
            logger.error(f"Executive summary failed: {e}")
            return {
                **state,
                "executive_summary": f"Summary generation failed: {str(e)}",
                "priority_actions": ["Fix workflow errors"],
                "effort_estimate": "Unknown due to analysis errors",
                "error_messages": state.get("error_messages", []) + [f"Executive summary: {str(e)}"],
                "workflow_status": "summary_error"
            }
    
    def create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(CodeReviewState)
        
        # Add nodes
        workflow.add_node("analyze_structure", self.analyze_structure_node)
        workflow.add_node("analyze_security", self.analyze_security_node)
        workflow.add_node("analyze_performance", self.analyze_performance_node)
        workflow.add_node("analyze_maintainability", self.analyze_maintainability_node)
        workflow.add_node("synthesize_findings", self.synthesize_findings_node)
        workflow.add_node("generate_documentation", self.generate_documentation_node)
        workflow.add_node("create_summary", self.create_executive_summary_node)
        
        # Define the flow
        workflow.set_entry_point("analyze_structure")
        workflow.add_edge("analyze_structure", "analyze_security")
        workflow.add_edge("analyze_security", "analyze_performance")
        workflow.add_edge("analyze_performance", "analyze_maintainability")
        workflow.add_edge("analyze_maintainability", "synthesize_findings")
        workflow.add_edge("synthesize_findings", "generate_documentation")
        workflow.add_edge("generate_documentation", "create_summary")
        workflow.add_edge("create_summary", END)
        
        return workflow.compile()
    
    async def review_code(
        self, 
        code: str, 
        language: str, 
        context: Optional[str] = None
    ) -> CodeReviewState:
        """
        Run the complete code review workflow.
        
        Args:
            code: The code to review
            language: Programming language
            context: Additional context about the code
            
        Returns:
            Complete review results
        """
        logger.info(f"Starting code review for {language} code ({len(code)} characters)")
        
        # Initial state
        initial_state: CodeReviewState = {
            "code": code,
            "language": language,
            "context": context,
            "structure_analysis": "",
            "security_analysis": "",
            "performance_analysis": "",
            "maintainability_analysis": "",
            "issues": [],
            "suggestions": [],
            "documentation": "",
            "refactored_code": "",
            "executive_summary": "",
            "priority_actions": [],
            "effort_estimate": "",
            "workflow_status": "starting",
            "error_messages": []
        }
        
        try:
            # Create and run workflow
            app = self.create_workflow()
            result = await app.ainvoke(initial_state)
            
            logger.info(f"Code review completed with status: {result.get('workflow_status')}")
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                **initial_state,
                "workflow_status": "failed",
                "error_messages": [f"Workflow execution failed: {str(e)}"],
                "executive_summary": f"Code review failed due to workflow error: {str(e)}"
            }


# Convenience function for easy usage
async def review_code_async(
    code: str, 
    language: str, 
    context: Optional[str] = None
) -> CodeReviewState:
    """
    Convenience function to run code review.
    
    Args:
        code: Code to review
        language: Programming language
        context: Additional context
        
    Returns:
        Review results
    """
    workflow = CodeReviewWorkflow()
    return await workflow.review_code(code, language, context)
