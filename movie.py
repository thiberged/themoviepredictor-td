class Movie:

    def __init__(self, title, original_title, release_date, duration, rating):
        self.title = title
        self.original_title = original_title
        self.release_date = release_date
        self.duration = duration
        self.rating = rating

        self.id = None
        self.actors = []
        self.productors = []
        self.is_3d = None
        self.production_budget = None
        self.marketing_budget = None


    def description_movie(self):
        print(self.title +" "+ self.original_title +" "+ self.release_date +" "+ self.duration +" "+ self.rating)

    def budget_total(self):
        if (self.production_budget == None or self.marketing_budget == None):
            return None

        return self.production_budget + self.marketing_budget