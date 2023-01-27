import hashlib


class Hasher:
    @staticmethod
    def hash(input_sequence: str) -> str:
        hasher = hashlib.new('sha256')
        hasher.update(input_sequence.encode())
        return hasher.hexdigest()

    @staticmethod
    def verify(str_to_check: str, hashed_str: str) -> bool:
        return Hasher.hash(str_to_check) == hashed_str
