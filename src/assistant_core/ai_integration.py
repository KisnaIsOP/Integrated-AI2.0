from typing import List, Dict, Any, Optional, Tuple
import os
import openai
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import logging
from datetime import datetime
from enum import Enum
import re
from .weather_service import WeatherService
from .memory_manager import MemoryManager
from .system_controller import SystemController
from .context_manager import ContextManager
import time

# Load environment variables
load_dotenv()

class CommandType(Enum):
    SYSTEM = "system"
    APPLICATION = "application"
    FILE = "file"
    NETWORK = "network"
    SETTINGS = "settings"
    UNKNOWN = "unknown"

class CommandIntent:
    def __init__(self, command_type: CommandType, action: str, parameters: Dict[str, Any], confidence: float):
        self.command_type = command_type
        self.action = action
        self.parameters = parameters
        self.confidence = confidence
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_type": self.command_type.value,
            "action": self.action,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }

class AIIntegration:
    def __init__(self):
        # Initialize API keys and clients
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Initialize components
        self.system_controller = SystemController()
        self.context_manager = ContextManager()
        self.weather_service = WeatherService()
        self.memory_manager = MemoryManager()
        self.logger = logging.getLogger(__name__)
        
        # Enhanced settings
        self.settings = {
            "default_model": "OpenAI",
            "temperature": 0.7,
            "max_context": 10,
            "stream_responses": True,
            "command_confidence_threshold": 0.8,
            "command_patterns": {
                "system": [
                    r"(?i)(check|show|get|display)\s+(system|cpu|memory|disk)\s+(status|info|usage)",
                    r"(?i)(monitor|track)\s+(system|resources|performance)"
                ],
                "application": [
                    r"(?i)(open|launch|start|run|execute)\s+([a-zA-Z0-9\s\-_]+)",
                    r"(?i)(close|stop|exit|quit|terminate)\s+([a-zA-Z0-9\s\-_]+)"
                ],
                "file": [
                    r"(?i)(create|make|new)\s+(?:a\s+)?(?:new\s+)?(file|directory|folder)",
                    r"(?i)(delete|remove|move|copy)\s+(?:the\s+)?(?:file|directory|folder)"
                ]
            },
            "models": {
                "openai": {
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "presence_penalty": 0.0,
                    "frequency_penalty": 0.0
                },
                "gemini": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
        }
        
        # Command history
        self.command_history: List[CommandIntent] = []

    async def analyze_command_intent(self, text: str) -> Optional[CommandIntent]:
        """Analyze command intent with pattern matching and AI verification"""
        text = text.strip().lower()
        
        # Pattern matching
        for cmd_type, patterns in self.settings["command_patterns"].items():
            for pattern in patterns:
                match = re.match(pattern, text)
                if match:
                    params = match.groups()
                    return CommandIntent(
                        CommandType(cmd_type),
                        cmd_type,
                        {"raw_params": params},
                        0.9
                    )
        
        # AI-based intent detection
        try:
            ai_prompt = f"Analyze this text for command intent: {text}"
            ai_response = await self.get_openai_response(ai_prompt)
            
            # Simple parsing (enhance this based on your needs)
            if "system" in ai_response.lower():
                return CommandIntent(CommandType.SYSTEM, "system", {}, 0.7)
            elif "application" in ai_response.lower():
                return CommandIntent(CommandType.APPLICATION, "application", {}, 0.7)
                
        except Exception as e:
            self.logger.error(f"Error in AI intent analysis: {e}")
            
        return None

    async def execute_command_intent(self, intent: CommandIntent) -> Dict[str, Any]:
        """Execute a command based on analyzed intent"""
        if intent.confidence < self.settings["command_confidence_threshold"]:
            return {
                "status": "error",
                "message": f"Command confidence too low: {intent.confidence}"
            }
            
        try:
            if intent.command_type == CommandType.SYSTEM:
                result = await self.system_controller.execute_system_command(
                    intent.action,
                    intent.parameters
                )
            elif intent.command_type == CommandType.APPLICATION:
                result = await self.system_controller.execute_app_command(
                    intent.action,
                    intent.parameters
                )
            else:
                result = {
                    "status": "error",
                    "message": f"Unsupported command type: {intent.command_type}"
                }
            
            if result["status"] == "success":
                self.command_history.append(intent)
                self.context_manager.add_message(
                    "system",
                    f"Executed {intent.command_type.value} command: {intent.action}"
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def process_user_input(self, user_input: str) -> str:
        """Process user input with enhanced command handling"""
        try:
            # Analyze for command intent
            intent = await self.analyze_command_intent(user_input)
            
            if intent and intent.confidence >= self.settings["command_confidence_threshold"]:
                result = await self.execute_command_intent(intent)
                
                if result["status"] == "success":
                    response = f"Executed {intent.command_type.value} command successfully."
                    if "details" in result:
                        response += f"\n{result['details']}"
                else:
                    response = f"Command execution failed: {result['message']}"
                    
                self.context_manager.add_message("user", user_input)
                self.context_manager.add_message("assistant", response)
                return response
            
            # Process as normal conversation
            return await self.get_enhanced_response(user_input)
            
        except Exception as e:
            self.logger.error(f"Error processing user input: {e}")
            return f"Error: {str(e)}"

    def get_command_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent command history"""
        return [cmd.to_dict() for cmd in self.command_history[-limit:]]

    def get_command_statistics(self) -> Dict[str, Any]:
        """Get statistics about command usage"""
        if not self.command_history:
            return {"message": "No commands executed yet"}
            
        stats = {
            "total_commands": len(self.command_history),
            "by_type": {},
            "average_confidence": sum(cmd.confidence for cmd in self.command_history) / len(self.command_history)
        }
        
        for cmd in self.command_history:
            cmd_type = cmd.command_type.value
            stats["by_type"][cmd_type] = stats["by_type"].get(cmd_type, 0) + 1
            
        return stats

    async def get_openai_response(self, prompt: str, include_weather: bool = False) -> str:
        """Get response from OpenAI with enhanced context handling"""
        try:
            # Get conversation context with metadata
            context = self.context_manager.get_context(include_metadata=True)
            
            # Create messages list with system prompt
            messages = [
                {
                    'role': 'system',
                    'content': '''You are an intelligent AI assistant with access to:
                    1. System control and monitoring
                    2. Application management
                    3. Weather information
                    4. Conversation history and context
                    
                    Provide accurate, contextual responses and execute system commands when requested.
                    For system commands, be explicit about the actions you're taking.'''
                }
            ]
            
            # Add context messages
            messages.extend([
                {
                    'role': msg['role'],
                    'content': msg['content'],
                    'metadata': msg.get('metadata', {})
                }
                for msg in context
            ])
            
            # Add current prompt
            messages.append({'role': 'user', 'content': prompt})
            
            # Get relevant system information
            system_info = ""
            if any(keyword in prompt.lower() for keyword in ['system', 'cpu', 'memory', 'disk', 'performance']):
                try:
                    sys_data = self.system_controller.get_system_info()
                    if sys_data:
                        system_info = f"\nSystem Information:\n"
                        system_info += f"CPU Usage: {sys_data['cpu_usage']}%\n"
                        system_info += f"Memory Used: {sys_data['memory_used']}%\n"
                        system_info += f"Disk Used: {sys_data['disk_used']}%"
                except Exception as e:
                    self.logger.error(f"Error getting system info: {e}")
            
            # Get weather if requested
            weather_info = ""
            if include_weather and "weather" in prompt.lower():
                try:
                    city = self._extract_city_from_prompt(prompt)
                    if city:
                        weather_data = self.weather_service.get_weather(city)
                        if weather_data and 'error' not in weather_data:
                            weather_info = f"\nWeather in {weather_data['city']}:\n"
                            weather_info += f"Temperature: {weather_data['temperature']}°C\n"
                            weather_info += f"Description: {weather_data['description']}\n"
                            weather_info += f"Humidity: {weather_data['humidity']}%"
                except Exception as e:
                    self.logger.error(f"Error getting weather info: {e}")
            
            # Add additional context if available
            if system_info or weather_info:
                messages.append({
                    'role': 'system',
                    'content': f"{system_info}\n{weather_info}".strip()
                })
            
            # Get response with enhanced parameters
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.settings["models"]["openai"]["model"],
                messages=messages,
                temperature=self.settings["models"]["openai"]["temperature"],
                max_tokens=self.settings["models"]["openai"]["max_tokens"],
                presence_penalty=self.settings["models"]["openai"]["presence_penalty"],
                frequency_penalty=self.settings["models"]["openai"]["frequency_penalty"]
            )
            
            response_text = response.choices[0].message.content
            
            # Check for potential commands in response
            if any(keyword in prompt.lower() for keyword in ['open', 'launch', 'start', 'run', 'execute', 'system']):
                try:
                    intent = await self.analyze_command_intent(response_text)
                    if intent and intent.confidence >= self.settings["command_confidence_threshold"]:
                        result = await self.execute_command_intent(intent)
                        response_text += f"\n\nAction taken: {result.get('message', '')}"
                except Exception as e:
                    self.logger.error(f"Error handling command in response: {e}")
            
            # Update context
            await self.context_manager.add_message(
                "user",
                prompt,
                metadata={"has_command": bool(intent) if 'intent' in locals() else False}
            )
            await self.context_manager.add_message(
                "assistant",
                response_text,
                metadata={"command_executed": bool(result) if 'result' in locals() else False}
            )
            
            return response_text
            
        except Exception as e:
            error_msg = f"OpenAI Error: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    async def get_gemini_response(self, prompt: str, include_weather: bool = False) -> str:
        """Get response from Gemini with enhanced context handling"""
        try:
            # Add weather context if requested
            if include_weather:
                city = self._extract_city_from_prompt(prompt)
                if city:
                    weather_info = await self.weather_service.get_weather(city)
                    prompt = f"Weather in {city}: {weather_info}\n\nUser query: {prompt}"
            
            # Get response from Gemini
            response = self.gemini_model.generate_content(prompt)
            
            # Extract text from response
            if hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
            
        except Exception as e:
            error_msg = f"Gemini Error: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    async def combine_responses(self, responses: List[str]) -> str:
        """Combine and synthesize responses from different AI models"""
        # Remove error messages
        valid_responses = [r for r in responses if not (r.startswith("OpenAI Error:") or r.startswith("Gemini Error:"))]
        
        if not valid_responses:
            return "Error: No valid responses from AI models."
        
        # If we only got one valid response, return it
        if len(valid_responses) == 1:
            return valid_responses[0]
        
        # Combine multiple responses
        combined = "\n\nCombined AI Response:\n"
        for i, response in enumerate(valid_responses, 1):
            combined += f"\nPerspective {i}:\n{response}\n"
        
        return combined

    async def get_enhanced_response(self, prompt: str) -> str:
        """Get enhanced response combining both AI models"""
        responses = []
        include_weather = "weather" in prompt.lower()
        
        # Get responses from available models
        if self.openai_api_key:
            try:
                openai_response = await self.get_openai_response(prompt, include_weather)
                responses.append(openai_response)
            except Exception as e:
                self.logger.error(f"OpenAI Error: {str(e)}")
        
        if self.gemini_api_key:
            try:
                gemini_response = await self.get_gemini_response(prompt, include_weather)
                responses.append(gemini_response)
            except Exception as e:
                self.logger.error(f"Gemini Error: {str(e)}")
        
        if not responses:
            return "Error: No API keys configured or all models failed to respond."
        
        # Combine responses
        combined_response = await self.combine_responses(responses)
        
        # Store the interaction in memory
        await self.memory_manager.add_interaction(prompt, combined_response)
        
        return combined_response

    async def get_response(self, prompt: str, model: str = "OpenAI") -> str:
        """Get response from specified model"""
        try:
            # First check if this is a system command
            command_data = self.parse_system_command(prompt)
            if command_data and self.system_controller:
                try:
                    result = self.system_controller.execute_command(command_data)
                    if result.get('status') == 'success':
                        if command_data['command'] == 'system':
                            return f"Here's your system status:\nCPU Usage: {result.get('cpu_usage')}%\nMemory Used: {result.get('memory_used')}%\nDisk Used: {result.get('disk_used')}%"
                        else:
                            return f"I've {command_data['command']}ed {' '.join(command_data['args'])} for you. {result.get('message', '')}"
                    else:
                        return f"Sorry, I couldn't {command_data['command']} {' '.join(command_data['args'])}. {result.get('message', '')}"
                except Exception as e:
                    return f"Error executing command: {str(e)}"

            # If not a system command, get AI response
            try:
                if model.lower() == "openai":
                    return await self.get_openai_response(prompt)
                elif model.lower() == "gemini":
                    return await self.get_gemini_response(prompt)
                else:  # Both
                    responses = await asyncio.gather(
                        self.get_openai_response(prompt),
                        self.get_gemini_response(prompt)
                    )
                    return await self.combine_responses(responses)
            except Exception as e:
                return f"AI Error: {str(e)}"
                
        except Exception as e:
            return f"Error: {str(e)}"

    def parse_system_command(self, text: str) -> Dict[str, Any]:
        """Parse system commands from text"""
        try:
            text = text.lower()
            words = text.split()
            
            # Command patterns
            app_commands = ['open', 'launch', 'start', 'close', 'stop']
            system_commands = ['status', 'info', 'system']
            
            for i, word in enumerate(words):
                # Check for app commands
                if word in app_commands:
                    if i + 1 < len(words):
                        return {
                            "command": word,
                            "target": " ".join(words[i+1:]),
                            "type": "application"
                        }
                        
                # Check for system commands
                elif word in system_commands:
                    return {
                        "command": "status",
                        "type": "system"
                    }
                    
            return None
            
        except Exception as e:
            print(f"Error parsing command: {str(e)}")
            return None

    def get_response_sync(self, prompt: str, model: str = "OpenAI") -> str:
        """Synchronous wrapper for getting response"""
        return asyncio.run(self.get_response(prompt, model))

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and extract key information"""
        # This can be expanded based on your needs
        prompt = f"""Analyze the following text and provide:
        1. Sentiment (positive/negative/neutral)
        2. Key topics
        3. Main intent
        
        Text: {text}"""
        
        response = self.get_response_sync(prompt)
        return {
            'analysis': response,
            'raw_text': text
        }

    async def generate_system_command(self, user_input: str) -> Optional[CommandIntent]:
        """
        Generate system commands based on natural language input with enhanced validation and safety checks.
        
        Args:
            user_input (str): Natural language command from user
            
        Returns:
            Optional[CommandIntent]: Validated command intent or None if generation fails
        """
        try:
            # First try pattern matching
            for cmd_type, patterns in self.settings["command_patterns"].items():
                for pattern in patterns:
                    if re.search(pattern, user_input, re.IGNORECASE):
                        initial_type = cmd_type
                        break
                else:
                    initial_type = CommandType.UNKNOWN
            
            # Generate command using AI
            prompt = f"""Analyze this command and convert to a system operation:
            User Input: {user_input}
            
            Respond in strict JSON format with:
            {{
                "command_type": "system|application|file|network|settings",
                "action": "specific_action",
                "parameters": {{"param1": "value1", ...}},
                "confidence": 0.0 to 1.0,
                "safety_check": "safety considerations",
                "requires_elevation": boolean
            }}"""
            
            response = await self.get_response(prompt)
            
            try:
                result = json.loads(response)
                
                # Validate command structure
                required_fields = ["command_type", "action", "parameters", "confidence"]
                if not all(field in result for field in required_fields):
                    self.logger.warning(f"Missing required fields in command generation: {result}")
                    return None
                
                # Create command intent
                command_type = getattr(CommandType, result["command_type"].upper(), CommandType.UNKNOWN)
                confidence = min(
                    result["confidence"],
                    0.9 if command_type == initial_type else 0.7  # Reduce confidence if type mismatch
                )
                
                # Apply confidence threshold
                if confidence < self.settings["command_confidence_threshold"]:
                    self.logger.info(f"Command confidence {confidence} below threshold")
                    return None
                
                intent = CommandIntent(
                    command_type=command_type,
                    action=result["action"],
                    parameters=result["parameters"],
                    confidence=confidence
                )
                
                # Add to command history
                self.command_history.append(intent)
                
                # Log command generation
                self.logger.info(
                    f"Generated command: type={command_type}, action={result['action']}, "
                    f"confidence={confidence}"
                )
                
                return intent
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse AI response: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating system command: {str(e)}")
            return None

    async def multi_model_response(self, message: str, model_preference: Optional[str] = None, system_commands_enabled: bool = False, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get enhanced responses from multiple AI models with intelligent coordination.
        
        Args:
            message (str): User message to process
            model_preference (Optional[str]): Preferred model to use (e.g., 'gpt-4', 'gpt-3.5-turbo', 'gemini-pro')
            system_commands_enabled (bool): Whether system commands are enabled
            context (Optional[Dict[str, Any]]): Additional context for response generation
            
        Returns:
            Dict[str, Any]: Synthesized response with metadata
        """
        try:
            # Initialize context if not provided
            context = context or {}
            
            # Handle model preference
            if model_preference:
                if model_preference.startswith('gpt'):
                    response = await self.get_openai_response(message)
                    return {"success": True, "response": response}
                elif model_preference == 'gemini-pro':
                    response = await self.get_gemini_response(message)
                    return {"success": True, "response": response}
            
            # If no preference or 'auto', use enhanced response
            response = await self.get_enhanced_response(message)
            
            # Check for system commands if enabled
            if system_commands_enabled:
                intent = await self.analyze_command_intent(message)
                if intent and intent.confidence >= self.settings["command_confidence_threshold"]:
                    result = await self.execute_command_intent(intent)
                    if result["status"] == "success":
                        response += f"\n\nExecuted command: {result.get('message', '')}"
            
            return {
                "success": True,
                "response": response,
                "metadata": {
                    "model": model_preference or "auto",
                    "system_commands": system_commands_enabled
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "model": model_preference or "auto",
                    "system_commands": system_commands_enabled
                }
            }

    async def _analyze_request(self, message: str) -> Dict[str, Any]:
        """
        Analyze the request to determine optimal response strategy.
        
        Args:
            message (str): User message to analyze
            
        Returns:
            Dict[str, Any]: Analysis results including complexity, capabilities, etc.
        """
        prompt = """Analyze this user message and provide response requirements:
        Message: {message}
        
        Respond in JSON format with:
        {
            "complexity": 0-1,
            "required_capabilities": ["capability1", ...],
            "topic_category": "category",
            "response_type": "factual|creative|analytical|procedural",
            "time_sensitivity": 0-1
        }"""
        
        try:
            response = await self.get_response(prompt.format(message=message))
            return json.loads(response)
        except:
            return {
                "complexity": 0.5,
                "required_capabilities": ["general"],
                "topic_category": "general",
                "response_type": "general",
                "time_sensitivity": 0.5
            }
    
    def _select_models(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Select appropriate models based on request analysis.
        
        Args:
            analysis (Dict[str, Any]): Request analysis results
            
        Returns:
            List[str]: List of selected model names
        """
        models = []
        
        # Add OpenAI for complex or analytical tasks
        if (analysis["complexity"] > 0.7 or 
            analysis["response_type"] in ["analytical", "procedural"] or
            "code" in analysis["required_capabilities"]):
            models.append("openai")
        
        # Add Gemini for creative or real-time tasks
        if (analysis["response_type"] == "creative" or
            analysis["time_sensitivity"] > 0.8 or
            "visual" in analysis["required_capabilities"]):
            models.append("gemini")
        
        # Ensure at least one model is selected
        if not models:
            models = ["openai"] if self.openai_client else ["gemini"]
        
        return models
    
    def _generate_model_prompts(self, message: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate optimized prompts for each model.
        
        Args:
            message (str): Original user message
            analysis (Dict[str, Any]): Request analysis results
            context (Dict[str, Any]): Additional context
            
        Returns:
            Dict[str, str]: Model-specific prompts
        """
        base_prompt = f"""Context: {json.dumps(context)}
        Analysis: {json.dumps(analysis)}
        User Message: {message}
        
        Provide a response that is:
        1. {analysis['response_type'].capitalize()} in nature
        2. Addresses the specific capabilities: {', '.join(analysis['required_capabilities'])}
        3. Appropriate for the topic: {analysis['topic_category']}"""
        
        return {
            "openai": base_prompt + "\nOptimize for analytical accuracy and structured output.",
            "gemini": base_prompt + "\nOptimize for real-time relevance and creative insights."
        }
    
    def _assess_response_quality(self, response: str, analysis: Dict[str, Any]) -> float:
        """
        Assess the quality of a response based on multiple factors.
        
        Args:
            response (str): Model response to assess
            analysis (Dict[str, Any]): Original request analysis
            
        Returns:
            float: Quality score between 0 and 1
        """
        score = 1.0
        
        # Length check
        if len(response) < 20:
            score *= 0.5
        elif len(response) > 1000:
            score *= 0.8
        
        # Content relevance (basic checks)
        relevance_keywords = set(analysis["required_capabilities"])
        response_words = set(response.lower().split())
        keyword_overlap = len(relevance_keywords.intersection(response_words))
        score *= (0.5 + min(keyword_overlap / len(relevance_keywords), 0.5))
        
        # Structure check
        has_structure = bool(re.search(r'\n|•|\-|\d\.', response))
        if analysis["response_type"] in ["analytical", "procedural"] and not has_structure:
            score *= 0.7
        
        return min(max(score, 0.0), 1.0)
    
    async def _synthesize_responses(self, responses: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize multiple responses into a coherent final response.
        
        Args:
            responses (List[Dict[str, Any]]): Valid model responses
            analysis (Dict[str, Any]): Original request analysis
            
        Returns:
            Dict[str, Any]: Synthesized response with metadata
        """
        start_time = time.time()
        
        if len(responses) == 1:
            return {
                "response": responses[0]["response"],
                "quality_score": responses[0]["quality_score"],
                "processing_time": time.time() - start_time,
                "confidence": responses[0]["quality_score"]
            }
        
        # Sort by quality score
        responses.sort(key=lambda x: x["quality_score"], reverse=True)
        
        # For high complexity tasks, combine insights
        if analysis["complexity"] > 0.7:
            synthesis_prompt = f"""Synthesize these model responses into a single coherent response:
            
            Responses:
            {json.dumps([r['response'] for r in responses])}
            
            Analysis:
            {json.dumps(analysis)}
            
            Provide a response that combines the best insights while maintaining clarity and coherence."""
            
            try:
                combined = await self.get_response(synthesis_prompt)
                quality_score = self._assess_response_quality(combined, analysis)
                
                return {
                    "response": combined,
                    "quality_score": quality_score,
                    "processing_time": time.time() - start_time,
                    "confidence": sum(r["quality_score"] for r in responses) / len(responses)
                }
            except:
                # Fallback to best response
                return {
                    "response": responses[0]["response"],
                    "quality_score": responses[0]["quality_score"],
                    "processing_time": time.time() - start_time,
                    "confidence": responses[0]["quality_score"]
                }
        
        # For simpler tasks, use the best response
        return {
            "response": responses[0]["response"],
            "quality_score": responses[0]["quality_score"],
            "processing_time": time.time() - start_time,
            "confidence": responses[0]["quality_score"]
        }
    
    def _update_response_stats(self, response: Dict[str, Any]) -> None:
        """
        Update response statistics for monitoring and optimization.
        
        Args:
            response (Dict[str, Any]): Response data including quality metrics
        """
        stats = {
            "timestamp": time.time(),
            "quality_score": response["quality_score"],
            "processing_time": response["processing_time"],
            "confidence": response["confidence"]
        }
        
        # Update rolling statistics
        if not hasattr(self, 'response_stats'):
            self.response_stats = []
        self.response_stats = self.response_stats[-99:] + [stats]  # Keep last 100 responses

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup"""
        await self.cleanup()

    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Save any pending context
            if self.context_manager:
                await self.context_manager.cleanup()
            
            # Save command history
            if self.command_history:
                history_file = "command_history.json"
                with open(history_file, 'w') as f:
                    json.dump(
                        [cmd.to_dict() for cmd in self.command_history],
                        f,
                        indent=2
                    )
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def __del__(self):
        """Ensure cleanup on destruction"""
        try:
            asyncio.run(self.cleanup())
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def _extract_city_from_prompt(self, prompt: str) -> Optional[str]:
        """Extract city name from prompt"""
        # Simple implementation - enhance based on your needs
        words = prompt.lower().split()
        if "in" in words:
            city_index = words.index("in") + 1
            if city_index < len(words):
                return words[city_index].capitalize()
        return None
