// Auto-generated Code Vault for 'FibonacciSequence' [Cpp]

#include <iostream>
#include <vector>

/**
 * Function to calculate the nth Fibonacci number using dynamic programming.
 * 
 * @param n The position of the Fibonacci number to calculate.
 * @return The nth Fibonacci number.
 */
int fibonacci(int n) {
    // Create a vector to store the Fibonacci numbers.
    std::vector<int> fib(n + 1);
    
    // Base cases: fib(0) = 0, fib(1) = 1.
    fib[0] = 0;
    if (n >= 1) {
        fib[1] = 1;
    }
    
    // Calculate the Fibonacci numbers from 2 to n.
    for (int i = 2; i <= n; i++) {
        // Each Fibonacci number is the sum of the two preceding ones.
        fib[i] = fib[i - 1] + fib[i - 2];
    }
    
    // Return the nth Fibonacci number.
    return fib[n];
}

/**
 * Function to print the Fibonacci sequence up to the nth number.
 * 
 * @param n The number of Fibonacci numbers to print.
 */
void printFibonacciSequence(int n) {
    for (int i = 0; i <= n; i++) {
        std::cout << "Fibonacci(" << i << ") = " << fibonacci(i) << std::endl;
    }
}

int main() {
    int n;
    std::cout << "Enter the number of Fibonacci numbers to generate: ";
    std::cin >> n;
    
    printFibonacciSequence(n);
    
    return 0;
}
