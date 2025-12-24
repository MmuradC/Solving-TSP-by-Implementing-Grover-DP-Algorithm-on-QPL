import React, { useState, useEffect } from 'react';
import { Play, RefreshCw, Download, Info, Zap, Cpu, TrendingUp, Database, Activity, FileUp, X, BarChart3 } from 'lucide-react';

function App() {
  const [cityCount, setCityCount] = useState(5);
  const [costMatrix, setCostMatrix] = useState([]);
  const [quantumThreshold, setQuantumThreshold] = useState(3);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [showCircuit, setShowCircuit] = useState(false);
  const [datasetProgress, setDatasetProgress] = useState([]);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [algorithmResults, setAlgorithmResults] = useState([]);

  useEffect(() => {
    generateMatrix();
    loadStatistics();
    loadDatasetProgress();
  }, [cityCount]);

  const loadStatistics = () => {
    fetch('http://localhost:8000/api/statistics')
      .then(res => res.json())
      .then(data => setStatistics(data))
      .catch(err => console.log('Stats unavailable'));
  };

  const loadDatasetProgress = () => {
    fetch('http://localhost:8000/api/dataset/progress')
      .then(res => res.json())
      .then(data => setDatasetProgress(data.progress || []))
      .catch(err => console.log('Progress unavailable'));
  };

  const generateMatrix = () => {
    const n = cityCount;
    const matrix = Array(n).fill(0).map(() => Array(n).fill(0));
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const cost = Math.floor(Math.random() * 40) + 10;
        matrix[i][j] = cost;
        matrix[j][i] = cost;
      }
    }
    setCostMatrix(matrix);
  };

  const updateMatrixCell = (i, j, value) => {
    const newMatrix = costMatrix.map(row => [...row]);
    const val = parseInt(value) || 0;
    newMatrix[i][j] = val;
    newMatrix[j][i] = val;
    setCostMatrix(newMatrix);
  };

  const solveTSP = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cost_matrix: costMatrix,
          quantum_threshold: quantumThreshold,
          algorithm: 'quantum'
        })
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const compareAllAlgorithms = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/compare-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cost_matrix: costMatrix,
          quantum_threshold: quantumThreshold
        })
      });
      const data = await response.json();
      setAlgorithmResults(data.algorithms);
      setComparison({ speedup: data.speedup });
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const text = e.target.result;
        const response = await fetch('http://localhost:8000/api/dataset/upload-text', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: text,
            filename: file.name
          })
        });
        const data = await response.json();
        alert(`Uploaded ${data.num_instances} instances`);
        setShowUploadModal(false);
        loadDatasetProgress();
      } catch (error) {
        alert('Error uploading file');
      }
    };
    reader.readAsText(file);
  };

  const saveInstance = async () => {
    try {
      await fetch('http://localhost:8000/api/instances', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: `TSP_${cityCount}_${Date.now()}`,
          size: cityCount,
          cost_matrix: costMatrix
        })
      });
      alert('Instance saved!');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const QuantumCircuit = () => {
    const iterations = Math.ceil(Math.PI / 4 * Math.sqrt(Math.pow(2, cityCount)));
    const successProb = (Math.sin((2 * 1 + 1) * Math.asin(1 / Math.sqrt(Math.pow(2, cityCount)))) ** 2 * 100).toFixed(1);
    const speedup = Math.sqrt(Math.pow(2, cityCount)).toFixed(2);

    return (
      <div className="bg-gray-950 rounded-lg p-6 border border-cyan-500/30">
        <h3 className="text-xl font-bold text-cyan-400 mb-4 flex items-center gap-2">
          <Zap className="w-6 h-6" />
          Quantum Circuit - Grover's Algorithm
        </h3>
        <div className="font-mono text-sm text-gray-300 overflow-x-auto">
          <pre className="text-cyan-400">
{`     ┌───┐     ┌─────────┐┌─┐
q_0: ┤ H ├──■──┤ Ry(θ_0) ├┤M├───
     ├───┤┌─┴─┐└─────────┘└╥┘
q_1: ┤ H ├┤ X ├─────■──────╫────
     ├───┤└───┘   ┌─┴─┐    ║ 
q_2: ┤ H ├────────┤ X ├────╫────
     └───┘        └───┘    ║ 

Grover Operator: G = (2|ψ⟩⟨ψ| - I) · O_f
Iterations: k = ${iterations}
Success Probability: ${successProb}%
Quantum Speedup: ${speedup}x`}
          </pre>
        </div>
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="bg-gray-900 p-3 rounded border border-gray-800">
            <div className="text-xs text-gray-500">Superposition</div>
            <div className="text-cyan-400 font-bold">H⊗{cityCount}</div>
          </div>
          <div className="bg-gray-900 p-3 rounded border border-gray-800">
            <div className="text-xs text-gray-500">Oracle Queries</div>
            <div className="text-green-400 font-bold">{results?.quantum_calls || iterations}</div>
          </div>
          <div className="bg-gray-900 p-3 rounded border border-gray-800">
            <div className="text-xs text-gray-500">Measurements</div>
            <div className="text-purple-400 font-bold">1024 shots</div>
          </div>
        </div>
      </div>
    );
  };

  const AlgorithmComparison = () => {
    if (!algorithmResults || algorithmResults.length === 0) return null;
    const maxTime = Math.max(...algorithmResults.map(a => a.time));
    const minCost = Math.min(...algorithmResults.map(a => a.cost));

    return (
      <div className="bg-gray-950 rounded-lg p-6 border border-gray-800">
        <h3 className="text-2xl font-bold text-cyan-400 mb-6 flex items-center gap-2">
          <TrendingUp className="w-6 h-6" />
          Algorithm Performance Comparison
        </h3>
        <div className="space-y-6">
          {algorithmResults.map((algo, idx) => (
            <div key={idx} className="space-y-2">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <span className="text-gray-200 font-semibold text-lg">{algo.name}</span>
                    {algo.cost === minCost && (
                      <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs font-bold">OPTIMAL</span>
                    )}
                  </div>
                  <div className="text-gray-500 text-sm mt-1">{algo.description}</div>
                  <div className="text-gray-400 text-xs mt-1">
                    Cost: <span className="text-cyan-400 font-semibold">{algo.cost}</span> | 
                    Complexity: <span className="text-purple-400 font-mono">{algo.complexity}</span>
                  </div>
                </div>
              </div>
              <div className="relative w-full bg-gray-900 rounded-full h-10 overflow-hidden border border-gray-800">
                <div
                  className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 flex items-center justify-between px-4 text-sm font-bold text-white transition-all duration-1000"
                  style={{ width: `${Math.min((algo.time / maxTime) * 100, 100)}%` }}
                >
                  <span>{algo.time.toFixed(4)}s</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const DatasetTable = () => (
    <div className="bg-gray-950 rounded-lg p-6 border border-gray-800">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-2xl font-bold text-cyan-400 flex items-center gap-2">
          <BarChart3 className="w-6 h-6" />
          Dataset Analysis Progress
        </h3>
        <button
          onClick={() => setShowUploadModal(true)}
          className="bg-cyan-600 hover:bg-cyan-700 px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <FileUp className="w-5 h-5" />
          Upload Dataset
        </button>
      </div>
      {datasetProgress.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <BarChart3 className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg">No dataset uploaded yet</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Instance</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Cities</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Distance</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Category</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Quantum</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Classical</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Speedup</th>
              </tr>
            </thead>
            <tbody>
              {datasetProgress.map((item, idx) => (
                <tr key={idx} className="border-b border-gray-900 hover:bg-gray-900/50">
                  <td className="py-3 px-4 text-gray-300 font-mono text-xs">{item.name}</td>
                  <td className="py-3 px-4 text-cyan-400 font-semibold">{item.num_cities}</td>
                  <td className="py-3 px-4 text-green-400 font-semibold">{item.total_distance}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      item.best_route_category === 'optimal' 
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {item.best_route_category}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-blue-400">{item.quantum_time}s</td>
                  <td className="py-3 px-4 text-orange-400">{item.classical_time}s</td>
                  <td className="py-3 px-4 text-purple-400 font-bold">{item.speedup}x</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const UploadModal = () => (
    showUploadModal && (
      <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
        <div className="bg-gray-900 rounded-lg p-8 max-w-2xl w-full border border-gray-800">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-2xl font-bold text-cyan-400">Upload Dataset</h3>
            <button onClick={() => setShowUploadModal(false)} className="text-gray-400 hover:text-white">
              <X className="w-6 h-6" />
            </button>
          </div>
          <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center">
            <FileUp className="w-12 h-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400 mb-4">Upload CSV file</p>
            <input type="file" accept=".csv" onChange={handleFileUpload} className="hidden" id="file-upload" />
            <label htmlFor="file-upload" className="bg-cyan-600 hover:bg-cyan-700 px-6 py-3 rounded-lg cursor-pointer inline-block">
              Choose File
            </label>
          </div>
        </div>
      </div>
    )
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        <header className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Zap className="w-12 h-12 text-cyan-400" />
            <h1 className="text-5xl font-bold text-cyan-400">Quantum TSP Solver</h1>
          </div>
          <p className="text-xl text-gray-400">Quantum-Enhanced Dynamic Programming</p>
        </header>

        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Database className="w-5 h-5 text-cyan-400" />
                <span className="text-gray-500 text-sm">Total Runs</span>
              </div>
              <div className="text-3xl font-bold text-cyan-400">{statistics.total_runs || 0}</div>
            </div>
            <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-5 h-5 text-green-400" />
                <span className="text-gray-500 text-sm">Avg Quantum Calls</span>
              </div>
              <div className="text-3xl font-bold text-green-400">{statistics.avg_quantum_calls?.toFixed(0) || 0}</div>
            </div>
            <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-purple-400" />
                <span className="text-gray-500 text-sm">Avg Classical Calls</span>
              </div>
              <div className="text-3xl font-bold text-purple-400">{statistics.avg_classical_calls?.toFixed(0) || 0}</div>
            </div>
            <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Cpu className="w-5 h-5 text-yellow-400" />
                <span className="text-gray-500 text-sm">Speedup</span>
              </div>
              <div className="text-3xl font-bold text-yellow-400">{comparison?.speedup?.toFixed(2) || '--'}x</div>
            </div>
          </div>
        )}

        <div className="bg-gray-950 border border-gray-800 rounded-2xl p-8 mb-8">
          <h2 className="text-3xl font-bold mb-6 flex items-center gap-3 text-cyan-400">
            <Cpu className="w-8 h-8" />
            Problem Definition
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-lg font-semibold mb-2 text-gray-400">Cities:</label>
              <input
                type="number"
                min="3"
                max="10"
                value={cityCount}
                onChange={(e) => setCityCount(parseInt(e.target.value) || 3)}
                className="w-full px-4 py-3 bg-gray-900 border-2 border-gray-700 rounded-lg text-white text-lg focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-lg font-semibold mb-2 text-gray-400">Quantum Threshold:</label>
              <input
                type="number"
                min="2"
                max="10"
                value={quantumThreshold}
                onChange={(e) => setQuantumThreshold(parseInt(e.target.value) || 2)}
                className="w-full px-4 py-3 bg-gray-900 border-2 border-gray-700 rounded-lg text-white text-lg focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>
          <div className="flex gap-4 mb-6">
            <button onClick={generateMatrix} className="flex-1 bg-gray-900 hover:bg-gray-800 border border-gray-700 px-6 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 text-gray-200">
              <RefreshCw className="w-5 h-5" />Generate
            </button>
            <button onClick={() => setShowCircuit(!showCircuit)} className="flex-1 bg-cyan-900 hover:bg-cyan-800 border border-cyan-700 px-6 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 text-gray-200">
              <Zap className="w-5 h-5" />{showCircuit ? 'Hide' : 'Show'} Circuit
            </button>
          </div>
          {showCircuit && <QuantumCircuit />}
          {costMatrix.length > 0 && (
            <div className="overflow-x-auto mt-6">
              <h3 className="text-xl font-semibold mb-4 text-gray-400">Cost Matrix:</h3>
              <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${cityCount}, minmax(60px, 1fr))` }}>
                {costMatrix.map((row, i) => row.map((cell, j) => (
                  <input
                    key={`${i}-${j}`}
                    type="number"
                    value={cell}
                    disabled={i === j}
                    onChange={(e) => updateMatrixCell(i, j, e.target.value)}
                    className={`w-full px-2 py-2 text-center rounded border-2 text-white font-semibold ${i === j ? 'bg-black border-gray-800 cursor-not-allowed text-gray-600' : 'bg-gray-900 border-gray-700 focus:border-cyan-500'} focus:outline-none`}
                  />
                )))}
              </div>
            </div>
          )}
        </div>

        <div className="flex flex-wrap gap-4 mb-8">
          <button onClick={solveTSP} disabled={loading} className="flex-1 min-w-[200px] bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 disabled:opacity-50 px-8 py-4 rounded-xl font-bold text-xl flex items-center justify-center gap-3">
            {loading ? <RefreshCw className="w-6 h-6 animate-spin" /> : <Play className="w-6 h-6" />}Solve
          </button>
          <button onClick={compareAllAlgorithms} disabled={loading} className="flex-1 min-w-[200px] bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 px-8 py-4 rounded-xl font-bold text-xl flex items-center justify-center gap-3">
            <TrendingUp className="w-6 h-6" />Compare All
          </button>
          <button onClick={saveInstance} className="flex-1 min-w-[200px] bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700 px-8 py-4 rounded-xl font-bold text-xl flex items-center justify-center gap-3">
            <Download className="w-6 h-6" />Save
          </button>
        </div>

        <DatasetTable />
        {algorithmResults.length > 0 && (
          <div className="mt-8">
            <AlgorithmComparison />
          </div>
        )}

        {results && (
          <div className="bg-gray-950 border border-gray-800 rounded-2xl p-8 mt-8">
            <h2 className="text-3xl font-bold mb-6 text-cyan-400">Results</h2>
            <div className="mb-6">
              <div className="flex items-center justify-center gap-3 flex-wrap">
                {results.path && results.path.map((city, idx) => (
                  <React.Fragment key={idx}>
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-2xl font-bold">{city}</div>
                    {idx < results.path.length - 1 && <div className="text-3xl text-cyan-400">→</div>}
                  </React.Fragment>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-900 p-6 rounded-xl text-center border-2 border-cyan-500">
                <div className="text-4xl font-bold text-cyan-400 mb-2">{results.cost}</div>
                <div className="text-gray-500">Cost</div>
              </div>
              <div className="bg-gray-900 p-6 rounded-xl text-center border-2 border-blue-500">
                <div className="text-4xl font-bold text-blue-400 mb-2">{results.dp_states || 0}</div>
                <div className="text-gray-500">DP States</div>
              </div>
              <div className="bg-gray-900 p-6 rounded-xl text-center border-2 border-green-500">
                <div className="text-4xl font-bold text-green-400 mb-2">{results.quantum_calls || 0}</div>
                <div className="text-gray-500">Quantum</div>
              </div>
              <div className="bg-gray-900 p-6 rounded-xl text-center border-2 border-purple-500">
                <div className="text-4xl font-bold text-purple-400 mb-2">{results.time?.toFixed(4)}s</div>
                <div className="text-gray-500">Time</div>
              </div>
            </div>
          </div>
        )}
        <UploadModal />
      </div>
    </div>
  );
}

export default App;