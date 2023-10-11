class Index:
    _instance = None
    mapping = {'aeroplane': 1,
               'bicycle': 2,
               'bird': 3,
               'boat': 4,
               'bottle': 5,
               'bus': 6,
               'car': 7,
               'cat': 8,
               'chair': 9,
               'cow': 10,
               'diningtable': 11,
               'dog': 12,
               'horse': 13,
               'motorbike': 14,
               'person': 15,
               'pottedplant': 16,
               'sheep': 17,
               'sofa': 18,
               'train': 19,
               'tvmonitor': 20,
               'test': 8}

    @staticmethod
    def get_index(name):
        return Index.mapping[name]
