# Auto-generated Code Vault for 'Factorial' [Python]

#!/usr/bin/env python3
"""
Calculate the factorial of 15 and display the result.

This script defines a reusable factorial function, validates input,
and prints the exact value of 15!.
"""

def factorial(n: int) -> int:
    """
    Compute the factorial of a non‑negative integer n.

    Parameters
    ----------
    n : int
        Non‑negative integer whose factorial is to be calculated.

    Returns
    -------
    int
        The factorial of n (n!).

    Raises
    ------
    ValueError
        If n is negative.
    """
    if n < 0:
        raise ValueError("Factorial is undefined for negative integers")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def main() -> None:
    """Calculate and print 15!."""
    number = 15
    result = factorial(number)
    print(f"{number}! = {result}")

if __name__ == "__main__":
    main()
