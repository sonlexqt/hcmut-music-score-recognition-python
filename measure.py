class Measure:
    def __init__(self):
        self.index = -1
        self.symbols = []
        self.number_of_symbols = 0

    def set_index(self, index):
        self.index = index

    def add_symbols(self, sbl):
        # TODO XIN set index for each symbol
        self.number_of_symbols += 1
        self.symbols.append(sbl)
