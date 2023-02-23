def majority_element_1(nums):
    m = {}
    for n in nums:
        m[n] = m.get(n, 0) + 1
        if m[n] > len(nums) // 2:
            return n


def main():
    numbers = [3, 2, 3, 2, 2, 2, 4]
    result = majority_element_1(numbers)
    print(result)
    s = {(x, x+1) for x in range(100)}
    abc = 'abcdefghijklmnopzrstuvwxyz'
    dd = {x:{x:c} for x,c in zip(range(len(abc)), abc)}
    print(s)
    print(dd)

if __name__ == '__main__':
    main()