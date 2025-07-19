#!/usr/bin/env python3
"""
AI Assistant for Sannetic Explorer
Uses ChatGPT API for automatic debugging, error fixing, and intelligent calculations
"""

import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging
import requests
from dataclasses import dataclass

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Import configuration manager
try:
    from config_manager import get_config
    config = get_config()
except ImportError:
    print("Warning: Configuration manager not available, using environment variables")
    config = None

from logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

@dataclass
class AIContext:
    """Context information for AI assistant"""
    error_type: str
    error_message: str
    code_context: str
    system_state: Dict[str, Any]
    suggested_fixes: List[str]
    confidence_level: float

class ChatGPTClient:
    """ChatGPT API client for intelligent assistance"""
    
    def __init__(self):
        # Use configuration manager if available
        if config:
            self.api_key = config.get('ai', 'openai_api_key')
            self.model = config.get('ai', 'openai_model', 'gpt-4o-mini')
            self.max_tokens = config.get('ai', 'openai_max_tokens', 2000)
            self.temperature = config.get('ai', 'openai_temperature', 0.1)
        else:
            # Fallback to environment variables
            self.api_key = os.getenv('OPENAI_API_KEY')
            self.model = "gpt-4o-mini"
            self.max_tokens = 2000
            self.temperature = 0.1
        
        self.base_url = "https://api.openai.com/v1"
        
        if not self.api_key:
            logger.warning("⚠️ OpenAI API key not found. AI features will be disabled.")
            logger.info("💡 Set OPENAI_API_KEY in .env file to enable AI assistance")
            if config:
                logger.info("📄 Copy env.example to .env and configure your API keys")
    
    def is_available(self) -> bool:
        """Check if ChatGPT API is available"""
        return bool(self.api_key)
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       system_prompt: Optional[str] = None) -> Optional[str]:
        """Send chat completion request to ChatGPT"""
        if not self.is_available():
            return None
        
        try:
            # Prepare messages
            formatted_messages = []
            
            if system_prompt:
                formatted_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            formatted_messages.extend(messages)
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"ChatGPT API error: {e}")
            return None

