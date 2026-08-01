# Auto-generated Code Vault for 'BubbleSort' [Python]

def bubble_sort(lst):
    """
    Sorts a list in ascending order using the Bubble Sort algorithm.

    Args:
        lst (list): The list to be sorted.

    Returns:
        list: The sorted list.
    """
    n = len(lst)

    for i in range(n):
        # Create a flag that will allow the function to terminate early if there's nothing left to sort
        swapped = False

        # Start looking at each item of the list one by one, comparing it with its adjacent value
        for j in range(n - i - 1):
            # If we find an element that is greater than its adjacent element, then swap them
            if lst[j] > lst[j + 1]:
                # Swap values
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
                # Set the flag to True so we'll loop again after this iteration
                swapped = True

        # If no two elements were swapped in the inner loop, the list is sorted
        if not swapped:
            break

    return lst


def main():
    # Test the bubble_sort function
    unsorted_list = [8, 3, 1, 9, 2, 7, 4, 6, 5]
    print("Unsorted List:", unsorted_list)
    sorted_list = bubble_sort(unsorted_list)
    print("Sorted List:", sorted_list)


if __name__ == "__main__":
    main()
