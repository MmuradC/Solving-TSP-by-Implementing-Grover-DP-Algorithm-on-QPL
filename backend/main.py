from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import traceback
import json

from library.quantum_dp_solver import QuantumTSPSolver, ClassicalTSPSolver
from library.database_manager import DatabaseManager
from library.algorithm_comparison import router as comparison_router
from library.dataset_manager_api import router as dataset_router

app = FastAPI(title="Quantum TSP Solver API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_manager = DatabaseManager()

app.include_router(comparison_router)
app.include_router(dataset_router)

@app.get("/")
def read_root():
    return {
        "message": "Quantum TSP Solver API",
        "version": "2.0.0",
        "endpoints": [
            "/api/solve",
            "/api/compare",
            "/api/compare-all",
            "/api/instances",
            "/api/statistics",
            "/api/dataset/upload",
            "/api/dataset/progress",
            "/api/dataset/statistics"
        ]
    }

@app.post("/api/solve")
async def solve_tsp(request: Request):
    try:
        data = await request.json()
        cost_matrix = np.array(data['cost_matrix'])
        quantum_threshold = data.get('quantum_threshold', 3)
        algorithm = data.get('algorithm', 'quantum')
        
        if algorithm == "quantum":
            solver = QuantumTSPSolver(
                cost_matrix=cost_matrix,
                use_quantum_threshold=quantum_threshold
            )
        else:
            solver = ClassicalTSPSolver(cost_matrix=cost_matrix)
        
        result = solver.solve()

        db_manager.save_result(
            algorithm=algorithm,
            city_count=len(cost_matrix),
            cost=result['cost'],
            time=result['time'],
            path=result['path'],
            quantum_calls=result.get('quantum_calls', 0),
            classical_calls=result.get('classical_calls', 0),
            dp_states=result.get('dp_states', 0),
        )

        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compare")
async def compare_algorithms(request: Request):
    try:
        data = await request.json()
        cost_matrix = np.array(data['cost_matrix'])
        quantum_threshold = data.get('quantum_threshold', 3)
        
        classical_solver = ClassicalTSPSolver(cost_matrix=cost_matrix)
        classical_result = classical_solver.solve()
        
        quantum_solver = QuantumTSPSolver(
            cost_matrix=cost_matrix,
            use_quantum_threshold=quantum_threshold
        )
        quantum_result = quantum_solver.solve()
        
        n = len(cost_matrix)
        theoretical_speedup = (2**n) / (2**(n/2))
        
        return {
            "classical": classical_result,
            "quantum": quantum_result,
            "speedup": theoretical_speedup,
            "quantum_advantage": quantum_result['quantum_calls'] > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/instances")
async def get_instances():
    try:
        instances = db_manager.get_all_instances()
        return {"instances": instances}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/instances")
async def save_instance(request: Request):
    try:
        data = await request.json()
        db_manager.save_instance(
            name=data['name'],
            size=data['size'],
            cost_matrix=data['cost_matrix']
        )
        return {"message": "Instance saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/statistics")
async def get_statistics():
    try:
        stats = db_manager.get_statistics()
        return stats
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)