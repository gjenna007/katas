class PartitionCalculator:
    def __init__(self):
        # Memoization dictionary to store computed values
        self.memo = {0: 1}  # Base case: p(0) = 1

    def pentagonal_numbers(self, n):
        """Generate generalized pentagonal numbers up to n."""
        k = 1
        while True:
            g1 = k * (3 * k - 1) // 2
            g2 = k * (3 * k + 1) // 2

            if g1 > n:
                break

            yield g1
            if g2 <= n:
                yield g2

            k += 1

    def partitions(self, n):
        """Compute p(n) using recursion + memoization."""
        if n in self.memo:
            return self.memo[n]

        total = 0
        k = 1

        while True:
            g1 = k * (3 * k - 1) // 2
            g2 = k * (3 * k + 1) // 2

            if g1 > n:
                break

            sign = (-1) ** (k - 1)

            total += sign * self.partitions(n - g1)

            if g2 <= n:
                total += sign * self.partitions(n - g2)

            k += 1

        self.memo[n] = total
        return total

def exp_sum(n):
    pc = PartitionCalculator()
    return pc.partitions(n)