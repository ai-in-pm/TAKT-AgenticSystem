import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
EMERGENCEAI_API_KEY = os.getenv('EMERGENCEAI_API_KEY')

# Agent Configuration
AGENT_CONFIGS = {
    'strategy_architect': {
        'name': 'Dr. TAKT Strategy Architect',
        'expertise': 'Portfolio & Enterprise-Level TAKT Implementation',
        'api_key': OPENAI_API_KEY,
        'model': 'gpt-4-turbo'
    },
    'workflow_specialist': {
        'name': 'Dr. Workflow Optimization Specialist',
        'expertise': 'Process Efficiency & Flow Synchronization',
        'api_key': ANTHROPIC_API_KEY,
        'model': 'claude-3'
    },
    'scheduling_engineer': {
        'name': 'Dr. TAKT Scheduling & Resource Engineer',
        'expertise': 'Advanced Scheduling & Resource Allocation',
        'api_key': GROQ_API_KEY,
        'model': 'mixtral-8x7b'
    },
    'data_analyst': {
        'name': 'Dr. AI-Driven TAKT Data Analyst',
        'expertise': 'Predictive Analytics & AI Optimization',
        'api_key': GOOGLE_API_KEY,
        'model': 'gemini-pro'
    },
    'risk_controller': {
        'name': 'Dr. Risk & Variability Controller',
        'expertise': 'TAKT Risk Management & Adaptability',
        'api_key': COHERE_API_KEY,
        'model': 'command'
    },
    'implementation_specialist': {
        'name': 'Dr. Implementation & Training Specialist',
        'expertise': 'TAKT Adoption & Change Management',
        'api_key': EMERGENCEAI_API_KEY,
        'model': 'emergence-latest'
    }
}
