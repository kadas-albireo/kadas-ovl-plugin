class CoordLL84(object):
    def __init__(self, lat, lng, hgt):
        self.lat = lat
        self.lng = lng
        self.hgt = hgt

    def __str__(self):
        return 'lat: ' + str(self.lat) + ' lng: ' + str(self.lng) + ' hgt: ' + str(self.hgt)
