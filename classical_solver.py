import numpy as np
import time
from itertools import permutations
import heapq

class ClassicalTSPSolver:
    """Classical TSP solving algorithms for comparison"""
    
    def __init__(self, distance_matrix):
        self.distance_matrix = np.array(distance_matrix)
        self.num_cities = len(distance_matrix)
    
    def held_karp(self):
        """Held-Karp dynamic programming algorithm - with timeout protection"""
        start_time = time.time()
        
        n = self.num_cities
        
        # For very large problems, fall back to branch and bound
        if n > 15:
            print(f"Problem too large for Held-Karp ({n} cities), using Branch & Bound instead")
            return self.branch_and_bound()
        
        C = {}
        
        # Base case
        for k in range(1, n):
            C[(1 << k, k)] = (self.distance_matrix[0][k], 0)
        
        # Build up solutions
        for subset_size in range(2, n):
            # Check timeout every iteration
            if time.time() - start_time > 30:  # 30 second timeout
                print("Held-Karp timeout, switching to greedy...")
                return self.greedy()
            
            for subset in range(1, 1 << n):
                if not (subset & 1) or bin(subset).count('1') != subset_size:
                    continue
                
                for k in range(1, n):
                    if not (subset & (1 << k)):
                        continue
                    
                    prev = subset & ~(1 << k)
                    min_cost = float('inf')
                    min_prev = 0
                    
                    for m in range(1, n):
                        if not (prev & (1 << m)):
                            continue
                        
                        cost = C.get((prev, m), (float('inf'), 0))[0] + \
                            self.distance_matrix[m][k]
                        
                        if cost < min_cost:
                            min_cost = cost
                            min_prev = m
                    
                    C[(subset, k)] = (min_cost, min_prev)
        
        # Find minimum cost tour
        bits = (1 << n) - 1
        min_cost = float('inf')
        last = 0
        
        for k in range(1, n):
            cost = C.get((bits, k), (float('inf'), 0))[0] + self.distance_matrix[k][0]
            if cost < min_cost:
                min_cost = cost
                last = k
        
        # Reconstruct tour
        tour = []
        subset = bits
        
        while last != 0:
            tour.append(int(last))
            prev_subset = subset & ~(1 << last)
            last = C.get((subset, last), (0, 0))[1]
            subset = prev_subset
        
        tour.append(0)
        tour.reverse()
        
        execution_time = time.time() - start_time
        
        return {
            'optimal_tour': tour,
            'optimal_cost': float(min_cost),
            'execution_time': execution_time
        }
    
    def branch_and_bound(self):
        """Branch and bound algorithm"""
        start_time = time.time()
        
        n = self.num_cities
        
        # Priority queue: (lower_bound, level, path, visited)
        pq = [(0, 0, [0], {0})]
        best_cost = float('inf')
        best_path = None
        
        while pq:
            lb, level, path, visited = heapq.heappop(pq)
            
            if lb >= best_cost:
                continue
            
            if level == n - 1:
                # Complete the tour
                total_cost = sum(
                    self.distance_matrix[path[i]][path[i+1]]
                    for i in range(len(path) - 1)
                )
                total_cost += self.distance_matrix[path[-1]][path[0]]
                
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_path = path + [0]
                continue
            
            current = path[-1]
            
            for next_city in range(n):
                if next_city in visited:
                    continue
                
                # Calculate lower bound
                new_cost = lb + self.distance_matrix[current][next_city]
                
                # Add MST lower bound for remaining cities
                remaining = set(range(n)) - visited - {next_city}
                if remaining:
                    mst_cost = self._mst_lower_bound(remaining, next_city)
                    new_cost += mst_cost
                
                if new_cost < best_cost:
                    heapq.heappush(pq, (
                        new_cost,
                        level + 1,
                        path + [next_city],
                        visited | {next_city}
                    ))
        
        execution_time = time.time() - start_time
        
        return {
            'optimal_tour': best_path if best_path else list(range(n)) + [0],
            'optimal_cost': best_cost if best_cost != float('inf') else 0,
            'execution_time': execution_time
        }
    
    def greedy(self):
        """Greedy nearest neighbor algorithm"""
        start_time = time.time()
        
        n = self.num_cities
        visited = {0}
        tour = [0]
        current = 0
        total_cost = 0
        
        while len(visited) < n:
            nearest = None
            nearest_dist = float('inf')
            
            for city in range(n):
                if city not in visited:
                    dist = self.distance_matrix[current][city]
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest = city
            
            if nearest is not None:
                tour.append(nearest)
                visited.add(nearest)
                total_cost += nearest_dist
                current = nearest
        
        # Return to start
        tour.append(0)
        total_cost += self.distance_matrix[current][0]
        
        execution_time = time.time() - start_time
        
        return {
            'optimal_tour': tour,
            'optimal_cost': total_cost,
            'execution_time': execution_time
        }
    
    def nearest_neighbor(self):
        """Nearest neighbor heuristic (same as greedy)"""
        return self.greedy()
    
    def _generate_subsets(self, n, size):
        """Generate all subsets of given size containing city 0"""
        for i in range(1 << n):
            if bin(i).count('1') == size and (i & 1):
                yield i
    
    def _reconstruct_path(self, C, bits, last):
        """Reconstruct optimal path from DP table"""
        path = []
        subset = bits
        
        while last != 0:
            path.append(last)
            prev_subset = subset & ~(1 << last)
            last = C.get((subset, last), (0, 0))[1]
            subset = prev_subset
        
        path.append(0)
        path.reverse()
        
        return path
    
    def _mst_lower_bound(self, cities, start):
        """Calculate MST lower bound for remaining cities"""
        if not cities:
            return 0
        
        cities_list = list(cities)
        n = len(cities_list)
        
        if n == 0:
            return 0
        
        # Prim's algorithm
        in_mst = {cities_list[0]}
        total_cost = 0
        
        while len(in_mst) < n:
            min_edge = float('inf')
            
            for u in in_mst:
                for v in cities_list:
                    if v not in in_mst:
                        cost = self.distance_matrix[u][v]
                        if cost < min_edge:
                            min_edge = cost
                            next_vertex = v
            
            if min_edge != float('inf'):
                in_mst.add(next_vertex)
                total_cost += min_edge
        
        return total_cost