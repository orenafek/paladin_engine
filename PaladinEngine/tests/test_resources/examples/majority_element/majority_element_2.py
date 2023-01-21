def majority_element_2(nums):
    candidate, count = nums[0], 0
    for num in nums:
        if num == candidate:
            count += 1
        elif count == 0:
            candidate, count = num, 1
        else:
            count -= 1
    return candidate


def main():
    numbers = [3, 2, 3, 2, 2, 2, 4]
    result = majority_element_2(numbers)
    print(result)


if __name__ == "__main__":
    main()
