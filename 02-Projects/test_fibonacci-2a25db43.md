---
type: imported
source: C:\Users\Jaques\Documents\test_fibonacci.py
imported: 2026-07-24T11:03:23.201437
file_type: .py
---

# test_fibonacci.py

**Original:** `C:\Users\Jaques\Documents\test_fibonacci.py`

## Content

```py
def fibonacci(n: int) -> int:
    """Generate nth Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def optimized_fibonacci(n: int, memo: dict = None) -> int:
    """Optimized Fibonacci with memoization"""
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = optimized_fibonacci(n - 1, memo) + optimized_fibonacci(n - 2, memo)
    return memo[n]

# Test performance
if __name__ == "__main__":
    import time
    
    # Original approach
    start = time.time()
    result = fibonacci(30)
    elapsed = time.time() - start
    print(f"fibonacci(30) = {result}, took {elapsed:.3f}s")
    
    # Optimized approach
    start = time.time()
    result = optimized_fibonacci(30)
    elapsed = time.time() - start
    print(f"optimized_fibonacci(30) = {result}, took {elapsed:.3f}s")

```
