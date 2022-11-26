def is_prime_naive_solution(number):
    if number == 1:
        return False
    for i in range(2, number):
        if number % i == 0:
            return False
    return True


def main():
    number = 173
    result = is_prime_naive_solution(number)
    print(result)


if __name__ == "__main__":
    main()
