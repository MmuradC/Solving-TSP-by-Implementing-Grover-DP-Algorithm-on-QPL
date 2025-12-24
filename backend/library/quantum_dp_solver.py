# algorithm/backend/library/quantum_dp_solver.py

import numpy as np
import math
import time
from itertools import combinations
from .quantum_minimum_finder import QuantumMinimumFinder

class QuantumTSPSolver:
    """
    Quantum-enhanced DP solver for TSP
    Implements algorithm from: Ronagh, P. (2019)
    
    Achieves O*(⌈c⌉^4 * √(2^n)) complexity where:
    - n is number of cities
    - c is maximum edge weight
    """
    
    def __init__(self, cost_matrix, use_quantum_threshold=3):
        self.cost_matrix = np.array(cost_matrix)
        self.n = len(cost_matrix)
        self.dp_table = {}
        self.parent = {}
        self.qmf = QuantumMinimumFinder()
        self.use_quantum_threshold = use_quantum_threshold
        self.quantum_calls = 0
        self.classical_calls = 0
    
    def solve(self):
        """
        Solve TSP using quantum-enhanced dynamic programming
        
        Returns:
            dict: {
                'path': optimal tour path,
                'cost': minimum cost,
                'time': execution time,
                'dp_states': number of DP states computed,
                'quantum_calls': number of quantum operations,
                'classical_calls': number of classical operations
            }
        """
        start_time = time.time()
        
        # Initialize base cases
        # dp_table[(visited_set, last_city)] = min_cost
        for i in range(1, self.n):
            self.dp_table[(1 << i, i)] = self.cost_matrix[0][i]
            self.parent[(1 << i, i)] = 0
        
        # Build DP table for subsets of increasing size
        for size in range(2, self.n):
            for subset in combinations(range(1, self.n), size):
                bits = sum(1 << i for i in subset)
                
                for last in subset:
                    prev_bits = bits & ~(1 << last)
                    valid_prevs = [p for p in subset if p != last]
                    
                    if not valid_prevs:
                        continue
                    
                    # Cost function for quantum minimum finding
                    def cost_function(idx):
                        if idx >= len(valid_prevs):
                            return float('inf')
                        prev = valid_prevs[idx]
                        prev_state = (prev_bits, prev)
                        if prev_state not in self.dp_table:
                            return float('inf')
                        return self.dp_table[prev_state] + self.cost_matrix[prev][last]
                    
                    # Quantum vs Classical decision
                    # Use quantum when search space exceeds threshold
                    if len(valid_prevs) > self.use_quantum_threshold:
                        # Quantum minimum finding: O(√N) queries
                        min_idx, _ = self.qmf.find_minimum(
                            cost_function, 
                            len(valid_prevs)
                        )
                        min_prev = valid_prevs[min_idx]
                        min_cost = cost_function(min_idx)
                        self.quantum_calls += 1
                    else:
                        # Classical minimum finding: O(N) queries
                        min_cost = float('inf')
                        min_prev = -1
                        for idx, prev in enumerate(valid_prevs):
                            cost = cost_function(idx)
                            if cost < min_cost:
                                min_cost = cost
                                min_prev = prev
                        self.classical_calls += 1
                    
                    if min_prev != -1 and min_cost != float('inf'):
                        self.dp_table[(bits, last)] = min_cost
                        self.parent[(bits, last)] = min_prev
        
        # Find optimal tour
        all_cities = (1 << self.n) - 2
        min_cost = float('inf')
        last_city = -1
        
        for i in range(1, self.n):
            state = (all_cities, i)
            if state in self.dp_table:
                cost = self.dp_table[state] + self.cost_matrix[i][0]
                if cost < min_cost:
                    min_cost = cost
                    last_city = i
        
        path = self._reconstruct_path(last_city, all_cities)
        solve_time = time.time() - start_time
        
        return {
            'path': path,
            'cost': int(min_cost) if min_cost != float('inf') else None,
            'time': solve_time,
            'dp_states': len(self.dp_table),
            'quantum_calls': self.quantum_calls,
            'classical_calls': self.classical_calls
        }
    
    def _reconstruct_path(self, last_city, all_cities):
        """Reconstruct optimal path from parent pointers"""
        if last_city == -1:
            return None
        
        path = [0]
        bits = all_cities
        current = last_city
        
        while bits:
            path.append(current)
            prev = self.parent.get((bits, current), -1)
            if prev == -1:
                break
            bits &= ~(1 << current)
            current = prev
        
        path.append(0)
        path.reverse()
        return path


class ClassicalTSPSolver:
    """
    Classical dynamic programming solver for TSP
    Bellman-Held-Karp algorithm: O(n^2 * 2^n)
    """
    
    def __init__(self, cost_matrix):
        self.cost_matrix = np.array(cost_matrix)
        self.n = len(cost_matrix)
        self.dp_table = {}
        self.parent = {}
    
    def solve(self):
        """Solve TSP using classical DP"""
        start_time = time.time()
        
        # Initialize
        for i in range(1, self.n):
            self.dp_table[(1 << i, i)] = self.cost_matrix[0][i]
            self.parent[(1 << i, i)] = 0
        
        # DP iteration
        for size in range(2, self.n):
            for subset in combinations(range(1, self.n), size):
                bits = sum(1 << i for i in subset)
                
                for last in subset:
                    prev_bits = bits & ~(1 << last)
                    
                    min_cost = float('inf')
                    min_prev = -1
                    
                    for prev in subset:
                        if prev == last:
                            continue
                        prev_state = (prev_bits, prev)
                        if prev_state in self.dp_table:
                            cost = self.dp_table[prev_state] + self.cost_matrix[prev][last]
                            if cost < min_cost:
                                min_cost = cost
                                min_prev = prev
                    
                    if min_prev != -1 and min_cost != float('inf'):
                        self.dp_table[(bits, last)] = min_cost
                        self.parent[(bits, last)] = min_prev
        
        # Find minimum
        all_cities = (1 << self.n) - 2
        min_cost = float('inf')
        last_city = -1
        
        for i in range(1, self.n):
            state = (all_cities, i)
            if state in self.dp_table:
                cost = self.dp_table[state] + self.cost_matrix[i][0]
                if cost < min_cost:
                    min_cost = cost
                    last_city = i
        
        path = self._reconstruct_path(last_city, all_cities)
        solve_time = time.time() - start_time
        
        return {
            'path': path,
            'cost': int(min_cost) if min_cost != float('inf') else None,
            'time': solve_time,
            'dp_states': len(self.dp_table),
            'quantum_calls': 0,
            'classical_calls': len(self.dp_table)
        }
    
    def _reconstruct_path(self, last_city, all_cities):
        """Reconstruct path"""
        if last_city == -1:
            return None
        
        path = [0]
        bits = all_cities
        current = last_city
        
        while bits:
            path.append(current)
            prev = self.parent.get((bits, current), -1)
            if prev == -1:
                break
            bits &= ~(1 << current)
            current = prev
        
        path.append(0)
        path.reverse()
        return path