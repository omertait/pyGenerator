
import sys

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

def kth_smallest_element(root, k):
    def inorder_traversal(node):
        if not node:
            return []
        return inorder_traversal(node.left) + [node.value] + inorder_traversal(node.right)

    if not root:
        return None
        
    inorder = inorder_traversal(root)
    if k <= 0 or k > len(inorder):
        raise ValueError("Invalid value of k")

    return inorder[k-1]

def unit_tests():
    # Test Case 1
    root1 = Node(4)
    root1.left = Node(2)
    root1.right = Node(6)
    root1.left.left = Node(1)
    root1.left.right = Node(3)
    root1.right.left = Node(5)
    root1.right.right = Node(7)
    assert kth_smallest_element(root1, 1) == 1

    # Test Case 2
    root2 = Node(8)
    root2.left = Node(4)
    root2.right = Node(12)
    root2.left.left = Node(2)
    root2.left.right = Node(6)
    root2.right.left = Node(10)
    root2.right.right = Node(14)
    assert kth_smallest_element(root2, 3) == 6

    # Test Case 3
    root3 = Node(5)
    root3.left = Node(3)
    root3.right = Node(7)
    assert kth_smallest_element(root3, 2) == 5

    # Test Case 4
    root4 = None
    assert kth_smallest_element(root4, 1) is None

    # Test Case 5
    root5 = Node(100)
    assert kth_smallest_element(root5, 1) == 100

    print("All unit tests pass")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        num = int(input("Enter a number: "))
        # Perform the desired operation using num
        # In this case, let's assume the desired operation is finding whether the number is prime or not
    elif sys.argv[1] == 'test':
        unit_tests()
        print("All tests pass")
    else:
        print("Invalid command line argument")
