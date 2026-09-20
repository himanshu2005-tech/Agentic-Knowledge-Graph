# Auto-generated Code Vault for 'FibonacciNumber' [Python]

#!/usr/bin/env python3
"""
FibonacciNumber Module

This module provides a fast and reliable implementation for computing
the nth Fibonacci number using the fast‑doubling method, which runs in
O(log n) time and O(1) additional space. The script, when executed
directly, calculates and prints the 50th Fibonacci number.

Author: Senior Python Engineer
"""

from __future__ import annotations
from typing import Tuple

def _fib_fast_doubling(n: int) -> Tuple[int, int]:
    """
    Helper that returns a tuple (F(n), F(n+1)) using the fast‑doubling
    recurrence relations:

        F(2k)   = F(k) * [2*F(k+1) − F(k)]
        F(2k+1) = F(k+1)^2 + F(k)^2

    Parameters
    ----------
    n: int
        The index of the Fibonacci number (must be >= 0).

    Returns
    -------
    Tuple[int, int]
        (F(n), F(n+1))
    """
    if n == 0:
        return (0, 1)
    else:
        a, b = _fib_fast_doubling(n // 2)
        c = a * ((b << 1) - a)          # F(2k) = F(k) * (2*F(k+1) − F(k))
        d = a * a + b * b               # F(2k+1) = F(k)^2 + F(k+1)^2
        if n & 1:
            return (d, c + d)           # (F(2k+1), F(2k+2))
        else:
            return (c, d)               # (F(2k), F(2k+1))

def fibonacci(n: int) -> int:
    """
    Compute the nth Fibonacci number (0‑based index) efficiently.

    Parameters
    ----------
    n: int
        The position in the Fibonacci sequence (must be non‑negative).

    Returns
    -------
    int
        The nth Fibonacci number.

    Raises
    ------
    ValueError
        If `n` is negative.
    """
    if n < 0:
        raise ValueError("Fibonacci number is not defined for negative indices")
    fn, _ = _fib_fast_doubling(n)
    return fn

def main() -> None:
    """
    Entry point for the script. Calculates and prints the 50th Fibonacci number.
    """
    target_index = 50
    result = fibonacci(target_index)
    print(f"The {target_index}th Fibonacci number is: {result}")

if __name__ == "__main__":
    main()
