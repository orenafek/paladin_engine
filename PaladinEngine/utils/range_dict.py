from typing import Optional, Tuple, Any


class RangeDict:
    def __init__(self, max_time):
        self.max_time = max_time
        self.data = {}
        self.last_inserted_time = -1
        self.last_inserted_value = None
        self.first_inserted_time = -1
        self.ranges_cache = []  # Cache for storing ranges
        self.edges_cache = None  # Cache for storing edges

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if key < 0 or key > self.max_time:
                raise ValueError("Key must be within the range [0, max_time]")
            self.data[key] = value
            self.last_inserted_time = key
            self.last_inserted_value = value
            self.ranges_cache = None  # Invalidate ranges cache
            self.edges_cache = None  # Invalidate edges cache
            self.first_inserted_time = self.first_inserted_time if self.first_inserted_time == -1 else key
        elif isinstance(key, tuple) and len(key) == 2 and isinstance(key[0], int) and isinstance(key[1], int):
            start, end = key
            if start < 0 or end > self.max_time or start > end:
                raise ValueError("Invalid range")
            for t in range(start, end + 1):
                self.data[t] = value
            self.last_inserted_time = end
            self.last_inserted_value = value
            self.ranges_cache = None  # Invalidate ranges cache
            self.edges_cache = None  # Invalidate edges cache
            self.first_inserted_time = self.first_inserted_time if self.first_inserted_time == -1 else key[0]
        else:
            raise TypeError("Key must be either an integer or a tuple of two integers")

    def __getitem__(self, key):
        if isinstance(key, int):
            if key < 0 or key >= self.max_time:
                raise ValueError("Key must be within the range [0, max_time)")

            ranges = self.ranges()
            # Binary search to find the range containing the key
            left, right = 0, len(ranges) - 1
            while left <= right:
                mid = (left + right) // 2
                start, stop, val = ranges[mid]
                if start <= key < stop:
                    return val
                elif key < start:
                    right = mid - 1
                else:
                    left = mid + 1

            return None

        elif isinstance(key, tuple) and len(key) == 2 and isinstance(key[0], int) and isinstance(key[1], int):
            start, end = key
            if start < 0 or end > self.max_time or start > end:
                raise ValueError("Invalid range")

            result = {}
            # Iterate through the ranges and check for intersections
            for (range_start, range_stop), value in self.ranges():
                intersection_start = max(start, range_start)
                intersection_stop = min(end, range_stop)
                if intersection_start < intersection_stop:
                    result.update({t: value for t in range(intersection_start, intersection_stop)})

            return result

        else:
            raise TypeError("Key must be either an integer or a tuple of two integers")

    def __contains__(self, key):
        if isinstance(key, int):
            if key < 0 or key > self.max_time:
                return False
            return any(start <= key < end for start, end, _ in self.ranges())
        else:
            raise TypeError("Key must be an integer")

    @property
    def first_time(self):
        return self.first_inserted_time

    @property
    def last_time(self):
        return self.last_inserted_time

    def get_last(self):
        return self.last_inserted_value

    def ranges(self):
        if self.ranges_cache is not None:
            return self.ranges_cache

        ranges = []
        start_time = 0
        prev_value = None
        for t in sorted(self.data.keys()):
            if prev_value is not None:
                ranges.append((start_time, t, prev_value))
            start_time = t
            prev_value = self.data[t]
        ranges.append((start_time, self.max_time, prev_value))
        self.ranges_cache = ranges
        return ranges

    def __repr__(self):
        return repr(self.data)

    def edges(self):
        if self.ranges_cache is not None:
            return [(start, end) for start, end, _ in self.ranges()]
        else:
            return [(start, end) for start, end, _ in self.ranges()]

    def get_closest(self, t) -> Tuple[Optional[Any], Optional[int]]:
        if t < 0 or t >= self.max_time:
            return None, None

        closest_time = None
        closest_value = None
        for start, end, value in self.ranges():
            if start <= t and (closest_time is None or start < closest_time):
                closest_time = start
                closest_value = value

        return closest_value, closest_time


if __name__ == '__main__':
    # Example usage:
    rd = RangeDict(10)

    # Inserting value 'V' at time 5
    rd[5] = 'V'

    # Inserting value 'V2' for the range [7, 9]
    rd[(7, 9)] = 'V2'

    print(5 in rd)  # Output: True
    print(6 in rd)  # Output: True
    print(7 in rd)  # Output: True
    print(10 in rd)  # Output: False
