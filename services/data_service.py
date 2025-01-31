import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sqlite3
import json

class TaktDataService:
    def __init__(self, db_path: str = "takt_data.db"):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables for different metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                timestamp DATETIME,
                metric_type TEXT,
                value REAL,
                work_area TEXT,
                project_id TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resource_utilization (
                timestamp DATETIME,
                resource_type TEXT,
                planned REAL,
                actual REAL,
                efficiency REAL,
                project_id TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_events (
                timestamp DATETIME,
                risk_type TEXT,
                probability REAL,
                impact REAL,
                status TEXT,
                mitigation_plan TEXT,
                project_id TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS takt_metrics (
                timestamp DATETIME,
                work_package TEXT,
                planned_duration REAL,
                actual_duration REAL,
                variance REAL,
                bottleneck_factor REAL,
                project_id TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def get_performance_metrics(self, 
                              start_date: datetime,
                              end_date: datetime,
                              project_id: Optional[str] = None) -> pd.DataFrame:
        """Retrieve performance metrics for the specified date range"""
        # First get the raw data
        query = '''
            SELECT timestamp, metric_type, value, work_area
            FROM performance_metrics
            WHERE timestamp BETWEEN ? AND ?
        '''
        
        params = [start_date, end_date]
        if project_id:
            query += ' AND project_id = ?'
            params.append(project_id)

        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        # If no data exists, return an empty DataFrame with required columns
        if df.empty:
            return pd.DataFrame({
                'timestamp': [],
                'TAKT_Adherence': [],
                'Flow_Efficiency': [],
                'Resource_Utilization': [],
                'planned_duration': [],
                'actual_duration': [],
                'variance': []
            })

        # Pivot the data for easier analysis
        df_pivot = df.pivot_table(
            index='timestamp',
            columns='metric_type',
            values='value',
            aggfunc='mean'
        ).reset_index()

        # Ensure all required columns exist
        required_columns = ['TAKT_Adherence', 'Flow_Efficiency', 'Resource_Utilization', 
                          'planned_duration', 'actual_duration', 'variance']
        for col in required_columns:
            if col not in df_pivot.columns:
                df_pivot[col] = 0.0

        return df_pivot

    def get_resource_utilization(self,
                               start_date: datetime,
                               end_date: datetime,
                               project_id: Optional[str] = None) -> pd.DataFrame:
        """Retrieve resource utilization data"""
        query = '''
            SELECT timestamp, resource_type, planned, actual, efficiency
            FROM resource_utilization
            WHERE timestamp BETWEEN ? AND ?
        '''
        
        params = [start_date, end_date]
        if project_id:
            query += ' AND project_id = ?'
            params.append(project_id)

        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        return df

    def get_risk_matrix(self,
                       project_id: Optional[str] = None) -> pd.DataFrame:
        """Retrieve current risk matrix data"""
        query = '''
            SELECT risk_type, probability, impact, status, mitigation_plan
            FROM risk_events
            WHERE timestamp = (
                SELECT MAX(timestamp)
                FROM risk_events
                WHERE project_id = ? OR project_id IS NULL
            )
        '''

        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn, params=[project_id])
        conn.close()

        return df

    def get_takt_metrics(self,
                        start_date: datetime,
                        end_date: datetime,
                        project_id: Optional[str] = None) -> pd.DataFrame:
        """Retrieve TAKT-specific metrics"""
        query = '''
            SELECT timestamp, work_package, planned_duration, actual_duration,
                   variance, bottleneck_factor
            FROM takt_metrics
            WHERE timestamp BETWEEN ? AND ?
        '''
        
        params = [start_date, end_date]
        if project_id:
            query += ' AND project_id = ?'
            params.append(project_id)

        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        return df

    def calculate_advanced_metrics(self, 
                                 start_date: datetime,
                                 end_date: datetime,
                                 project_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate advanced TAKT metrics"""
        takt_data = self.get_takt_metrics(start_date, end_date, project_id)
        
        metrics = {
            'takt_adherence': self._calculate_takt_adherence(takt_data),
            'flow_efficiency': self._calculate_flow_efficiency(takt_data),
            'bottleneck_analysis': self._analyze_bottlenecks(takt_data),
            'variance_trends': self._analyze_variance_trends(takt_data),
            'predictive_metrics': self._calculate_predictive_metrics(takt_data)
        }
        
        return metrics

    def _calculate_takt_adherence(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate TAKT time adherence metrics"""
        if data.empty:
            return {'average_adherence': 0, 'stability_index': 0}
            
        variance_ratio = data['actual_duration'] / data['planned_duration']
        return {
            'average_adherence': (variance_ratio <= 1.1).mean() * 100,
            'stability_index': 100 - (variance_ratio.std() * 100)
        }

    def _calculate_flow_efficiency(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate flow efficiency metrics"""
        if data.empty:
            return {'flow_efficiency': 0, 'waste_percentage': 0}
            
        total_time = data['actual_duration'].sum()
        value_added_time = data[data['variance'] <= 0]['actual_duration'].sum()
        
        flow_efficiency = (value_added_time / total_time * 100) if total_time > 0 else 0
        return {
            'flow_efficiency': flow_efficiency,
            'waste_percentage': 100 - flow_efficiency
        }

    def _analyze_bottlenecks(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze bottlenecks in the TAKT system"""
        if data.empty:
            return []
            
        bottlenecks = data[data['bottleneck_factor'] > 1.2]
        return [
            {
                'work_package': row['work_package'],
                'bottleneck_factor': row['bottleneck_factor'],
                'impact': row['variance']
            }
            for _, row in bottlenecks.iterrows()
        ]

    def _analyze_variance_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends in TAKT time variance"""
        if data.empty:
            return {'trend': 'No data', 'pattern': None}
            
        variance_series = data['variance'].rolling(window=5).mean()
        trend = 'Improving' if variance_series.iloc[-1] < variance_series.iloc[0] else 'Degrading'
        
        return {
            'trend': trend,
            'pattern': variance_series.tolist()
        }

    def _calculate_predictive_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate predictive metrics for future TAKT performance"""
        if data.empty:
            return {'prediction': None, 'confidence': 0}
            
        # Simple linear regression for prediction
        X = np.arange(len(data)).reshape(-1, 1)
        y = data['variance'].values
        
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X, y)
        
        next_point = model.predict([[len(data)]])[0]
        confidence = model.score(X, y) * 100
        
        return {
            'prediction': next_point,
            'confidence': confidence
        }

    def insert_sample_data(self, project_id: str = "Project A"):
        """Insert sample data for testing purposes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Sample dates
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=30),
            end=datetime.now(),
            freq='D'
        )

        # Sample performance metrics
        for date in dates:
            date_str = date.strftime('%Y-%m-%d %H:%M:%S')
            # TAKT Adherence (80-95%)
            cursor.execute('''
                INSERT INTO performance_metrics (timestamp, metric_type, value, work_area, project_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (date_str, 'TAKT_Adherence', np.random.uniform(80, 95), 'All', project_id))

            # Flow Efficiency (70-90%)
            cursor.execute('''
                INSERT INTO performance_metrics (timestamp, metric_type, value, work_area, project_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (date_str, 'Flow_Efficiency', np.random.uniform(70, 90), 'All', project_id))

            # Resource Utilization (75-95%)
            cursor.execute('''
                INSERT INTO performance_metrics (timestamp, metric_type, value, work_area, project_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (date_str, 'Resource_Utilization', np.random.uniform(75, 95), 'All', project_id))

        # Sample TAKT metrics
        work_packages = ['Foundation', 'Framing', 'MEP', 'Finishes', 'Exterior']
        for date in dates:
            date_str = date.strftime('%Y-%m-%d %H:%M:%S')
            for package in work_packages:
                planned = np.random.uniform(20, 40)  # Planned duration in hours
                actual = planned * np.random.uniform(0.9, 1.2)  # Actual duration with some variance
                cursor.execute('''
                    INSERT INTO takt_metrics (
                        timestamp, work_package, planned_duration, actual_duration,
                        variance, bottleneck_factor, project_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    date_str, package, planned, actual,
                    actual - planned,  # Variance
                    actual / planned,  # Bottleneck factor
                    project_id
                ))

        # Sample resource utilization
        resource_types = ['Labor', 'Equipment', 'Materials', 'Space']
        for date in dates:
            date_str = date.strftime('%Y-%m-%d %H:%M:%S')
            for resource in resource_types:
                planned = np.random.uniform(70, 90)
                actual = planned * np.random.uniform(0.8, 1.1)
                cursor.execute('''
                    INSERT INTO resource_utilization (
                        timestamp, resource_type, planned, actual,
                        efficiency, project_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    date_str, resource, planned, actual,
                    (actual / planned) * 100,  # Efficiency
                    project_id
                ))

        # Sample risk events
        risk_types = [
            'Weather Delay', 'Material Shortage', 'Labor Shortage',
            'Equipment Failure', 'Quality Issues'
        ]
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for risk in risk_types:
            cursor.execute('''
                INSERT INTO risk_events (
                    timestamp, risk_type, probability, impact,
                    status, mitigation_plan, project_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                current_time, risk,
                np.random.uniform(0.1, 0.9),  # Probability
                np.random.uniform(0.2, 0.8),  # Impact
                np.random.choice(['Active', 'Mitigated']),
                f'Mitigation plan for {risk.lower()}',
                project_id
            ))

        conn.commit()
        conn.close()
