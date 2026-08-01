# Auto-generated Code Vault for 'StringReversal' [Python]

# string_reversal.py

def reverse_string(input_string):
    """
    Reverses the input string.

    Args:
        input_string (str): The string to be reversed.

    Returns:
        str: The reversed string.
    """
    return input_string[::-1]

def main():
    # Define the input string
    input_string = "Agentic RAG is awesome"

    # Print the original string
    print("Original String: ", input_string)

    # Reverse the string
    reversed_string = reverse_string(input_string)

    # Print the reversed string
    print("Reversed String: ", reversed_string)

if __name__ == "__main__":
    main()
