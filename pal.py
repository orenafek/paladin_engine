def rs(s): return s[::-1]


def ip(s): print("Enter a string: ", end="");return input()


def isp(s): return s == rs(s)


def fsp(s):
    return [s[i:i + 1] for i in range(len(s)) if not isp(s[i:i + 1])]


def fsp2(s):
    return [s[i:j] for i in range(len(s))
            for j in range(i + 1, len(s)) if isp(s[i:j])]


def fsp3(s): return [s[i:k] for i in range(len(s)) for j in range(i + 1, len(s)) if isp(s[i:j]) for k in
                     range(j + 1, len(s)) if isp(s[j:k]) if isp(s[i:k]) and len(s[i:k]) > 1 and s[i:k] not in fsp(s)]


# Example: String with letters a, b, c, d, e, and special characters #$!
input_string = "abcde#$!"
print("Input string:", input_string)

first_degree_palindromes = fsp(input_string)
second_degree_palindromes = fsp2(input_string)
filtered_palindromes = fsp3(input_string)
print("Second-degree palindromes:", filtered_palindromes)
