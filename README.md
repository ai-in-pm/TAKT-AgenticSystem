# TAKT AI Planning System

A sophisticated AI-powered system for implementing and managing TAKT planning in construction and manufacturing projects. The system utilizes six specialized AI agents, each with Ph.D.-level expertise in different aspects of TAKT planning.

## 🤖 AI Agents

1. **Dr. TAKT Strategy Architect**
   - Portfolio & Enterprise-Level TAKT Implementation
   - Strategic alignment and business objectives
   - High-level TAKT roadmap development

2. **Dr. Workflow Optimization Specialist**
   - Process efficiency & flow synchronization
   - Bottleneck identification and resolution
   - Workflow simulation and optimization

3. **Dr. TAKT Scheduling & Resource Engineer**
   - Advanced scheduling and resource allocation
   - TAKT time calculations and optimization
   - Resource leveling and optimization

4. **Dr. AI-Driven TAKT Data Analyst**
   - Predictive analytics & AI optimization
   - Performance pattern analysis
   - Data-driven decision support

5. **Dr. Risk & Variability Controller**
   - TAKT risk management & adaptability
   - Variability analysis and control
   - Contingency planning

6. **Dr. Implementation & Training Specialist**
   - TAKT adoption & change management
   - Training program development
   - Implementation support

## 🚀 Features

- **Chain of Thought (CoT) Reasoning**
  - Step-by-step logical analysis
  - Transparent decision-making process
  - Cross-validation between agents

- **Interactive UI**
  - Project dashboard
  - Real-time analytics
  - Performance monitoring
  - Training modules

- **Advanced Analytics**
  - Predictive modeling
  - Resource optimization
  - Risk assessment
  - Performance tracking

## 📊 Visualization Components

- TAKT timeline visualization
- Resource utilization heatmaps
- Performance dashboards
- Risk matrices
- Workflow diagrams

## 🛠️ Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd TAKT-AgenticSystem
```

2. Create and activate virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with the following API keys:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
COHERE_API_KEY=your_key_here
EMERGENCEAI_API_KEY=your_key_here
```

## 🚀 Usage

1. Start the UI:
```bash
cd ui
streamlit run app.py
```

2. Navigate to the different sections:
   - Dashboard
   - Project Analysis
   - TAKT Planning
   - Reports
   - Training

## 📁 Project Structure

```
TAKT-AgenticSystem/
├── agents/
│   ├── base_agent.py
│   ├── strategy_architect.py
│   ├── workflow_specialist.py
│   ├── scheduling_engineer.py
│   ├── data_analyst.py
│   ├── risk_controller.py
│   └── implementation_specialist.py
├── analysis/
│   ├── data_processor.py
│   └── visualization.py
├── ui/
│   └── app.py
├── config.py
├── orchestrator.py
├── requirements.txt
└── README.md
```

## 📈 Sample Templates

### TAKT Planning Template
```python
project_template = {
    'project_info': {
        'name': 'Project Name',
        'type': 'Construction/Manufacturing',
        'size': 'Project Size',
        'duration': 'Expected Duration'
    },
    'takt_parameters': {
        'available_time': 'Working hours per day',
        'customer_demand': 'Units per day',
        'work_packages': ['Package 1', 'Package 2', ...]
    }
}
```

### Risk Assessment Template
```python
risk_template = {
    'risk_categories': ['Weather', 'Supply Chain', 'Labor', 'Technical'],
    'impact_levels': ['Low', 'Medium', 'High'],
    'mitigation_strategies': {
        'category': 'Strategy description',
        'contingency_plan': 'Backup plan details'
    }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude
- Google for Gemini
- Groq for inference optimization
- Cohere for NLP capabilities
- EmergenceAI for specialized AI features
