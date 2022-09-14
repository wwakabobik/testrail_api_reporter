class CaseStat:
    """
    Placeholder class for automation statistics
    """
    def __init__(self, name):
        self.name = name
        self.total = 0
        self.automated = 0
        self.not_automated = 0
        self.na = 0

    # getters
    def get_name(self):
        return self.name

    def get_total(self):
        return self.total

    def get_automated(self):
        return self.automated

    def get_not_automated(self):
        return self.not_automated

    def get_na(self):
        return self.na

    # setters
    def set_name(self, name):
        self.name = name

    def set_total(self, total):
        self.total = total

    def set_automated(self, automated):
        self.automated = automated

    def set_not_automated(self, not_automated):
        self.not_automated = not_automated

    def set_na(self, na):
        self.na = na
