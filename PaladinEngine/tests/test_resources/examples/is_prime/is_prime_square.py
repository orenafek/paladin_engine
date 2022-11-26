import math


def is_prime_square_solution(number):
    if number == 1:
        return False
    stopping_point = int(math.sqrt(number)) + 1
    for i in range(2, stopping_point):
        if number % i == 0:
            return False
    return True


def main():
    number = 173
    result = is_prime_square_solution(number)
    print(result)


if __name__ == "__main__":
    main()
