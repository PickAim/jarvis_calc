from abc import abstractmethod


class Calculator:
    @staticmethod
    @abstractmethod
    def calculate(*args):
        pass
