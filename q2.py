
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def max_path_sum(root):
    best = float("-inf")

    def dfs(node):
        nonlocal best
        if not node:
            return 0

        left_gain = max(0, dfs(node.left))
        right_gain = max(0, dfs(node.right))

        best = max(best, node.val + left_gain + right_gain)

        return node.val + max(left_gain, right_gain)

    dfs(root)
    return best


# -------- TESTS --------
# Test 1: [1,2,3] -> 6
root1 = TreeNode(1, TreeNode(2), TreeNode(3))
print(max_path_sum(root1))  # 6

# Test 2: [-10,9,20,null,null,15,7] -> 42
root2 = TreeNode(-10,
                 TreeNode(9),
                 TreeNode(20, TreeNode(15), TreeNode(7)))
print(max_path_sum(root2))  # 42

# Test 3: single negative node -> -3
root3 = TreeNode(-3)
print(max_path_sum(root3))  # -3