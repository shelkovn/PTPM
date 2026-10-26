class Converter:

    def do(x:float) -> int:

        if not isinstance(x, float):
            raise ValueError("not a float")
            
        parts = str(x).split('.')

        if (not (len(parts) == 2 and len(parts[1]) == 1)):
            raise ValueError("not one decimal")

        if (x <= -30.5):
            return -2000

        if (x < 0):
            return int(x) - 5

        if (x == 0):
            raise ValueError("recieved zero")

        if (x < 100.7):
            return int(x)

        return 1000
