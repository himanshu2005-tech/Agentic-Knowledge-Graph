// Auto-generated Code Vault for 'QuickSort' [Cpp]

#include <iostream>
#include <vector>
#include <ctime>
#include <cstdlib>

// Function to swap two elements
void swap(int& a, int& b) {
    int temp = a;
    a = b;
    b = temp;
}

// Function to partition the array and return the pivot index
int partition(std::vector<int>& arr, int low, int high) {
    // Choose the last element as the pivot
    int pivot = arr[high];
    int i = low - 1;

    // Iterate through the array and move elements smaller than the pivot to the left
    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(arr[i], arr[j]);
        }
    }

    // Move the pivot to its correct position
    swap(arr[i + 1], arr[high]);
    return i + 1;
}

// Function to implement QuickSort
void quickSort(std::vector<int>& arr, int low, int high) {
    if (low < high) {
        // Partition the array and get the pivot index
        int pivotIndex = partition(arr, low, high);

        // Recursively sort the subarrays
        quickSort(arr, low, pivotIndex - 1);
        quickSort(arr, pivotIndex + 1, high);
    }
}

// Function to print the array
void printArray(const std::vector<int>& arr) {
    for (int num : arr) {
        std::cout << num << " ";
    }
    std::cout << std::endl;
}

int main() {
    // Initialize a random seed
    srand(static_cast<unsigned int>(time(nullptr)));

    // Create a vector with 10 random integers
    std::vector<int> arr(10);
    for (int i = 0; i < 10; i++) {
        arr[i] = rand() % 100;
    }

    // Print the original array
    std::cout << "Original array: ";
    printArray(arr);

    // Sort the array using QuickSort
    quickSort(arr, 0, arr.size() - 1);

    // Print the sorted array
    std::cout << "Sorted array: ";
    printArray(arr);

    return 0;
}
