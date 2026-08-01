# Auto-generated Code Vault for 'PalindromeChecker' [Python]

class PalindromeChecker:
    def __init__(self, number):
        """
        Initialize the PalindromeChecker with a number.
        
        Args:
            number (int): The number to check for palindrome.
        """
        self.number = number

    def is_palindrome(self):
        """
        Check if the number is a palindrome.
        
        Returns:
            bool: True if the number is a palindrome, False otherwise.
        """
        # Convert the number to a string to easily reverse it
        str_number = str(self.number)
        
        # Compare the string with its reverse
        return str_number == str_number[::-1]


def main():
    # Create a PalindromeChecker instance with the number 10
    checker = PalindromeChecker(10)
    
    # Check if the number is a palindrome
    result = checker.is_palindrome()
    
    # Print the result
    print(f"Is {checker.number} a palindrome? {result}")


if __name__ == "__main__":
    main()
