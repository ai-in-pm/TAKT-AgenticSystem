from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Any

class TaktAgent(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.name = config['name']
        self.expertise = config['expertise']
        self.api_key = config['api_key']
        self.model = config['model']
        self.logger = logging.getLogger(self.name)

    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the given context and provide recommendations"""
        pass

    @abstractmethod
    def validate(self, analysis: Dict[str, Any]) -> bool:
        """Validate the analysis results"""
        pass

    def chain_of_thought(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement the Chain of Thought reasoning process
        Returns structured analysis with reasoning steps
        """
        self.logger.info(f"Starting Chain of Thought analysis for {self.name}")
        
        # Common CoT steps for all agents
        analysis = {
            'agent_name': self.name,
            'expertise': self.expertise,
            'context': context,
            'reasoning_steps': [],
            'conclusions': [],
            'recommendations': [],
            'validation': {},
            'cross_validation_needed': True
        }
        
        return analysis

    def cross_validate(self, other_agents: List['TaktAgent'], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-validate analysis with other agents"""
        validated_analysis = analysis.copy()
        validated_analysis['cross_validation_results'] = []
        
        for agent in other_agents:
            if agent.name != self.name:
                validation = agent.validate(analysis)
                validated_analysis['cross_validation_results'].append({
                    'validator': agent.name,
                    'validated': validation
                })
        
        return validated_analysis
