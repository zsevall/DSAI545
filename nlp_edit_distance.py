def min_edit_distance(source: str, target: str, show_operations: bool = False, show_matrix: bool = False):
    """
    Calculate the minimum edit distance between two strings.
    
    Args:
        source (str): Source string
        target (str): Target string
        show_operations (bool): Whether to show the operations needed for transformation
        show_matrix (bool): Whether to print the DP matrix and backtracking path
        
    Returns:
        int: Minimum edit distance
        list: List of operations (if show_operations is True)
        list: Backtracking path (if show_matrix is True)
    """
    # Create a matrix of size (m+1)x(n+1) for the dynamic programming approach
    m, n = len(source), len(target)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize the first row and column
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill the matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if source[i-1] == target[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(
                    dp[i-1][j] + 1,      # deletion
                    dp[i][j-1] + 1,      # insertion
                    dp[i-1][j-1] + 2     # substitution (costs 2)
                )
    
    if not show_operations and not show_matrix:
        return dp[m][n]
    
    # Backtrack to find operations
    operations = []
    backtrack_path = []
    i, j = m, n
    
    while i > 0 or j > 0:
        backtrack_path.append((i, j))
        if i > 0 and j > 0 and source[i-1] == target[j-1]:
            operations.append(("keep", source[i-1]))
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 2:
            operations.append(("substitute", source[i-1], target[j-1]))
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
            operations.append(("delete", source[i-1]))
            i -= 1
        elif j > 0 and dp[i][j] == dp[i][j-1] + 1:
            operations.append(("insert", target[j-1]))
            j -= 1
    
    backtrack_path.append((i, j))  # Add the final position (0,0)
    backtrack_path.reverse()
    operations.reverse()
    
    if show_matrix:
        if show_operations:
            return dp[m][n], operations, backtrack_path
        return dp[m][n], backtrack_path
    
    if show_operations:
        return dp[m][n], operations
    
    return dp[m][n]

def print_matrix_with_path(dp, source, target, path):
    """
    Print the DP matrix with the backtracking path.
    
    Args:
        dp (list): The dynamic programming matrix
        source (str): Source string
        target (str): Target string
        path (list): List of (i,j) coordinates representing the backtracking path
    """
    m, n = len(source), len(target)
    
    # Convert path to a set for O(1) lookup
    path_set = set(path)
    
    # Create the header row with target characters
    header = "    "
    for j in range(n + 1):
        if j == 0:
            header += "ε "
        else:
            header += target[j-1] + " "
    print(header)
    
    # Print each row of the matrix
    for i in range(m + 1):
        # Print row header (source character)
        if i == 0:
            row = "ε | "
        else:
            row = source[i-1] + " | "
        
        # Print the matrix values with path arrows
        for j in range(n + 1):
            # Current position
            curr_pos = (i, j)
            
            # Find the next position in the path
            next_pos = None
            if curr_pos in path_set:
                path_idx = path.index(curr_pos)
                if path_idx < len(path) - 1:
                    next_pos = path[path_idx + 1]
            
            # Determine the arrow direction
            arrow = str(dp[i][j])
            if next_pos:
                di, dj = next_pos[0] - i, next_pos[1] - j
                if di == 1 and dj == 0:
                    arrow += "↓"  # Down (deletion)
                elif di == 0 and dj == 1:
                    arrow += "→"  # Right (insertion)
                elif di == 1 and dj == 1:
                    arrow += "↘"  # Diagonal (match or substitution)
            
            row += arrow.ljust(3) + " "
        
        print(row)

def display_transformation(source: str, target: str, show_matrix: bool = False):
    """
    Display the transformation process from source to target string.
    
    Args:
        source (str): Source string
        target (str): Target string
        show_matrix (bool): Whether to print the DP matrix and backtracking path
    """
    if show_matrix:
        distance, operations, path = min_edit_distance(source, target, show_operations=True, show_matrix=True)
    else:
        distance, operations = min_edit_distance(source, target, show_operations=True)
    
    print(f"Transforming '{source}' to '{target}'")
    print(f"Minimum Edit Distance: {distance}")
    
    if show_matrix:
        print("\nEdit Distance Matrix with Backtracking Path:")
        # Get the DP matrix
        m, n = len(source), len(target)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Initialize the first row and column
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # Fill the matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if source[i-1] == target[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(
                        dp[i-1][j] + 1,      # deletion
                        dp[i][j-1] + 1,      # insertion
                        dp[i-1][j-1] + 2     # substitution (costs 2)
                    )
        
        print_matrix_with_path(dp, source, target, path)
    
    print("\nOperations:")
    
    current = list(source)
    for idx, op in enumerate(operations, 1):
        if op[0] == "keep":
            print(f"{idx}. Keep '{op[1]}'")
        elif op[0] == "substitute":
            pos = current.index(op[1])
            current[pos] = op[2]
            print(f"{idx}. Substitute '{op[1]}' with '{op[2]}' -> {''.join(current)}")
        elif op[0] == "delete":
            pos = current.index(op[1])
            current.pop(pos)
            print(f"{idx}. Delete '{op[1]}' -> {''.join(current)}")
        elif op[0] == "insert":
            if len(current) == 0:
                current.append(op[1])
                pos = 0
            else:
                pos = len(current)
                current.insert(pos, op[1])
            print(f"{idx}. Insert '{op[1]}' -> {''.join(current)}")

# Example usage
if __name__ == "__main__":
    # Simple examples
    print("Example 1:")
    display_transformation("kitten", "sitting", show_matrix=True)
    
    print("\nExample 2:")
    display_transformation("sunday", "saturday", show_matrix=True) 