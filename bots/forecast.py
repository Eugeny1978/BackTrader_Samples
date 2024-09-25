from random import randint

class Forecast(object):

    def __init__(self, datas):
        self.datas = datas

    def get_predict(self, datas):
        return randint(0, 1)


if __name__ == '__main__':

    f = Forecast([4, 5 ,6])
    for i in range(20):
        print(f.get_predict([4, 6, 8]))
