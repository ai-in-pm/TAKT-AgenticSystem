import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

class TaktDataProcessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)

    def process_project_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw project data for analysis
        """
        processed_data = {
            'takt_metrics': self._calculate_takt_metrics(raw_data),
            'resource_metrics': self._calculate_resource_metrics(raw_data),
            'performance_metrics': self._calculate_performance_metrics(raw_data)
        }
        return processed_data

    def _calculate_takt_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate key TAKT metrics
        """
        takt_time = data.get('available_time', 0) / data.get('customer_demand', 1)
        cycle_time = np.mean(data.get('cycle_times', [takt_time]))
        
        return {
            'takt_time': takt_time,
            'cycle_time': cycle_time,
            'efficiency': (takt_time / cycle_time if cycle_time > 0 else 0) * 100
        }

    def _calculate_resource_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate resource utilization metrics
        """
        resources = data.get('resources', {})
        
        metrics = {
            'labor_utilization': self._calculate_utilization(resources.get('labor', [])),
            'equipment_utilization': self._calculate_utilization(resources.get('equipment', [])),
            'material_efficiency': self._calculate_material_efficiency(resources.get('materials', {}))
        }
        
        return metrics

    def _calculate_performance_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate performance-related metrics
        """
        actual_progress = data.get('actual_progress', [])
        planned_progress = data.get('planned_progress', [])
        
        if not actual_progress or not planned_progress:
            return {'schedule_performance': 0, 'cost_performance': 0}
            
        schedule_performance = np.mean(np.array(actual_progress) / np.array(planned_progress))
        cost_performance = data.get('actual_cost', 0) / data.get('planned_cost', 1)
        
        return {
            'schedule_performance': schedule_performance * 100,
            'cost_performance': (1 - (cost_performance - 1)) * 100 if cost_performance > 0 else 0
        }

    def analyze_trends(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze historical trends in TAKT performance
        """
        if historical_data.empty:
            return {}
            
        # Perform time series analysis
        trends = {
            'moving_average': self._calculate_moving_average(historical_data),
            'seasonality': self._analyze_seasonality(historical_data),
            'anomalies': self._detect_anomalies(historical_data)
        }
        
        return trends

    def _calculate_moving_average(self, data: pd.DataFrame, window: int = 7) -> pd.Series:
        """Calculate moving average of performance metrics"""
        if 'performance' not in data.columns:
            return pd.Series()
        return data['performance'].rolling(window=window).mean()

    def _analyze_seasonality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze seasonal patterns in the data"""
        if 'performance' not in data.columns or 'date' not in data.columns:
            return {}
            
        data['month'] = pd.to_datetime(data['date']).dt.month
        monthly_avg = data.groupby('month')['performance'].mean()
        
        return {
            'monthly_averages': monthly_avg.to_dict(),
            'peak_month': monthly_avg.idxmax(),
            'low_month': monthly_avg.idxmin()
        }

    def _detect_anomalies(self, data: pd.DataFrame, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in performance data using z-score
        """
        if 'performance' not in data.columns:
            return []
            
        z_scores = np.abs(stats.zscore(data['performance']))
        anomalies = data[z_scores > threshold]
        
        return [
            {
                'date': row['date'],
                'value': row['performance'],
                'z_score': z_score
            }
            for (_, row), z_score in zip(anomalies.iterrows(), z_scores[z_scores > threshold])
        ]

    def _calculate_utilization(self, resource_data: List[float]) -> float:
        """Calculate resource utilization percentage"""
        if not resource_data:
            return 0
        return (np.mean(resource_data) / 100) * 100

    def _calculate_material_efficiency(self, material_data: Dict[str, Any]) -> float:
        """Calculate material usage efficiency"""
        if not material_data:
            return 0
            
        planned = material_data.get('planned', 0)
        actual = material_data.get('actual', 0)
        
        if planned == 0:
            return 0
            
        return ((planned - actual) / planned) * 100 if actual <= planned else 0
