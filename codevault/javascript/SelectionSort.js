// Auto-generated Code Vault for 'SelectionSort' [Javascript]

class SelectionSort {
  /**
   * Sorts an array using the selection sort algorithm.
   * @param {Array} arr - The array to be sorted.
   * @returns {Array} The sorted array.
   */
  static sort(arr) {
    // Loop through the array
    for (let i = 0; i < arr.length; i++) {
      // Initialize the minimum index
      let minIndex = i;
      
      // Find the minimum element in the unsorted part of the array
      for (let j = i + 1; j < arr.length; j++) {
        if (arr[j] < arr[minIndex]) {
          minIndex = j;
        }
      }
      
      // Swap the found minimum element with the first element of the unsorted part
      [arr[i], arr[minIndex]] = [arr[minIndex], arr[i]];
    }
    
    return arr;
  }
}

// Example usage:
let arr = [64, 25, 12, 22, 11];
console.log("Original array:", arr);
console.log("Sorted array:", SelectionSort.sort(arr));
