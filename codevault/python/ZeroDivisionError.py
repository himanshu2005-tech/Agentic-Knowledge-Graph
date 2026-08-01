# Auto-generated Code Vault for 'ZeroDivisionError' [Python]

# Define a function to divide two numbers
def divide_numbers(dividend, divisor):
    """
    Divide two numbers and return the result.

    Args:
        dividend (float): The number being divided.
        divisor (float): The number by which we are dividing.

    Returns:
        float: The result of the division.
    """
    try:
        # Attempt to divide the numbers
        result = dividend / divisor
        return result
    except ZeroDivisionError:
        # Handle the ZeroDivisionError exception
        print("Error: Cannot divide by zero.")
        return None

# Define a main function to test the divide_numbers function
def main():
    # Test the divide_numbers function with valid input
    print("Testing with valid input:")
    result = divide_numbers(10, 2)
    if result is not None:
        print(f"10 divided by 2 is {result}")

    # Test the divide_numbers function with invalid input
    print("\nTesting with invalid input:")
    result = divide_numbers(10, 0)
    if result is None:
        print("Result is None due to ZeroDivisionError")

# Call the main function
if __name__ == "__main__":
    main()