class SanneticAI:
    """AI Assistant for Sannetic Explorer with specialized capabilities"""
    
    def __init__(self):
        self.client = ChatGPTClient()
        self.system_prompt = self._get_system_prompt()
        self.error_history = []
        self.fix_success_rate = {}
        
    def _get_system_prompt(self) -> str:
        """Get specialized system prompt for Sannetic Explorer"""
        return """You are an expert AI assistant for Sannetic Explorer, a satellite tracking system. Your expertise includes:

1. **Orbital Mechanics**: TLE data, satellite propagation, Kepler's laws, orbital elements
2. **Python Programming**: Debugging, error fixing, code optimization
3. **API Integration**: Rate limiting, error handling, data validation
4. **Satellite Systems**: GPS, Starlink, ISS, LEO/MEO/GEO orbits
5. **Data Analysis**: JSON processing, error pattern recognition

Your responses should be:
- **Precise and technical** when debugging code
- **Actionable** with specific fix suggestions
- **Educational** explaining the reasoning behind fixes
- **Efficient** focusing on the most likely solutions first

Always provide:
1. Root cause analysis
2. Specific code fixes
3. Prevention strategies
4. Confidence level (0-100%)

Format responses as JSON when providing structured fixes."""

    def analyze_error(self, error_info: Dict[str, Any]) -> AIContext:
        """Analyze error and provide intelligent diagnosis"""
        logger.info("🤖 AI analyzing error...")
        
        try:
            # Prepare error context
            error_context = {
                "error_type": error_info.get("type", "Unknown"),
                "error_message": error_info.get("message", ""),
                "traceback": error_info.get("traceback", ""),
                "code_context": error_info.get("code_context", ""),
                "system_state": error_info.get("system_state", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            # Create analysis prompt
            analysis_prompt = f"""
Analyze this Sannetic Explorer error and provide diagnosis:

ERROR DETAILS:
Type: {error_context['error_type']}
Message: {error_context['error_message']}
Code Context: {error_context['code_context']}

SYSTEM STATE:
{json.dumps(error_context['system_state'], indent=2)}

TRACEBACK:
{error_context['traceback']}

Provide analysis in JSON format:
{{
    "root_cause": "explanation of the underlying issue",
    "error_category": "data_structure|api_error|calculation_error|configuration",
    "suggested_fixes": ["fix1", "fix2", "fix3"],
    "code_changes": ["specific code changes needed"],
    "prevention": "how to prevent this in future",
    "confidence": 85,
    "urgency": "low|medium|high|critical"
}}
"""

            messages = [{"role": "user", "content": analysis_prompt}]
            response = self.client.chat_completion(messages, self.system_prompt)
            
            if response:
                try:
                    # Parse AI response
                    ai_analysis = json.loads(response)
                    
                    context = AIContext(
                        error_type=error_context['error_type'],
                        error_message=error_context['error_message'],
                        code_context=error_context['code_context'],
                        system_state=error_context['system_state'],
                        suggested_fixes=ai_analysis.get('suggested_fixes', []),
                        confidence_level=ai_analysis.get('confidence', 0) / 100.0
                    )
                    
                    logger.info(f"🎯 AI diagnosis complete (confidence: {ai_analysis.get('confidence', 0)}%)")
                    logger.info(f"🔍 Root cause: {ai_analysis.get('root_cause', 'Unknown')}")
                    
                    return context
                    
                except json.JSONDecodeError:
                    logger.warning("⚠️ AI response was not valid JSON, using fallback analysis")
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
        
        # Fallback analysis
        return self._fallback_analysis(error_info)
    
    def _fallback_analysis(self, error_info: Dict[str, Any]) -> AIContext:
        """Fallback error analysis when AI is not available"""
        error_message = error_info.get("message", "")
        
        # Pattern-based analysis
        suggested_fixes = []
        confidence = 0.3
        
        if "NoneType" in error_message:
            suggested_fixes = [
                "Add null checks before accessing object attributes",
                "Validate data structure before processing",
                "Check API response for empty/null data"
            ]
            confidence = 0.7
        elif "string indices must be integers" in error_message:
            suggested_fixes = [
                "Check data type - expecting dict but got string",
                "Validate JSON parsing was successful",
                "Add type checking before dictionary access"
            ]
            confidence = 0.8
        elif "404" in error_message:
            suggested_fixes = [
                "Check API endpoint URL",
                "Verify NORAD ID exists",
                "Update API parameters"
            ]
            confidence = 0.6
        
        return AIContext(
            error_type=error_info.get("type", "Unknown"),
            error_message=error_message,
            code_context=error_info.get("code_context", ""),
            system_state=error_info.get("system_state", {}),
            suggested_fixes=suggested_fixes,
            confidence_level=confidence
        )
    
    def suggest_fix(self, context: AIContext, code_snippet: str) -> Optional[str]:
        """Suggest specific code fix based on error context"""
        if not self.client.is_available():
            return self._suggest_pattern_fix(context, code_snippet)
        
        logger.info("🛠️ AI generating code fix...")
        
        fix_prompt = f"""
Generate a specific code fix for this Sannetic Explorer error:

ERROR CONTEXT:
- Type: {context.error_type}
- Message: {context.error_message}
- Suggested fixes: {', '.join(context.suggested_fixes)}

CURRENT CODE:
```python
{code_snippet}
```

Provide ONLY the corrected code with:
1. Proper error handling
2. Data validation
3. Clear comments explaining the fix
4. Maintain the same function signature

Return only the corrected Python code, no explanations.
"""

        messages = [{"role": "user", "content": fix_prompt}]
        response = self.client.chat_completion(messages, self.system_prompt)
        
        if response:
            logger.info("✅ AI code fix generated")
            return response
        
        return self._suggest_pattern_fix(context, code_snippet)
    
    def _suggest_pattern_fix(self, context: AIContext, code_snippet: str) -> str:
        """Pattern-based code fix suggestions"""
        if "NoneType" in context.error_message:
            return f"""# Fixed version with null checks
{code_snippet}

# Add before problematic line:
if data is not None and isinstance(data, dict):
    # Your original code here
    pass
else:
    logger.warning("Data is None or not a dictionary")
    return None
"""
        
        return f"# Add error handling around:\n{code_snippet}\n\n# Consider adding try-catch and data validation"
    
    def calculate_orbital_parameters(self, tle_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use AI to calculate complex orbital parameters"""
        if not self.client.is_available():
            return None
        
        logger.info("🧮 AI calculating orbital parameters...")
        
        calculation_prompt = f"""
Calculate advanced orbital parameters from this TLE data:

TLE DATA:
{json.dumps(tle_data, indent=2)}

Calculate and return JSON with:
{{
    "orbital_period_hours": "calculated orbital period",
    "apogee_km": "highest point of orbit",
    "perigee_km": "lowest point of orbit",
    "orbital_velocity_kmh": "average orbital velocity",
    "ground_track_repeat_cycle": "ground track repeat pattern",
    "eclipse_duration_minutes": "estimated eclipse duration per orbit",
    "orbital_decay_rate": "estimated decay rate in km/day",
    "next_perigee_time": "estimated next perigee passage",
    "visibility_windows": "optimal viewing times",
    "collision_risk_assessment": "low|medium|high based on orbital debris"
}}

Use standard orbital mechanics formulas. Provide only the JSON response.
"""

        messages = [{"role": "user", "content": calculation_prompt}]
        response = self.client.chat_completion(messages, self.system_prompt)
        
        if response:
            try:
                calculations = json.loads(response)
                logger.info("✅ AI orbital calculations complete")
                return calculations
            except json.JSONDecodeError:
                logger.warning("⚠️ AI calculation response was not valid JSON")
        
        return None
    
    def optimize_api_strategy(self, current_usage: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get AI recommendations for API optimization"""
        if not self.client.is_available():
            return None
        
        logger.info("⚡ AI optimizing API strategy...")
        
        optimization_prompt = f"""
Analyze current API usage and suggest optimizations:

CURRENT USAGE:
{json.dumps(current_usage, indent=2)}

Provide optimization strategy in JSON:
{{
    "priority_changes": ["most important optimizations"],
    "rate_limit_adjustments": {{"api_name": "new_rate_limit"}},
    "caching_improvements": ["caching strategy suggestions"],
    "batch_optimizations": ["batch processing improvements"],
    "error_reduction": ["strategies to reduce API errors"],
    "cost_savings": "estimated percentage savings",
    "implementation_priority": "high|medium|low"
}}

Focus on reducing API calls while maintaining data quality.
"""

        messages = [{"role": "user", "content": optimization_prompt}]
        response = self.client.chat_completion(messages, self.system_prompt)
        
        if response:
            try:
                optimizations = json.loads(response)
                logger.info("✅ AI optimization strategy complete")
                return optimizations
            except json.JSONDecodeError:
                logger.warning("⚠️ AI optimization response was not valid JSON")
        
        return None
    
    def debug_satellite_data(self, satellite_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Debug satellite data quality and suggest improvements"""
        logger.info(f"🔍 AI debugging satellite data for {satellite_name}...")
        
        # Analyze data quality
        issues = []
        suggestions = []
        
        # Check for missing data
        if data.get('dataSources', {}).get('celestrak') == "noValue":
            issues.append("Missing TLE data from Celestrak")
            suggestions.append("Fetch fresh TLE data using satellite NORAD ID")
        
        # Check TLE freshness
        celestrak_data = data.get('dataSources', {}).get('celestrak', {})
        if isinstance(celestrak_data, dict) and 'data' in celestrak_data:
            tle_data = celestrak_data['data']
            if isinstance(tle_data, dict) and 'EPOCH' in tle_data:
                try:
                    epoch = datetime.fromisoformat(tle_data['EPOCH'].replace('Z', '+00:00'))
                    age_days = (datetime.now() - epoch).days
                    if age_days > 7:
                        issues.append(f"TLE data is {age_days} days old")
                        suggestions.append("Update TLE data for better accuracy")
                except:
                    issues.append("Invalid TLE epoch format")
                    suggestions.append("Validate and reformat TLE epoch")
        
        # Check for data structure issues
        if not isinstance(data.get('orbit', {}), dict):
            issues.append("Invalid orbit data structure")
            suggestions.append("Rebuild orbit data from TLE")
        
        # AI analysis if available
        ai_suggestions = []
        if self.client.is_available():
            debug_prompt = f"""
Analyze this satellite data for {satellite_name} and identify issues:

DATA:
{json.dumps(data, indent=2)[:1000]}...

Identify:
1. Data quality issues
2. Missing critical information
3. Structural problems
4. Suggestions for improvement

Return JSON with specific actionable recommendations.
"""
            
            messages = [{"role": "user", "content": debug_prompt}]
            response = self.client.chat_completion(messages, self.system_prompt)
            
            if response:
                try:
                    ai_analysis = json.loads(response)
                    ai_suggestions = ai_analysis.get('suggestions', [])
                except:
                    pass
        
        return {
            "satellite": satellite_name,
            "issues_found": issues,
            "suggestions": suggestions + ai_suggestions,
            "data_quality_score": max(0, 100 - len(issues) * 20),
            "ai_analyzed": self.client.is_available()
        }
    
    def auto_fix_error(self, error_info: Dict[str, Any], 
                      code_file: Optional[str] = None) -> Dict[str, Any]:
        """Automatically analyze and suggest fixes for errors"""
        logger.info("🔧 AI auto-fixing error...")
        
        # Analyze the error
        context = self.analyze_error(error_info)
        
        # Generate fix if code is provided
        suggested_code = None
        if code_file and Path(code_file).exists():
            try:
                with open(code_file, 'r') as f:
                    code_content = f.read()
                suggested_code = self.suggest_fix(context, code_content)
            except Exception as e:
                logger.error(f"Error reading code file: {e}")
        
        # Record this error for learning
        self.error_history.append({
            "timestamp": datetime.now().isoformat(),
            "error_type": context.error_type,
            "confidence": context.confidence_level,
            "suggested_fixes": context.suggested_fixes
        })
        
        return {
            "analysis": {
                "error_type": context.error_type,
                "confidence": context.confidence_level,
                "suggested_fixes": context.suggested_fixes
            },
            "code_fix": suggested_code,
            "prevention_tips": [
                "Add comprehensive error handling",
                "Validate data types before processing",
                "Use defensive programming practices",
                "Implement proper logging for debugging"
            ],
            "ai_available": self.client.is_available()
        }


# Global AI assistant instance
ai_assistant = SanneticAI()

def handle_error_with_ai(func):
    """Decorator to automatically handle errors with AI assistance"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = {
                "type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc(),
                "function": func.__name__,
                "args": str(args)[:200],  # Limit length
                "kwargs": str(kwargs)[:200]
            }
            
            # Get AI assistance
            fix_result = ai_assistant.auto_fix_error(error_info)
            
            logger.error(f"❌ Error in {func.__name__}: {e}")
            logger.info(f"🤖 AI Confidence: {fix_result['analysis']['confidence']:.1%}")
            logger.info("💡 AI Suggestions:")
            for suggestion in fix_result['analysis']['suggested_fixes'][:3]:
                logger.info(f"   • {suggestion}")
            
            # Re-raise the original exception
            raise
    
    return wrapper

def get_ai_orbital_analysis(satellite_name: str, tle_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get comprehensive AI analysis of satellite orbital characteristics"""
    logger.info(f"🛰️ Getting AI orbital analysis for {satellite_name}...")
    
    if not ai_assistant.client.is_available():
        logger.warning("⚠️ AI not available for orbital analysis")
        return None
    
    # Calculate orbital parameters
    calculations = ai_assistant.calculate_orbital_parameters(tle_data)
    
    if calculations:
        logger.info("✅ AI orbital analysis complete")
        return {
            "satellite": satellite_name,
            "timestamp": datetime.now().isoformat(),
            "calculations": calculations,
            "confidence": "high",
            "source": "ChatGPT-4"
        }
    
    return None

def main():
    """Test AI assistant capabilities"""
    logger.info("🤖 Testing Sannetic Explorer AI Assistant")
    
    # Test availability
    if ai_assistant.client.is_available():
        logger.info("✅ ChatGPT API available")
        
        # Test error analysis
        test_error = {
            "type": "AttributeError",
            "message": "'NoneType' object has no attribute 'get'",
            "traceback": "Traceback (most recent call last)...",
            "code_context": "celestrak_data = satellite_data.get('dataSources', {}).get('celestrak')",
            "system_state": {"satellites_loaded": 29, "api_calls_made": 5}
        }
        
        fix_result = ai_assistant.auto_fix_error(test_error)
        logger.info(f"🎯 AI analysis confidence: {fix_result['analysis']['confidence']:.1%}")
        logger.info("💡 AI suggestions:")
        for suggestion in fix_result['analysis']['suggested_fixes']:
            logger.info(f"   • {suggestion}")
        
        # Test satellite data debugging
        test_data = {
            "name": "Test Satellite",
            "dataSources": {"celestrak": "noValue"},
            "orbit": {}
        }
        
        debug_result = ai_assistant.debug_satellite_data("Test Satellite", test_data)
        logger.info(f"🔍 Data quality score: {debug_result['data_quality_score']}/100")
        logger.info(f"📋 Issues found: {len(debug_result['issues_found'])}")
        
    else:
        logger.warning("⚠️ ChatGPT API not available")
        logger.info("💡 Set OPENAI_API_KEY to enable AI features")
        
        # Test fallback analysis
        test_error = {
            "type": "AttributeError", 
            "message": "'NoneType' object has no attribute 'get'"
        }
        
        context = ai_assistant._fallback_analysis(test_error)
        logger.info(f"🔧 Fallback analysis confidence: {context.confidence_level:.1%}")
        logger.info("💡 Pattern-based suggestions:")
        for suggestion in context.suggested_fixes:
            logger.info(f"   • {suggestion}")

if __name__ == "__main__":
    main() 