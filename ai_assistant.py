import json
import os
import logging
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-openai-api-key")
openai = OpenAI(api_key=OPENAI_API_KEY)

class ToolieAI:
    def __init__(self):
        self.customer_context = """
        You are Toolie, the AI assistant for Kynetik Electric, a professional electrical contracting company.
        You help customers with:
        - Understanding electrical services (Industrial Installs, 3D LiDAR Scans, Troubleshooting)
        - Guiding them through bid requests
        - Explaining electrical concepts in simple terms
        - Providing quick estimates and recommendations
        - Directing them to appropriate services
        
        Always be professional, helpful, and safety-focused. If you're unsure about electrical safety,
        always recommend consulting a licensed electrician.
        """
        
        self.operator_context = """
        You are Toolie, the AI assistant for Kynetik Electric operators.
        You help with:
        - Technical electrical calculations (conduit fill, load calculations, etc.)
        - Code references and compliance
        - Troubleshooting guidance for technicians
        - Quick quotes and estimates
        - Form completion assistance
        - Project planning and material lists
        
        Provide detailed technical information appropriate for licensed electricians.
        """

    def get_response(self, message, context="customer-facing", conversation_history=None):
        """
        Get AI response from Toolie
        
        Args:
            message (str): User's message
            context (str): Either 'customer-facing' or 'solo-operator'
            conversation_history (list): Previous messages for context
        
        Returns:
            str: AI response
        """
        try:
            system_prompt = self.customer_context if context == "customer-facing" else self.operator_context
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if provided
            if conversation_history:
                for hist in conversation_history[-5:]:  # Keep last 5 exchanges
                    messages.append({"role": "user", "content": hist.get("message", "")})
                    messages.append({"role": "assistant", "content": hist.get("response", "")})
            
            messages.append({"role": "user", "content": message})
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error getting AI response: {e}")
            return "I'm experiencing technical difficulties. Please try again later or contact support directly."

    def generate_quick_quote(self, project_details):
        """
        Generate a quick electrical quote estimate
        
        Args:
            project_details (dict): Project information
        
        Returns:
            dict: Quote estimate with breakdown
        """
        try:
            prompt = f"""
            Based on the following electrical project details, provide a rough estimate breakdown.
            Return your response as JSON with this structure:
            {{
                "estimated_total": number,
                "labor_hours": number,
                "material_cost": number,
                "notes": "explanation of estimate",
                "confidence": "high/medium/low"
            }}
            
            Project Details:
            - Type: {project_details.get('job_type', 'General')}
            - Size: {project_details.get('project_size', 'Unknown')}
            - Description: {project_details.get('description', 'No description')}
            - Location: {project_details.get('location', 'Not specified')}
            
            Consider typical electrical rates, material costs, and complexity.
            """
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Error generating quote: {e}")
            return {
                "estimated_total": 0,
                "labor_hours": 0,
                "material_cost": 0,
                "notes": "Unable to generate estimate. Please request a formal bid.",
                "confidence": "low"
            }

    def analyze_troubleshooting_issue(self, issue_description, symptoms):
        """
        Analyze electrical troubleshooting issues and provide guidance
        
        Args:
            issue_description (str): Description of the electrical issue
            symptoms (list): List of observed symptoms
        
        Returns:
            dict: Troubleshooting analysis and recommendations
        """
        try:
            prompt = f"""
            Analyze this electrical issue and provide troubleshooting guidance.
            Return your response as JSON with this structure:
            {{
                "likely_causes": ["cause1", "cause2"],
                "safety_warnings": ["warning1", "warning2"],
                "diy_steps": ["step1", "step2"],
                "when_to_call_pro": "description",
                "urgency_level": "low/medium/high"
            }}
            
            Issue: {issue_description}
            Symptoms: {', '.join(symptoms) if symptoms else 'None specified'}
            
            Prioritize safety and recommend professional help when appropriate.
            """
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Error analyzing troubleshooting issue: {e}")
            return {
                "likely_causes": ["Unknown issue"],
                "safety_warnings": ["Turn off power and consult a licensed electrician"],
                "diy_steps": ["Contact a professional"],
                "when_to_call_pro": "Immediately - electrical issues can be dangerous",
                "urgency_level": "high"
            }
