def move_zeros_1(nums):
    k = 0
    for i in range(len(nums)):
        if nums[i] != 0:
            nums[k] = nums[i]
            k += 1

    while k < len(nums):
        nums[k] = 0
        k += 1

    return nums


def main():
    numbers = [0, 3, 2, 3, 2, 0, 2, 2, 4]
    result = move_zeros_1(numbers)
    print(result)


if __name__ == "__main__":
    main()
