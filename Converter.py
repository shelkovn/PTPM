class Converter:

    def do(self, x:float) -> int:

        if not isinstance(x, float):
            raise ValueError("not a float")

        if round(x, 1) != x:
            raise ValueError("not one decimal")

        #round(x % 0.1, 7) != 0 

        if (x <= -30.5):        #1
            return -2000

        if (x < 0):             #2
            return int(x) - 5

        if (x == 0):            #2 border
            raise ValueError("recieved zero")

        if (x < 100.7):         #3
            return int(x)

        return 1000             #above 3
