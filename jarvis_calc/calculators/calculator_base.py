from abc import abstractmethod


class Calculator:
    @abstractmethod
    def calculate(self, *args):
        pass
