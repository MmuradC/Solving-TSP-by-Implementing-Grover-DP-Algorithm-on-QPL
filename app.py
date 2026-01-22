from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
import os
import json
from werkzeug.utils import secure_filename
from quantum_solver import QuantumTSPSolver
from classical_solver import ClassicalTSPSolver
from visualizer import TSPVisualizer
import io
import sys

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['JSON_SORT_KEYS'] = False

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

current_data = {
    'df': None,
    'distance_matrix': None,
    'num_cities': 0
}

def make_json_response(success=True, **kwargs):
    """Helper to ensure consistent JSON responses"""
    response_data = {'success': success}
    response_data.update(kwargs)
    return jsonify(response_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return make_json_response(False, error='No file uploaded'), 400
        
        file = request.files['file']
        if file.filename == '':
            return make_json_response(False, error='No file selected'), 400
        
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            df = pd.read_csv(filepath)
            processed_data = process_tsp_dataset(df)
            
            current_data['df'] = df
            current_data['distance_matrix'] = processed_data['distance_matrix']
            current_data['num_cities'] = processed_data['num_cities']
            
            visualizer = TSPVisualizer()
            viz_html = visualizer.visualize_dataset(processed_data)
            
            return make_json_response(
                True,
                num_cities=int(processed_data['num_cities']),
                visualization=viz_html,
                stats={
                    'rows': int(len(df)),
                    'columns': int(len(df.columns)),
                    'features': [str(col) for col in df.columns]
                }
            )
        
        return make_json_response(False, error='Invalid file format'), 400
    
    except Exception as e:
        print(f"Upload error: {str(e)}", file=sys.stderr)
        return make_json_response(False, error=str(e)), 500

@app.route('/randomize', methods=['POST'])
def randomize_values():
    try:
        data = request.get_json() or {}
        num_cities = int(data.get('num_cities', 5))
        num_cities = min(max(num_cities, 3), 10)
        
        np.random.seed()
        distance_matrix = np.random.randint(1, 100, size=(num_cities, num_cities))
        distance_matrix = (distance_matrix + distance_matrix.T) // 2
        np.fill_diagonal(distance_matrix, 0)
        
        current_data['distance_matrix'] = distance_matrix
        current_data['num_cities'] = num_cities
        
        visualizer = TSPVisualizer()
        viz_html = visualizer.visualize_distance_matrix(distance_matrix)
        
        return make_json_response(
            True,
            num_cities=int(num_cities),
            visualization=viz_html
        )
    
    except Exception as e:
        print(f"Randomize error: {str(e)}", file=sys.stderr)
        return make_json_response(False, error=str(e)), 500

@app.route('/show_circuit', methods=['POST'])
def show_circuit():
    try:
        if current_data['distance_matrix'] is None:
            return make_json_response(False, error='No dataset loaded'), 400
        
        solver = QuantumTSPSolver(current_data['distance_matrix'])
        circuit_img = solver.visualize_circuit()
        
        return make_json_response(
            True,
            circuit_image=circuit_img,
            num_qubits=int(solver.num_qubits),
            circuit_depth=int(solver.circuit_depth)
        )
    
    except Exception as e:
        print(f"Circuit error: {str(e)}", file=sys.stderr)
        return make_json_response(False, error=str(e)), 500

@app.route('/solve_quantum', methods=['POST'])
def solve_quantum():
    try:
        if current_data['distance_matrix'] is None:
            return make_json_response(False, error='No dataset loaded'), 400
        
        if current_data['num_cities'] > 10:
            return make_json_response(
                False, 
                error=f'Quantum solver limited to 10 cities. Current: {current_data["num_cities"]}'
            ), 400
        
        solver = QuantumTSPSolver(current_data['distance_matrix'])
        result = solver.solve()
        
        return make_json_response(
            True,
            optimal_tour=[int(x) for x in result['optimal_tour']],
            optimal_cost=float(result['optimal_cost']),
            execution_time=float(result['execution_time']),
            quantum_info={
                'num_iterations': int(result.get('num_iterations', 0)),
                'success_probability': float(result.get('success_probability', 0))
            }
        )
    
    except Exception as e:
        print(f"Quantum solve error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return make_json_response(False, error=str(e)), 500

@app.route('/solve_classical', methods=['POST'])
def solve_classical():
    try:
        if current_data['distance_matrix'] is None:
            return make_json_response(False, error='No dataset loaded'), 400
        
        data = request.get_json() or {}
        algorithm = data.get('algorithm', 'greedy')
        
        # Size limits
        if algorithm in ['held_karp', 'branch_bound'] and current_data['num_cities'] > 15:
            return make_json_response(
                False,
                error=f'{algorithm} limited to 15 cities. Use greedy for larger problems.'
            ), 400
        
        solver = ClassicalTSPSolver(current_data['distance_matrix'])
        
        if algorithm == 'held_karp':
            result = solver.held_karp()
        elif algorithm == 'branch_bound':
            result = solver.branch_and_bound()
        else:
            result = solver.greedy()
        
        return make_json_response(
            True,
            algorithm=str(algorithm),
            optimal_tour=[int(x) for x in result['optimal_tour']],
            optimal_cost=float(result['optimal_cost']),
            execution_time=float(result['execution_time'])
        )
    
    except Exception as e:
        print(f"Classical solve error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return make_json_response(False, error=str(e)), 500

@app.route('/visualize_results', methods=['POST'])
def visualize_results():
    try:
        data = request.get_json() or {}
        results = data.get('results', {})
        
        if not results:
            return make_json_response(False, error='No results to visualize'), 400
        
        if current_data['distance_matrix'] is None:
            return make_json_response(False, error='No dataset loaded'), 400
        
        visualizer = TSPVisualizer()
        viz_html = visualizer.compare_results(
            current_data['distance_matrix'],
            results
        )
        
        return make_json_response(True, visualization=viz_html)
    
    except Exception as e:
        print(f"Visualize error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return make_json_response(False, error=str(e)), 500

@app.route('/save_results', methods=['POST'])
def save_results():
    try:
        data = request.get_json() or {}
        results = data.get('results', {})
        
        if not results:
            return make_json_response(False, error='No results to save'), 400
        
        results_list = []
        for name, data in results.items():
            results_list.append({
                'Algorithm': str(name),
                'Tour': str(data.get('optimal_tour', [])),
                'Cost': float(data.get('optimal_cost', 0)),
                'Time_seconds': float(data.get('execution_time', 0))
            })
        
        results_df = pd.DataFrame(results_list)
        
        output = io.BytesIO()
        results_df.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='tsp_results.csv'
        )
    
    except Exception as e:
        print(f"Save error: {str(e)}", file=sys.stderr)
        return make_json_response(False, error=str(e)), 500

def process_tsp_dataset(df):
    """Process uploaded TSP dataset"""
    try:
        if 'city_from' in df.columns and 'city_to' in df.columns and 'distance' in df.columns:
            cities = sorted(set(df['city_from'].unique()) | set(df['city_to'].unique()))
            num_cities = len(cities)
            city_to_idx = {city: idx for idx, city in enumerate(cities)}
            
            distance_matrix = np.zeros((num_cities, num_cities))
            for _, row in df.iterrows():
                i = city_to_idx[row['city_from']]
                j = city_to_idx[row['city_to']]
                distance_matrix[i][j] = float(row['distance'])
                distance_matrix[j][i] = float(row['distance'])
        
        elif df.shape[0] == df.shape[1]:
            distance_matrix = df.values.astype(float)
            num_cities = len(distance_matrix)
        
        else:
            num_cities = min(10, len(df))
            distance_matrix = np.random.randint(1, 100, size=(num_cities, num_cities))
            distance_matrix = (distance_matrix + distance_matrix.T) // 2
            np.fill_diagonal(distance_matrix, 0)
        
        return {
            'distance_matrix': distance_matrix,
            'num_cities': num_cities
        }
    except Exception as e:
        print(f"Process dataset error: {str(e)}", file=sys.stderr)
        raise

if __name__ == '__main__':
    print("Starting Flask app...", file=sys.stderr)
    app.run(debug=True, host='0.0.0.0', port=5000)