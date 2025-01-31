import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import TaktOrchestrator
from services.data_service import TaktDataService

class TaktUI:
    def __init__(self):
        self.orchestrator = TaktOrchestrator()
        self.data_service = TaktDataService()
        self.setup_page()
        
    def setup_page(self):
        st.set_page_config(
            page_title="TAKT AI Planning System",
            page_icon="🏗️",
            layout="wide"
        )
        st.title("TAKT AI Planning System")

    def run(self):
        # Project selector in sidebar
        st.sidebar.header("Project Settings")
        project_id = st.sidebar.selectbox(
            "Select Project",
            ["Project A", "Project B", "Project C"]
        )
        
        # Navigation
        page = st.sidebar.selectbox(
            "Navigation",
            ["Dashboard", "Project Analysis", "TAKT Planning", "Reports", "Training"]
        )
        
        if page == "Dashboard":
            self.show_dashboard(project_id)
        elif page == "Project Analysis":
            self.show_project_analysis(project_id)
        elif page == "TAKT Planning":
            self.show_takt_planning(project_id)
        elif page == "Reports":
            self.show_reports(project_id)
        elif page == "Training":
            self.show_training()

    def show_dashboard(self, project_id: str):
        st.header("Project Dashboard")
        
        # Date range for metrics
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", 
                                     value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", 
                                   value=datetime.now())

        # Get real-time metrics
        metrics = self.data_service.calculate_advanced_metrics(
            start_date=start_date,
            end_date=end_date,
            project_id=project_id
        )
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("TAKT Adherence", 
                     f"{metrics['takt_adherence']['average_adherence']:.1f}%",
                     help="Percentage of tasks completed within TAKT time")
        with col2:
            st.metric("Flow Efficiency", 
                     f"{metrics['flow_efficiency']['flow_efficiency']:.1f}%",
                     help="Ratio of value-added time to total time")
        with col3:
            st.metric("Stability Index", 
                     f"{metrics['takt_adherence']['stability_index']:.1f}%",
                     help="Measure of TAKT time consistency")
        with col4:
            st.metric("Prediction Confidence", 
                     f"{metrics['predictive_metrics']['confidence']:.1f}%",
                     help="Confidence in future performance predictions")

        # TAKT Performance Trends
        st.subheader("TAKT Performance Analysis")
        tabs = st.tabs(["Performance Trends", "Flow Analysis", "Bottleneck Analysis"])
        
        with tabs[0]:
            self.show_performance_trends(project_id, start_date, end_date)
        
        with tabs[1]:
            self.show_flow_analysis(project_id, start_date, end_date)
            
        with tabs[2]:
            self.show_bottleneck_analysis(project_id, start_date, end_date)

    def show_performance_trends(self, project_id: str, start_date: datetime, end_date: datetime):
        # Get performance data
        performance_data = self.data_service.get_performance_metrics(start_date, end_date, project_id)
        
        if performance_data.empty:
            st.warning("No performance data available for the selected time period.")
            return
            
        # Create multi-line chart
        fig = go.Figure()
        
        metrics = ['TAKT_Adherence', 'Flow_Efficiency', 'Resource_Utilization']
        colors = ['blue', 'green', 'red']
        labels = ['TAKT Adherence', 'Flow Efficiency', 'Resource Utilization']
        
        for metric, color, label in zip(metrics, colors, labels):
            if metric in performance_data.columns:
                fig.add_trace(go.Scatter(
                    x=performance_data['timestamp'],
                    y=performance_data[metric],
                    name=label,
                    line=dict(color=color),
                    mode='lines+markers'
                ))
        
        fig.update_layout(
            title="Performance Trends Over Time",
            xaxis_title="Date",
            yaxis_title="Percentage (%)",
            hovermode='x unified',
            showlegend=True,
            yaxis=dict(range=[0, 100])  # Set y-axis range for percentages
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add a data table below the chart
        if st.checkbox("Show Raw Data"):
            st.dataframe(
                performance_data[['timestamp'] + metrics].rename(
                    columns=dict(zip(metrics, labels))
                )
            )

    def show_flow_analysis(self, project_id: str, start_date: datetime, end_date: datetime):
        # Get TAKT metrics
        takt_data = self.data_service.get_takt_metrics(start_date, end_date, project_id)
        
        # Create Sankey diagram for flow analysis
        work_packages = takt_data['work_package'].unique()
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=work_packages,
                color="blue"
            ),
            link=dict(
                source=np.arange(len(work_packages)-1),
                target=np.arange(1, len(work_packages)),
                value=takt_data.groupby('work_package')['actual_duration'].mean()
            )
        )])
        
        fig.update_layout(title="Work Package Flow Analysis")
        st.plotly_chart(fig)
        
        # Add flow metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Flow Time", 
                     f"{takt_data['actual_duration'].mean():.1f} hours")
        with col2:
            st.metric("Flow Variability", 
                     f"{takt_data['variance'].std():.1f}%")

    def show_bottleneck_analysis(self, project_id: str, start_date: datetime, end_date: datetime):
        # Get bottleneck data
        takt_data = self.data_service.get_takt_metrics(start_date, end_date, project_id)
        
        # Create bottleneck visualization
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=takt_data['work_package'],
            y=takt_data['bottleneck_factor'],
            name='Bottleneck Factor',
            marker_color='red'
        ))
        
        fig.add_trace(go.Scatter(
            x=takt_data['work_package'],
            y=np.ones(len(takt_data)) * 1.2,  # Threshold line
            name='Bottleneck Threshold',
            line=dict(color='yellow', dash='dash')
        ))
        
        fig.update_layout(
            title="Bottleneck Analysis by Work Package",
            xaxis_title="Work Package",
            yaxis_title="Bottleneck Factor",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig)
        
        # Show bottleneck details
        bottlenecks = takt_data[takt_data['bottleneck_factor'] > 1.2]
        if not bottlenecks.empty:
            st.warning("Detected Bottlenecks:")
            st.dataframe(bottlenecks[['work_package', 'bottleneck_factor', 'variance']])

    def show_project_analysis(self, project_id: str):
        st.header("Project Analysis")
        
        # Project Analysis Form
        with st.form("project_analysis_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                project_type = st.selectbox(
                    "Project Type",
                    ["Construction", "Manufacturing", "Infrastructure"]
                )
                project_size = st.number_input(
                    "Project Size (sq ft)",
                    min_value=1000,
                    max_value=1000000,
                    value=50000,
                    step=1000
                )
                
            with col2:
                duration = st.number_input(
                    "Expected Duration (months)",
                    min_value=1,
                    max_value=60,
                    value=12
                )
                team_size = st.number_input(
                    "Team Size",
                    min_value=1,
                    max_value=1000,
                    value=20
                )
            
            submitted = st.form_submit_button("Analyze Project")
            
            if submitted:
                self._run_project_analysis(
                    project_id, project_type, project_size,
                    duration, team_size
                )

    def _run_project_analysis(self, project_id: str, project_type: str,
                            project_size: float, duration: int, team_size: int):
        """Run analysis on project parameters and display results"""
        st.subheader("Analysis Results")
        
        # Get historical data for similar projects
        metrics = self.data_service.calculate_advanced_metrics(
            start_date=datetime.now() - timedelta(days=365),
            end_date=datetime.now(),
            project_id=project_id
        )
        
        # Calculate recommended TAKT time
        total_work_hours = duration * 20 * 8  # months * days/month * hours/day
        recommended_takt = total_work_hours / (project_size / 1000)  # hours per 1000 sq ft
        
        # Display key recommendations
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Recommended TAKT Time",
                f"{recommended_takt:.1f} hrs/1000 sq ft",
                help="Based on project size and duration"
            )
            st.metric(
                "Optimal Team Size",
                f"{max(5, min(team_size, int(project_size/5000)))} workers",
                help="Calculated based on project size and industry standards"
            )
            
        with col2:
            st.metric(
                "Expected Flow Efficiency",
                f"{metrics['flow_efficiency']['flow_efficiency']:.1f}%",
                help="Based on historical data and project parameters"
            )
            st.metric(
                "Resource Utilization Target",
                "85%",
                help="Recommended target for optimal resource usage"
            )
            
        with col3:
            risk_level = "Low" if project_size < 50000 else "Medium" if project_size < 200000 else "High"
            st.metric(
                "Risk Level",
                risk_level,
                help="Based on project size and complexity"
            )
            st.metric(
                "Quality Target",
                "98%",
                help="Recommended quality compliance target"
            )
        
        # Show detailed analysis
        st.subheader("Detailed Analysis")
        
        # Work Packages Analysis
        st.write("##### Recommended Work Packages")
        work_packages = pd.DataFrame({
            'Work Package': ['Site Preparation', 'Foundation', 'Structure', 'MEP', 'Finishes'],
            'Duration (days)': [20, 40, 60, 45, 30],
            'Team Size': [5, 8, 12, 10, 8],
            'Dependencies': ['None', 'Site Prep', 'Foundation', 'Structure', 'MEP']
        })
        st.dataframe(work_packages)
        
        # Resource Planning
        st.write("##### Resource Planning")
        fig = go.Figure()
        
        # Add resource allocation bars
        resources = ['Labor', 'Equipment', 'Materials', 'Space']
        allocations = [85, 75, 90, 70]
        
        fig.add_trace(go.Bar(
            x=resources,
            y=allocations,
            text=allocations,
            textposition='auto',
            name='Recommended Allocation (%)'
        ))
        
        fig.update_layout(
            title="Recommended Resource Allocation",
            yaxis_title="Allocation (%)",
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk Analysis
        st.write("##### Risk Analysis")
        risks = pd.DataFrame({
            'Risk Factor': [
                'Weather Impact',
                'Resource Availability',
                'Technical Complexity',
                'Supply Chain',
                'Regulatory Compliance'
            ],
            'Probability': [0.3, 0.4, 0.5, 0.3, 0.2],
            'Impact': [0.6, 0.7, 0.5, 0.6, 0.8],
            'Mitigation Strategy': [
                'Weather monitoring and contingency planning',
                'Early resource booking and backup suppliers',
                'Technical training and expert consultation',
                'Multiple supplier agreements',
                'Regular compliance audits'
            ]
        })
        
        # Create risk matrix
        fig = px.scatter(
            risks,
            x='Probability',
            y='Impact',
            text='Risk Factor',
            size=[40] * len(risks),
            color='Impact',
            color_continuous_scale='RdYlGn_r'
        )
        
        fig.update_traces(
            textposition='top center',
            marker=dict(sizemode='area')
        )
        
        fig.update_layout(
            title='Risk Assessment Matrix',
            xaxis_title='Probability',
            yaxis_title='Impact',
            xaxis=dict(range=[0, 1]),
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(risks[['Risk Factor', 'Mitigation Strategy']])

    def show_reports(self, project_id: str):
        st.header("Reports")
        
        report_type = st.selectbox(
            "Select Report Type",
            ["Performance Analysis", "Risk Assessment", "Resource Utilization"]
        )
        
        # Date range for reports
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", 
                                     value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", 
                                   value=datetime.now())
        
        if report_type == "Performance Analysis":
            self.show_performance_report(project_id, start_date, end_date)
        elif report_type == "Risk Assessment":
            self.show_risk_report(project_id)
        elif report_type == "Resource Utilization":
            self.show_resource_report(project_id, start_date, end_date)

    def show_performance_report(self, project_id: str, start_date: datetime, end_date: datetime):
        st.subheader("Performance Analysis Report")
        
        # Get real performance data
        performance_data = self.data_service.get_performance_metrics(start_date, end_date, project_id)
        advanced_metrics = self.data_service.calculate_advanced_metrics(start_date, end_date, project_id)
        
        # Performance metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average TAKT Adherence", 
                     f"{advanced_metrics['takt_adherence']['average_adherence']:.1f}%")
        with col2:
            st.metric("Flow Efficiency", 
                     f"{advanced_metrics['flow_efficiency']['flow_efficiency']:.1f}%")
        with col3:
            st.metric("Waste Percentage", 
                     f"{advanced_metrics['flow_efficiency']['waste_percentage']:.1f}%")
        
        # Performance trends
        st.subheader("Performance Trends")
        
        # Create combo chart with bars and lines
        fig = go.Figure()
        
        # Add bars for actual durations
        fig.add_trace(go.Bar(
            x=performance_data['timestamp'],
            y=performance_data['actual_duration'],
            name='Actual Duration',
            marker_color='lightblue'
        ))
        
        # Add line for planned duration
        fig.add_trace(go.Scatter(
            x=performance_data['timestamp'],
            y=performance_data['planned_duration'],
            name='Planned Duration',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title='Duration Analysis Over Time',
            xaxis_title='Date',
            yaxis_title='Duration (hours)',
            barmode='group',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig)
        
        # Variance Analysis
        st.subheader("Variance Analysis")
        variance_fig = px.box(
            performance_data,
            y='variance',
            points='all',
            title='Distribution of TAKT Time Variance'
        )
        st.plotly_chart(variance_fig)
        
        # Predictive Analysis
        st.subheader("Predictive Analysis")
        prediction = advanced_metrics['predictive_metrics']['prediction']
        confidence = advanced_metrics['predictive_metrics']['confidence']
        
        st.info(f"""
        Based on current trends, the predicted TAKT time variance for the next period is 
        {prediction:.2f} hours (Confidence: {confidence:.1f}%)
        """)
        
        # Download report
        if st.button("Download Detailed Report"):
            report_data = performance_data.join(
                pd.DataFrame(advanced_metrics).add_prefix('metric_')
            )
            csv = report_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"performance_report_{project_id}.csv",
                mime="text/csv"
            )

    def show_risk_report(self, project_id: str):
        st.subheader("Risk Assessment Report")
        
        # Get real risk data
        risk_data = self.data_service.get_risk_matrix(project_id)
        
        # Create advanced risk matrix
        fig = go.Figure()
        
        # Add risk points
        fig.add_trace(go.Scatter(
            x=risk_data['probability'],
            y=risk_data['impact'],
            mode='markers+text',
            text=risk_data['risk_type'],
            textposition="top center",
            marker=dict(
                size=risk_data['probability'] * risk_data['impact'] * 100,
                color=risk_data['probability'] * risk_data['impact'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="Risk Score")
            ),
            hovertemplate="<b>%{text}</b><br>" +
                         "Probability: %{x:.2f}<br>" +
                         "Impact: %{y:.2f}<br>" +
                         "Status: %{customdata}<br>" +
                         "<extra></extra>",
            customdata=risk_data['status']
        ))
        
        # Add risk zones
        fig.add_shape(type="rect",
            x0=0, y0=0.7,
            x1=0.3, y1=1,
            fillcolor="red",
            opacity=0.1,
            line_width=0
        )
        
        fig.update_layout(
            title="Risk Assessment Matrix",
            xaxis_title="Probability",
            yaxis_title="Impact",
            xaxis=dict(range=[0, 1]),
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig)
        
        # Risk details
        st.subheader("Risk Details")
        
        # Create expandable sections for each risk
        for _, risk in risk_data.iterrows():
            with st.expander(f"Risk: {risk['risk_type']} (Status: {risk['status']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Probability", f"{risk['probability']:.2f}")
                with col2:
                    st.metric("Impact", f"{risk['impact']:.2f}")
                st.text("Mitigation Plan:")
                st.write(risk['mitigation_plan'])
        
        # Download risk report
        if st.button("Download Risk Report"):
            csv = risk_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"risk_report_{project_id}.csv",
                mime="text/csv"
            )

    def show_resource_report(self, project_id: str, start_date: datetime, end_date: datetime):
        st.subheader("Resource Utilization Report")
        
        # Get real resource data
        resource_data = self.data_service.get_resource_utilization(start_date, end_date, project_id)
        
        # Create waterfall chart for resource allocation
        fig = go.Figure(go.Waterfall(
            name="Resource Allocation",
            orientation="v",
            measure=["relative"] * len(resource_data),
            x=resource_data['resource_type'],
            textposition="outside",
            text=resource_data['actual'].round(1),
            y=resource_data['actual'],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="Resource Allocation Waterfall",
            showlegend=True,
            xaxis_title="Resource Type",
            yaxis_title="Utilization (%)"
        )
        
        st.plotly_chart(fig)
        
        # Resource efficiency analysis
        st.subheader("Resource Efficiency Analysis")
        
        # Create bubble chart for efficiency analysis
        fig2 = px.scatter(
            resource_data,
            x='planned',
            y='actual',
            size='efficiency',
            color='resource_type',
            hover_name='resource_type',
            size_max=60,
            title="Resource Efficiency Analysis"
        )
        
        fig2.add_trace(
            go.Scatter(
                x=[0, 100],
                y=[0, 100],
                mode='lines',
                name='Perfect Utilization',
                line=dict(dash='dash', color='gray')
            )
        )
        
        fig2.update_layout(
            xaxis_title="Planned Utilization (%)",
            yaxis_title="Actual Utilization (%)"
        )
        
        st.plotly_chart(fig2)
        
        # Resource details table with conditional formatting
        st.subheader("Resource Details")
        
        # Add efficiency indicators
        def color_efficiency(val):
            if val >= 90:
                return 'background-color: green; color: white'
            elif val >= 70:
                return 'background-color: yellow'
            return 'background-color: red; color: white'
        
        styled_df = resource_data.style.applymap(
            color_efficiency,
            subset=['efficiency']
        )
        
        st.dataframe(styled_df)
        
        # Download resource report
        if st.button("Download Resource Report"):
            csv = resource_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"resource_report_{project_id}.csv",
                mime="text/csv"
            )

    def show_takt_planning(self, project_id: str):
        st.header("TAKT Planning")
        
        # TAKT Time Configuration
        st.subheader("TAKT Time Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            available_time = st.number_input(
                "Available Working Time (hours/day)",
                min_value=1,
                max_value=24,
                value=8,
                help="Total available working hours per day"
            )
            
            work_days = st.number_input(
                "Working Days per Week",
                min_value=1,
                max_value=7,
                value=5,
                help="Number of working days in a week"
            )
            
        with col2:
            crew_size = st.number_input(
                "Crew Size (workers)",
                min_value=1,
                max_value=100,
                value=10,
                help="Number of workers in a crew"
            )
            
            buffer_percentage = st.slider(
                "Buffer Percentage",
                min_value=0,
                max_value=30,
                value=15,
                help="Percentage of time added as buffer"
            )
        
        # Work Packages Configuration
        st.subheader("Work Packages")
        
        # Initialize session state for work packages if not exists
        if 'work_packages' not in st.session_state:
            st.session_state.work_packages = []
        
        # Add new work package form
        with st.expander("Add Work Package", expanded=len(st.session_state.work_packages) == 0):
            with st.form("work_package_form"):
                wp_col1, wp_col2 = st.columns(2)
                
                with wp_col1:
                    package_name = st.text_input("Work Package Name")
                    work_amount = st.number_input(
                        "Work Amount (units)",
                        min_value=1,
                        value=100,
                        help="Total amount of work in units (e.g., sq ft, items)"
                    )
                    
                with wp_col2:
                    dependencies = st.multiselect(
                        "Dependencies",
                        options=[wp['name'] for wp in st.session_state.work_packages],
                        help="Select work packages that must be completed before this one"
                    )
                    productivity_rate = st.number_input(
                        "Productivity Rate (units/hour)",
                        min_value=0.1,
                        value=10.0,
                        help="Expected units of work completed per hour"
                    )
                
                if st.form_submit_button("Add Work Package"):
                    if package_name:
                        # Calculate duration
                        base_duration = work_amount / (productivity_rate * crew_size * available_time)
                        buffer_time = base_duration * (buffer_percentage / 100)
                        total_duration = base_duration + buffer_time
                        
                        st.session_state.work_packages.append({
                            'name': package_name,
                            'work_amount': work_amount,
                            'productivity_rate': productivity_rate,
                            'dependencies': dependencies,
                            'base_duration': base_duration,
                            'buffer_time': buffer_time,
                            'total_duration': total_duration
                        })
                        st.experimental_rerun()
                    else:
                        st.error("Please enter a work package name")
        
        # Display Work Packages
        if st.session_state.work_packages:
            st.write("##### Configured Work Packages")
            
            # Convert work packages to DataFrame for display
            wp_df = pd.DataFrame([{
                'Work Package': wp['name'],
                'Work Amount': f"{wp['work_amount']} units",
                'Productivity Rate': f"{wp['productivity_rate']} units/hour",
                'Base Duration': f"{wp['base_duration']:.1f} days",
                'Buffer': f"{wp['buffer_time']:.1f} days",
                'Total Duration': f"{wp['total_duration']:.1f} days",
                'Dependencies': ', '.join(wp['dependencies']) if wp['dependencies'] else 'None'
            } for wp in st.session_state.work_packages])
            
            st.dataframe(wp_df)
            
            # TAKT Plan Visualization
            st.subheader("TAKT Plan Visualization")
            
            # Create Gantt chart
            tasks = []
            for wp in st.session_state.work_packages:
                # Calculate start time based on dependencies
                start_date = datetime.now()
                if wp['dependencies']:
                    # Find the latest end date among dependencies
                    dep_end_dates = []
                    for dep in wp['dependencies']:
                        dep_wp = next((w for w in st.session_state.work_packages if w['name'] == dep), None)
                        if dep_wp:
                            dep_end_dates.append(start_date + timedelta(days=float(dep_wp['total_duration'])))
                    if dep_end_dates:
                        start_date = max(dep_end_dates)
                
                tasks.append({
                    'Task': wp['name'],
                    'Start': start_date,
                    'Duration': wp['total_duration'],
                    'End': start_date + timedelta(days=wp['total_duration']),
                    'Dependencies': wp['dependencies']
                })
            
            fig = px.timeline(
                pd.DataFrame(tasks),
                x_start='Start',
                x_end='End',
                y='Task',
                title='TAKT Plan Timeline'
            )
            
            fig.update_layout(
                showlegend=True,
                xaxis_title='Date',
                yaxis_title='Work Package'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add clear button
            if st.button("Clear All Work Packages"):
                st.session_state.work_packages = []
                st.experimental_rerun()
            
        # TAKT Control Board
        st.subheader("TAKT Control Board")
        
        if st.session_state.work_packages:
            # Create control board with status tracking
            status_options = ['Not Started', 'In Progress', 'Completed', 'Delayed']
            
            for i, wp in enumerate(st.session_state.work_packages):
                status_key = f"status_{wp['name']}_{i}"  # Added index to make key unique
                if status_key not in st.session_state:
                    st.session_state[status_key] = 'Not Started'
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{wp['name']}**")
                with col2:
                    new_status = st.selectbox(
                        "Status",
                        options=status_options,
                        key=status_key
                    )
                with col3:
                    if new_status == 'Delayed':
                        st.error("⚠️ Delayed")
                    elif new_status == 'Completed':
                        st.success("✅ On Track")
                    elif new_status == 'In Progress':
                        st.info("🔄 In Progress")
                    else:
                        st.warning("⏳ Not Started")

    def show_training(self):
        st.header("Training & Implementation")
        
        # Training Modules Selection
        st.subheader("TAKT Training Modules")
        
        # Define training modules
        modules = {
            "takt_fundamentals": {
                "title": "TAKT Fundamentals",
                "duration": "4 hours",
                "level": "Beginner",
                "topics": [
                    "Introduction to TAKT Planning",
                    "Core Principles and Concepts",
                    "Benefits and Applications",
                    "Basic Implementation Steps"
                ],
                "prerequisites": None
            },
            "advanced_planning": {
                "title": "Advanced TAKT Planning",
                "duration": "8 hours",
                "level": "Intermediate",
                "topics": [
                    "Detailed TAKT Time Calculation",
                    "Work Package Optimization",
                    "Resource Leveling",
                    "Buffer Management"
                ],
                "prerequisites": "TAKT Fundamentals"
            },
            "implementation": {
                "title": "TAKT Implementation",
                "duration": "6 hours",
                "level": "Advanced",
                "topics": [
                    "Implementation Strategy",
                    "Team Organization",
                    "Progress Monitoring",
                    "Continuous Improvement"
                ],
                "prerequisites": "Advanced TAKT Planning"
            },
            "digital_tools": {
                "title": "Digital Tools for TAKT",
                "duration": "4 hours",
                "level": "Intermediate",
                "topics": [
                    "TAKT Planning Software",
                    "Digital Collaboration Tools",
                    "Data Collection and Analysis",
                    "Reporting and Dashboards"
                ],
                "prerequisites": "TAKT Fundamentals"
            }
        }
        
        # Module selection
        selected_module = st.selectbox(
            "Select Training Module",
            options=list(modules.keys()),
            format_func=lambda x: f"{modules[x]['title']} ({modules[x]['duration']})"
        )
        
        # Display module details
        if selected_module:
            module = modules[selected_module]
            
            # Module overview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Duration", module['duration'])
            with col2:
                st.metric("Level", module['level'])
            with col3:
                st.metric(
                    "Prerequisites",
                    module['prerequisites'] if module['prerequisites'] else "None"
                )
            
            # Topics covered
            st.write("##### Topics Covered")
            for topic in module['topics']:
                st.markdown(f"- {topic}")
            
            # Interactive learning section
            st.subheader("Interactive Learning")
            
            # Quiz section
            if st.button("Start Quiz"):
                st.session_state.show_quiz = True
                st.session_state.quiz_score = 0
                st.session_state.current_question = 0
                
                # Sample quiz questions for each module
                st.session_state.quiz_questions = {
                    "takt_fundamentals": [
                        {
                            "question": "What is TAKT time?",
                            "options": [
                                "The total project duration",
                                "The rhythm or pace of production to match customer demand",
                                "The time spent on breaks",
                                "The delay between tasks"
                            ],
                            "correct": 1
                        },
                        {
                            "question": "Which is NOT a key principle of TAKT planning?",
                            "options": [
                                "Continuous flow",
                                "Work standardization",
                                "Random task allocation",
                                "Buffer management"
                            ],
                            "correct": 2
                        }
                    ],
                    "advanced_planning": [
                        {
                            "question": "How is TAKT time calculated?",
                            "options": [
                                "Available working time / Customer demand",
                                "Total tasks / Number of workers",
                                "Project duration / Number of phases",
                                "Work packages * Buffer time"
                            ],
                            "correct": 0
                        },
                        {
                            "question": "What is the purpose of buffer time in TAKT planning?",
                            "options": [
                                "To extend the project timeline",
                                "To account for variations and uncertainties",
                                "To reduce worker productivity",
                                "To increase project cost"
                            ],
                            "correct": 1
                        }
                    ]
                }
                
            if hasattr(st.session_state, 'show_quiz') and st.session_state.show_quiz:
                questions = st.session_state.quiz_questions.get(selected_module, [])
                if st.session_state.current_question < len(questions):
                    question = questions[st.session_state.current_question]
                    
                    st.write(f"**Question {st.session_state.current_question + 1}:**")
                    st.write(question["question"])
                    
                    answer = st.radio(
                        "Select your answer:",
                        options=question["options"],
                        key=f"quiz_{st.session_state.current_question}"
                    )
                    
                    if st.button("Submit Answer"):
                        if question["options"].index(answer) == question["correct"]:
                            st.success("Correct! 🎉")
                            st.session_state.quiz_score += 1
                        else:
                            st.error("Incorrect. The correct answer is: " + 
                                   question["options"][question["correct"]])
                        
                        st.session_state.current_question += 1
                        if st.session_state.current_question < len(questions):
                            st.experimental_rerun()
                else:
                    # Quiz completed
                    st.success(f"Quiz completed! Score: {st.session_state.quiz_score}/{len(questions)}")
                    if st.button("Restart Quiz"):
                        st.session_state.show_quiz = False
                        st.experimental_rerun()
            
            # Resources section
            st.subheader("Additional Resources")
            
            # Resource tabs
            resource_tabs = st.tabs(["Documentation", "Videos", "Templates"])
            
            with resource_tabs[0]:
                st.markdown("""
                    📚 **Documentation**
                    - TAKT Planning Guide (PDF)
                    - Implementation Checklist
                    - Best Practices Manual
                    """)
                
            with resource_tabs[1]:
                st.markdown("""
                    🎥 **Video Tutorials**
                    - Introduction to TAKT Planning
                    - Step-by-step Implementation Guide
                    - Case Studies and Success Stories
                    """)
                
            with resource_tabs[2]:
                st.markdown("""
                    📋 **Templates**
                    - TAKT Time Calculator
                    - Work Package Template
                    - Progress Tracking Sheet
                    """)
            
            # Progress tracking
            st.subheader("Training Progress")
            
            # Initialize progress in session state if not exists
            if f"progress_{selected_module}" not in st.session_state:
                st.session_state[f"progress_{selected_module}"] = 0
            
            progress = st.session_state[f"progress_{selected_module}"]
            
            # Progress bar
            st.progress(progress)
            st.write(f"Module Completion: {int(progress * 100)}%")
            
            # Mark complete button
            if progress < 1.0:
                if st.button("Mark Module as Complete"):
                    st.session_state[f"progress_{selected_module}"] = 1.0
                    st.experimental_rerun()
            else:
                st.success("Module Completed! 🎉")
                if st.button("Reset Progress"):
                    st.session_state[f"progress_{selected_module}"] = 0
                    st.experimental_rerun()

if __name__ == "__main__":
    ui = TaktUI()
    ui.run()
