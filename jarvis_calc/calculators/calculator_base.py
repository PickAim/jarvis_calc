from abc import abstractmethod


class Calculator:
    @classmethod
    @abstractmethod
    def calculate(cls, *args):
        pass
