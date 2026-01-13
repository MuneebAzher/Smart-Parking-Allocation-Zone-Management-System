from parking_area import ParkingArea

class Zone:
    def __init__(self, zone_id):
        self.zone_id = zone_id
        self.parking_areas = []
        self.neighbors = []  # List of neighbor Zone IDs

    def add_parking_area(self, area: ParkingArea):
        self.parking_areas.append(area)

    def add_neighbor(self, neighbor_zone_id):
        if neighbor_zone_id not in self.neighbors:
            self.neighbors.append(neighbor_zone_id)

    def get_all_slots(self):
        all_slots = []
        for area in self.parking_areas:
            all_slots.extend(area.slots)
        return all_slots
