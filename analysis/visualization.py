import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any, List

class TaktVisualization:
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3

    def create_takt_timeline(self, data: pd.DataFrame) -> go.Figure:
        """
        Create a Gantt chart showing TAKT timeline
        """
        fig = px.timeline(
            data,
            x_start="Start",
            x_end="End",
            y="Task",
            color="Phase",
            title="TAKT Timeline"
        )
        
        fig.update_layout(
            xaxis_title="Timeline",
            yaxis_title="Work Packages",
            showlegend=True
        )
        
        return fig

    def create_resource_heatmap(self, data: pd.DataFrame) -> go.Figure:
        """
        Create a heatmap showing resource utilization across time and zones
        """
        fig = px.imshow(
            data,
            title="Resource Utilization Heatmap",
            labels=dict(x="Time Period", y="Work Zone", color="Utilization %")
        )
        
        fig.update_layout(
            xaxis_title="Time Periods",
            yaxis_title="Work Zones"
        )
        
        return fig

    def create_performance_dashboard(self, metrics: Dict[str, Any]) -> List[go.Figure]:
        """
        Create a set of visualizations for performance metrics
        """
        figures = []
        
        # TAKT Adherence Chart
        takt_adherence = pd.DataFrame(metrics['takt_adherence'])
        fig1 = px.line(
            takt_adherence,
            x="Date",
            y="Adherence",
            title="TAKT Time Adherence"
        )
        figures.append(fig1)
        
        # Resource Utilization
        resource_util = pd.DataFrame(metrics['resource_utilization'])
        fig2 = px.bar(
            resource_util,
            x="Resource",
            y="Utilization",
            title="Resource Utilization"
        )
        figures.append(fig2)
        
        # Efficiency Trends
        efficiency = pd.DataFrame(metrics['efficiency_trends'])
        fig3 = px.line(
            efficiency,
            x="Week",
            y="Efficiency",
            title="Weekly Efficiency Trends"
        )
        figures.append(fig3)
        
        return figures

    def create_risk_visualization(self, risk_data: Dict[str, Any]) -> go.Figure:
        """
        Create a risk matrix visualization
        """
        fig = go.Figure()
        
        # Add risk points
        fig.add_trace(go.Scatter(
            x=risk_data['probability'],
            y=risk_data['impact'],
            mode='markers+text',
            text=risk_data['risk_name'],
            textposition="top center",
            marker=dict(
                size=15,
                color=risk_data['risk_score'],
                colorscale='RdYlGn_r',
                showscale=True
            )
        ))
        
        # Update layout
        fig.update_layout(
            title="Risk Assessment Matrix",
            xaxis_title="Probability",
            yaxis_title="Impact",
            xaxis=dict(range=[0, 1]),
            yaxis=dict(range=[0, 1])
        )
        
        return fig

    def create_progress_tracking(self, progress_data: pd.DataFrame) -> go.Figure:
        """
        Create a visualization for tracking project progress
        """
        fig = go.Figure()
        
        # Actual progress line
        fig.add_trace(go.Scatter(
            x=progress_data['Date'],
            y=progress_data['Actual'],
            name='Actual Progress',
            line=dict(color='blue')
        ))
        
        # Planned progress line
        fig.add_trace(go.Scatter(
            x=progress_data['Date'],
            y=progress_data['Planned'],
            name='Planned Progress',
            line=dict(color='green', dash='dash')
        ))
        
        fig.update_layout(
            title="Project Progress Tracking",
            xaxis_title="Date",
            yaxis_title="Progress (%)",
            yaxis=dict(range=[0, 100])
        )
        
        return fig

    def create_workflow_diagram(self, workflow_data: Dict[str, Any]) -> go.Figure:
        """
        Create a Sankey diagram for workflow visualization
        """
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=workflow_data['nodes'],
                color=self.color_palette[:len(workflow_data['nodes'])]
            ),
            link=dict(
                source=workflow_data['source'],
                target=workflow_data['target'],
                value=workflow_data['values']
            )
        )])
        
        fig.update_layout(
            title="TAKT Workflow Diagram",
            font_size=12
        )
        
        return fig
