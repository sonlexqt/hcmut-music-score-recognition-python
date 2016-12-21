class Staff:
    def __init__(self):
        self.index = -1
        self.measures = []
        self.key_signature = None
        self.time_signature = None
        self.number_of_measures = 0

    def set_index(self, index):
        self.index = index

    def set_key_signature(self, key_signature):
        self.key_signature = key_signature

    def set_time_signature(self, time_signature):
        self.time_signature = time_signature

    def add_measure(self, measure):
        measure.set_index(self.number_of_measures)
        self.number_of_measures += 1
        self.measures.append(measure)
