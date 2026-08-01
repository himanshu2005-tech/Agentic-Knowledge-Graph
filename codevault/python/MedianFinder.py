# Auto-generated Code Vault for 'MedianFinder' [Python]

class MedianFinder:
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        # Merge two sorted arrays into one
        merged = sorted(nums1 + nums2)
        
        # Calculate the length of the merged array
        length = len(merged)
        
        # If the length is even, the median is the average of the two middle numbers
        if length % 2 == 0:
            return (merged[length // 2 - 1] + merged[length // 2]) / 2.0
        # If the length is odd, the median is the middle number
        else:
            return float(merged[length // 2])

    def findMedianSortedArraysOptimized(self, nums1: list[int], nums2: list[int]) -> float:
        # Ensure that nums1 is the smaller array
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1
        
        # Calculate the total length of the two arrays
        total_length = len(nums1) + len(nums2)
        
        # Initialize the low and high pointers for binary search
        low, high = 0, len(nums1)
        
        while low <= high:
            # Calculate the partition point for nums1
            partition_nums1 = (low + high) // 2
            
            # Calculate the partition point for nums2
            partition_nums2 = (total_length + 1) // 2 - partition_nums1
            
            # Calculate the values at the partition points
            max_left_nums1 = float('-inf') if partition_nums1 == 0 else nums1[partition_nums1 - 1]
            min_right_nums1 = float('inf') if partition_nums1 == len(nums1) else nums1[partition_nums1]
            
            max_left_nums2 = float('-inf') if partition_nums2 == 0 else nums2[partition_nums2 - 1]
            min_right_nums2 = float('inf') if partition_nums2 == len(nums2) else nums2[partition_nums2]
            
            # Check if the partition is correct
            if max_left_nums1 <= min_right_nums2 and max_left_nums2 <= min_right_nums1:
                # If the total length is even, the median is the average of the two middle numbers
                if total_length % 2 == 0:
                    return (max(max_left_nums1, max_left_nums2) + min(min_right_nums1, min_right_nums2)) / 2.0
                # If the total length is odd, the median is the middle number
                else:
                    return float(max(max_left_nums1, max_left_nums2))
            # If the partition is not correct, adjust the pointers
            elif max_left_nums1 > min_right_nums2:
                high = partition_nums1 - 1
            else:
                low = partition_nums1 + 1


def main():
    median_finder = MedianFinder()
    nums1 = [1, 3]
    nums2 = [2]
    print(median_finder.findMedianSortedArrays(nums1, nums2))
    print(median_finder.findMedianSortedArraysOptimized(nums1, nums2))

if __name__ == "__main__":
    main()
