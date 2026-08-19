# Auto-generated Code Vault for 'RadixSort' [Python]

"""
Radix Sort implementation for integers (including negative numbers).

The algorithm works by sorting the numbers digit by digit, starting from the
least significant digit and moving towards the most significant digit. For
each digit position a stable counting sort is used as the sub‑routine.

Features
--------
* Handles positive and negative integers.
* Works with any iterable of integers.
* Returns a new sorted list, leaving the input untouched.
* Fully typed and documented.
* Includes a simple command‑line interface for quick testing.

Example
-------
>>> from radix_sort import radix_sort
>>> radix_sort([170, 45, 75, -90, -802, 24, 2, 66])
[-802, -90, 2, 24, 45, 66, 75, 170]
"""

from typing import List, Iterable


def _counting_sort_by_digit(arr: List[int], exp: int) -> List[int]:
    """
    Perform a stable counting sort of ``arr`` according to the digit
    represented by ``exp`` (10**k where k is the digit position).

    Parameters
    ----------
    arr: List[int]
        The list of non‑negative integers to sort.
    exp: int
        The exponent corresponding to the digit position (1, 10, 100, ...).

    Returns
    -------
    List[int]
        A new list sorted by the current digit.
    """
    # Since decimal digits range from 0 to 9
    output = [0] * len(arr)
    count = [0] * 10

    # Store count of occurrences in count[]
    for number in arr:
        index = (number // exp) % 10
        count[index] += 1

    # Change count[i] so that count[i] contains the actual
    # position of this digit in output[]
    for i in range(1, 10):
        count[i] += count[i - 1]

    # Build the output array by iterating from right to left
    # to maintain stability.
    for number in reversed(arr):
        index = (number // exp) % 10
        count[index] -= 1
        output[count[index]] = number

    return output


def _radix_sort_non_negative(arr: List[int]) -> List[int]:
    """
    Radix sort for a list that contains only non‑negative integers.

    Parameters
    ----------
    arr: List[int]
        List of non‑negative integers.

    Returns
    -------
    List[int]
        Sorted list.
    """
    if not arr:
        return []

    # Find the maximum number to know the number of digits
    max_num = max(arr)

    exp = 1
    result = list(arr)  # Work on a copy
    while max_num // exp > 0:
        result = _counting_sort_by_digit(result, exp)
        exp *= 10
    return result


def radix_sort(data: Iterable[int]) -> List[int]:
    """
    Public API: sort any iterable of integers using radix sort.

    The implementation separates the input into non‑negative and negative
    numbers. Negative numbers are transformed to positive by taking the
    absolute value, sorted, then re‑negated and reversed to preserve order.

    Parameters
    ----------
    data: Iterable[int]
        The collection of integers to sort.

    Returns
    -------
    List[int]
        A new list containing the sorted integers.
    """
    # Convert to list to allow multiple passes over the data
    arr = list(data)

    # Separate negatives and non‑negatives
    negatives = [-x for x in arr if x < 0]   # Store as positive for sorting
    non_negatives = [x for x in arr if x >= 0]

    # Sort each part individually
    sorted_negatives = _radix_sort_non_negative(negatives)
    sorted_non_negatives = _radix_sort_non_negative(non_negatives)

    # Re‑negate the sorted negatives and reverse to get correct order
    sorted_negatives = [-x for x in reversed(sorted_negatives)]

    # Combine results
    return sorted_negatives + sorted_non_negatives


def _run_demo() -> None:
    """
    Simple demonstration executed when the module is run as a script.
    """
    import argparse
    import sys
    import random

    parser = argparse.ArgumentParser(
        description="Demonstrate radix sort on a list of integers."
    )
    parser.add_argument(
        "numbers",
        nargs="*",
        type=int,
        help="Numbers to sort. If omitted, a random list will be generated.",
    )
    parser.add_argument(
        "-n",
        "--size",
        type=int,
        default=20,
        help="Size of the random list when no numbers are given (default: 20).",
    )
    parser.add_argument(
        "-r",
        "--range",
        type=int,
        nargs=2,
        metavar=("MIN", "MAX"),
        default=[-1000, 1000],
        help="Range for random numbers (default: -1000 1000).",
    )
    args = parser.parse_args()

    if args.numbers:
        input_list = args.numbers
    else:
        low, high = args.range
        input_list = [random.randint(low, high) for _ in range(args.size)]

    print("Input :", input_list)
    sorted_list = radix_sort(input_list)
    print("Sorted:", sorted_list)


if __name__ == "__main__":
    _run_demo()
