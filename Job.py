class Job:
    def __init__(self, title, company,dt):
        self.title = title
        self.company = company
        self.dt = dt

    def myprint(self):
        print(self.title, self.company)
