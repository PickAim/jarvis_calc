from abc import abstractmethod


class CalculatorBase:
    @staticmethod
    @abstractmethod
    def calculate(*args):
        pass
