
def word_break_all(s, wordDict):
    word_set = set(wordDict)
    n = len(s)
    memo = {}

    def dfs(i):
        if i in memo:
            return memo[i]
        if i == n:
            return [""]  # one valid way: empty sentence

        res = []
        for j in range(i + 1, n + 1):
            word = s[i:j]
            if word in word_set:
                tails = dfs(j)
                for tail in tails:
                    if tail == "":
                        res.append(word)
                    else:
                        res.append(word + " " + tail)

        memo[i] = res
        return res

    return dfs(0)

print(word_break_all("catsanddog", ["cat","cats","and","sand","dog"]))
# Expected:
# ["cats and dog", "cat sand dog"] (order may vary)

print(word_break_all("pineapplepenapple",
                     ["apple","pen","applepen","pine","pineapple"]))
# Expected:
# ["pine apple pen apple",
#  "pineapple pen apple",
#  "pine applepen apple"] (order may vary)

print(word_break_all("catsandog", ["cats","dog","sand","and","cat"]))
# Expected: [] (no valid segmentation)