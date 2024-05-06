def knapsack(weights, vals, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(vals[i - 1] + dp[i - 1][w - weights[i - 1]], dp[i - 1][w])
            else:
                dp[i][w] = dp[i - 1][w]

    selected_items = []
    w1, c = capacity, n
    while c > 0 and w1 > 0:
        if dp[c][w1] != dp[c - 1][w1]:
            selected_items.append(c)
            w1 -= weights[c - 1]
        c -= 1

    return dp[n][capacity], selected_items


def main():
    # Example usage:
    weights = [2, 3, 4, 5]
    vals = [3, 4, 5, 6]
    capacity = 5
    max_value, selected_items = knapsack(weights, vals, capacity)
    print("Maximum value:", max_value)
    print("Selected items:", selected_items)
    if not set(selected_items) == {0, 1}:
        raise RuntimeError('Wrong Knapsack result')


if __name__ == '__main__':
    main()
