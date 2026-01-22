#!/bin/bash

echo "Testing API endpoints..."

# Test randomize
echo "1. Testing /randomize..."
curl -X POST http://localhost:5000/randomize \
  -H "Content-Type: application/json" \
  -d '{"num_cities": 5}' \
  -w "\nHTTP Status: %{http_code}\n"

echo -e "\n---\n"

# Test show_circuit
echo "2. Testing /show_circuit..."
curl -X POST http://localhost:5000/show_circuit \
  -w "\nHTTP Status: %{http_code}\n"

echo -e "\n---\n"

# Test solve_quantum
echo "3. Testing /solve_quantum..."
curl -X POST http://localhost:5000/solve_quantum \
  -w "\nHTTP Status: %{http_code}\n"

