dataset = [
    # O(1) - Constant
    ("def get_first(arr):\n    return arr[0]", "O(1)"),
    ("def add(a, b):\n    return a + b", "O(1)"),
    ("def is_even(n):\n    return n % 2 == 0", "O(1)"),
    ("def get_last(arr):\n    return arr[-1]", "O(1)"),
    ("def constant(n):\n    x = 10\n    y = 20\n    return x + y", "O(1)"),

    # O(log n) - Logarithmic
    ("def binary_search(arr, t):\n    l,r=0,len(arr)-1\n    while l<=r:\n        m=(l+r)//2\n        if arr[m]==t: return m\n        elif arr[m]<t: l=m+1\n        else: r=m-1\n    return -1", "O(log n)"),
    ("def find_power(base, exp):\n    result = 1\n    while exp > 0:\n        exp //= 2\n        result *= base\n    return result", "O(log n)"),

    # O(n) - Linear
    ("def linear_search(arr, t):\n    for x in arr:\n        if x == t: return True\n    return False", "O(n)"),
    ("def find_max(arr):\n    m = arr[0]\n    for x in arr:\n        if x > m: m = x\n    return m", "O(n)"),
    ("def calc_sum(arr):\n    s = 0\n    for x in arr:\n        s += x\n    return s", "O(n)"),
    ("def reverse_list(arr):\n    result = []\n    for i in range(len(arr)-1, -1, -1):\n        result.append(arr[i])\n    return result", "O(n)"),
    ("def count_evens(arr):\n    count = 0\n    for x in arr:\n        if x % 2 == 0: count += 1\n    return count", "O(n)"),

    # O(n log n)
    ("def merge_sort(arr):\n    if len(arr)<=1: return arr\n    mid=len(arr)//2\n    l=merge_sort(arr[:mid])\n    r=merge_sort(arr[mid:])\n    return merge(l,r)", "O(n log n)"),
    ("def heap_sort(arr):\n    import heapq\n    heapq.heapify(arr)\n    return [heapq.heappop(arr) for _ in range(len(arr))]", "O(n log n)"),

    # O(n^2) - Quadratic
    ("def bubble_sort(arr):\n    n=len(arr)\n    for i in range(n):\n        for j in range(n-i-1):\n            if arr[j]>arr[j+1]:\n                arr[j],arr[j+1]=arr[j+1],arr[j]\n    return arr", "O(n^2)"),
    ("def selection_sort(arr):\n    for i in range(len(arr)):\n        m=i\n        for j in range(i+1,len(arr)):\n            if arr[j]<arr[m]: m=j\n        arr[i],arr[m]=arr[m],arr[i]\n    return arr", "O(n^2)"),
    ("def print_pairs(arr):\n    for i in arr:\n        for j in arr:\n            print(i,j)", "O(n^2)"),
    ("def insertion_sort(arr):\n    for i in range(1,len(arr)):\n        k=arr[i]; j=i-1\n        while j>=0 and arr[j]>k:\n            arr[j+1]=arr[j]; j-=1\n        arr[j+1]=k\n    return arr", "O(n^2)"),

    # O(n^3) - Cubic
    ("def matrix_multiply(A,B,C):\n    n=len(A)\n    for i in range(n):\n        for j in range(n):\n            for k in range(n):\n                C[i][j]+=A[i][k]*B[k][j]", "O(n^3)"),
    ("def triple_loop(arr):\n    count=0\n    for i in arr:\n        for j in arr:\n            for k in arr:\n                count+=1\n    return count", "O(n^3)"),

    # O(2^n) - Exponential
    ("def fibonacci(n):\n    if n<=1: return n\n    return fibonacci(n-1)+fibonacci(n-2)", "O(2^n)"),
    ("def subsets(arr):\n    if not arr: return [[]]\n    rest=subsets(arr[1:])\n    return rest+[[arr[0]]+s for s in rest]", "O(2^n)"),
]

if __name__ == "__main__":
    print(f"Total samples: {len(dataset)}")
    from collections import Counter
    labels = [label for _, label in dataset]
    for k, v in Counter(labels).items():
        print(f"  {k}: {v} samples")