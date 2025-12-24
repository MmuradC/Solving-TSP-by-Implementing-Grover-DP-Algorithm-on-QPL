# Solving-TSP-by-Implementing-Grover-DP-Algorithm-on-QPL

Slides:
- https://docs.google.com/presentation/d/1mrBZa63AbNxeMC8a29v-BvrVYQ9TIWAed5A3QlzWgaM/edit?slide=id.g3ae5705265d_0_147#slide=id.g3ae5705265d_0_147

Docs:
- https://docs.google.com/document/d/1K35Oy6iyP-VmlH3E_xSq9JSzytDvEufT0dcq8N18vCA/edit?tab=t.0

## Installation

1. Install backend dependencies:
```bash
pip install -r requirements.txt

```

2. Run the backend server:
```bash (1)
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

3. Run the frontend server:
```bash (2)
cd frontend
npm install
npm run dev
```

4. For the frontend, open the React artifact in Claude.ai or deploy it separately.

## API Endpoints

- `GET /` - API information
- `POST /api/solve` - Solve TSP instance
- `POST /api/compare` - Compare quantum vs classical algorithms
- `GET /api/instances` - Get saved instances
- `POST /api/instances` - Save new instance
- `GET /api/statistics` - Get performance statistics

## Algorithm Complexity

- **Classical DP**: O(n² · 2ⁿ)
- **Quantum-Enhanced DP**: O*(⌈c⌉⁴ · √(2ⁿ))

Where n is the number of cities and c is the maximum edge weight.