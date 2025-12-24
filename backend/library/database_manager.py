# algorithm/backend/library/database_manager.py

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    """
    Manage TSP instances and results using CSV files
    """
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "database"
        self.db_path.mkdir(exist_ok=True)
        
        self.instances_file = self.db_path / "tsp_instances_dataset.csv"
        self.results_file = self.db_path / "tsp_dataset.csv"
        
        self._initialize_databases()

    def _initialize_databases(self):
        """Create CSV files if they don't exist"""
        
        # Instances database
        if not self.instances_file.exists():
            df = pd.DataFrame(columns=[
                'instance_id', 'name', 'num_cities', 'cost_matrix', 
                'created_at', 'optimal_cost'
            ])
            df.to_csv(self.instances_file, index=False)
        
        # Results database
        if not self.results_file.exists():
            df = pd.DataFrame(columns=[
                'run_id', 'instance_id', 'algorithm', 'num_cities',
                'cost', 'time', 'path', 'quantum_calls', 'classical_calls',
                'dp_states', 'timestamp'
            ])
            df.to_csv(self.results_file, index=False)
    
    def save_instance(self, name, size, cost_matrix):
        """Save TSP instance"""
        df = pd.read_csv(self.instances_file)
        
        instance_id = f"TSP_{size}_{len(df)}"
        
        new_row = {
            'instance_id': instance_id,
            'name': name,
            'num_cities': size,
            'cost_matrix': json.dumps(cost_matrix),
            'created_at': datetime.now().isoformat(),
            'optimal_cost': None
        }
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.instances_file, index=False)
        
        return instance_id
    
    def save_result(self, algorithm, city_count, cost, time, path, 
                    quantum_calls=0, classical_calls=0, dp_states=0):
        """Save algorithm execution result"""
        df = pd.read_csv(self.results_file)
        
        run_id = f"RUN_{len(df)}"
        
        new_row = {
            'run_id': run_id,
            'instance_id': None,
            'algorithm': algorithm,
            'num_cities': city_count,
            'cost': cost,
            'time': time,
            'path': json.dumps(path),
            'quantum_calls': quantum_calls,
            'classical_calls': classical_calls,
            'dp_states': dp_states,
            'timestamp': datetime.now().isoformat()
        }
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.results_file, index=False)
        
        return run_id
    
    def get_all_instances(self):
        """Get all saved instances"""
        if not self.instances_file.exists():
            return []
        
        df = pd.read_csv(self.instances_file)
        instances = []
        
        for _, row in df.iterrows():
            instances.append({
                'instance_id': row['instance_id'],
                'name': row['name'],
                'size': int(row['num_cities']),
                'cost_matrix': json.loads(row['cost_matrix']),
                'created_at': row['created_at']
            })
        
        return instances

    @staticmethod
    def _json_safe(x, default=0):
        # handles numpy/pandas NaN
        if x is None:
            return default
        try:
            if pd.isna(x):
                return default
        except Exception:
            pass
        # handles inf/-inf
        if isinstance(x, (float, np.floating)) and (np.isinf(x) or np.isnan(x)):
            return default
        return x

    def get_statistics(self):
        if not self.results_file.exists():
            return {
                "total_runs": 0,
                "algorithms": {},
                "avg_time_by_size": {},
                "avg_quantum_calls": 0,
                "avg_classical_calls": 0
            }

        df = pd.read_csv(self.results_file)

        if df.empty:
            return {
                "total_runs": 0,
                "algorithms": {},
                "avg_time_by_size": {},
                "avg_quantum_calls": 0,
                "avg_classical_calls": 0
            }

        # Ensure numeric
        for col in ["time", "quantum_calls", "classical_calls", "num_cities"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        avg_time_by_size = (
            df.groupby("num_cities")["time"]
            .mean()
            .dropna()
            .to_dict()
        )

        stats = {
            "total_runs": int(len(df)),
            "algorithms": df["algorithm"].value_counts().to_dict() if "algorithm" in df.columns else {},
            "avg_time_by_size": {int(k): float(v) for k, v in avg_time_by_size.items()},
            "avg_quantum_calls": float(self._json_safe(df["quantum_calls"].mean(), 0)),
            "avg_classical_calls": float(self._json_safe(df["classical_calls"].mean(), 0)),
        }

        return stats