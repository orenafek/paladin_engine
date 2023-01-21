def move_zeros_2(nums):
    i = 0
    for j in range(len(nums)):
        if nums[j] != 0:
            nums[i], nums[j] = nums[j], nums[i]
            i += 1
    return nums


def main():
    numbers = [0, 3, 2, 3, 2, 0, 2, 2, 4]
    result = move_zeros_2(numbers)
    print(result)


if __name__ == "__main__":
    main()
