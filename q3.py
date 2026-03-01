
def max_profit_k_transactions(prices, k):
    n = len(prices)
    if n == 0 or k == 0:
        return 0

    # If k is large, it's equivalent to unlimited transactions
    if k >= n // 2:
        profit = 0
        for i in range(1, n):
            if prices[i] > prices[i - 1]:
                profit += prices[i] - prices[i - 1]
        return profit

    # dp_prev[i] = max profit up to day i with at most (t-1) transactions
    # dp_curr[i] = max profit up to day i with at most t transactions
    dp_prev = [0] * n

    for t in range(1, k + 1):
        dp_curr = [0] * n
        best_buy = -prices[0]  # max(dp_prev[i] - prices[i]) seen so far

        for i in range(1, n):
            # Option 1: do nothing on day i
            # Option 2: sell on day i (prices[i] + best_buy)
            dp_curr[i] = max(dp_curr[i - 1], prices[i] + best_buy)

            # Update best_buy for future sells
            best_buy = max(best_buy, dp_prev[i] - prices[i])

        dp_prev = dp_curr

    return dp_prev[-1]


# -------- TESTS --------
print(max_profit_k_transactions([2, 4, 1], 2))              # Expected: 2
print(max_profit_k_transactions([3, 2, 6, 5, 0, 3], 2))      # Expected: 7
print(max_profit_k_transactions([7, 6, 4, 3, 1], 2))         # Expected: 0
print(max_profit_k_transactions([1, 2, 3, 4, 5], 2))         # Expected: 4
print(max_profit_k_transactions([], 3))                      # Expected: 0
print(max_profit_k_transactions([5], 10))                    # Expected: 0