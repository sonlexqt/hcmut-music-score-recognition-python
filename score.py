class Score:
    def __init__(self):
        self.staffs = []
        self.number_of_staffs = 0

    def add_staff(self, staff):
        staff.set_index(self.number_of_staffs)
        self.number_of_staffs += 1
        return self.staffs.append(staff)
