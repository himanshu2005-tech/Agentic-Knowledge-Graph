// Auto-generated Code Vault for 'MergeSort' [Javascript]

class MergeSort {
    /**
     * Public method to sort an array using Merge Sort algorithm.
     * @param {Array} array - The array to sort.
     * @param {Function} [compare] - Optional comparison function. Should return negative if a < b, 0 if equal, positive if a > b.
     * @returns {Array} New sorted array.
     */
    static sort(array, compare) {
        if (!Array.isArray(array)) {
            throw new TypeError('Input must be an array.');
        }
        if (array.length <= 1) {
            return array.slice(); // return a shallow copy
        }
        // Default comparison: ascending order
        const cmp = typeof compare === 'function' ? compare : (a, b) => a < b ? -1 : a > b ? 1 : 0;
        return this._mergeSort(array.slice(), cmp);
    }

    /**
     * Recursive helper that sorts and merges subarrays.
     * @private
     * @param {Array} subArray - Subarray to sort.
     * @param {Function} cmp - Comparison function.
     * @returns {Array} Sorted subarray.
     */
    static _mergeSort(subArray, cmp) {
        if (subArray.length <= 1) {
            return subArray;
        }
        const mid = Math.floor(subArray.length / 2);
        const left = this._mergeSort(subArray.slice(0, mid), cmp);
        const right = this._mergeSort(subArray.slice(mid), cmp);
        return this._merge(left, right, cmp);
    }

    /**
     * Merge two sorted arrays into a single sorted array.
     * @private
     * @param {Array} left - First sorted array.
     * @param {Array} right - Second sorted array.
     * @param {Function} cmp - Comparison function.
     * @returns {Array} Merged sorted array.
     */
    static _merge(left, right, cmp) {
        const result = [];
        let i = 0;
        let j = 0;

        while (i < left.length && j < right.length) {
            if (cmp(left[i], right[j]) <= 0) {
                result.push(left[i++]);
            } else {
                result.push(right[j++]);
            }
        }
        // Append remaining elements
        return result.concat(left.slice(i)).concat(right.slice(j));
    }
}

// Example usage:
if (require.main === module) {
    const unsorted = [38, 27, 43, 3, 9, 82, 10];
    console.log('Original:', unsorted);
    const sorted = MergeSort.sort(unsorted);
    console.log('Sorted:', sorted);
}

// Export for ES modules
export default MergeSort;
