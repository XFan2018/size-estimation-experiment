class Index:
    _instance = None
    mapping = {"cat": 8,
               "dog": 12,
               "person": 16,
               "test": 8}

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Index, cls).__new__()
        else:
            return cls._instance

    @staticmethod
    def get_index(name):
        return Index.mapping[name]
