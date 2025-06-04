# track_location.py

from associative_stock_location.location_algorithm import LocationAlgorithm
from associative_stock_location.retrieval import Retrieval

class TrackLocation:
    def __init__(self):
        self.locationAlgorithm = LocationAlgorithm()
        self.retrieval = Retrieval()

    def track(self, car_id):
        """Track the location of a specific car within the wrecking yard."""
        
        location = self.locationAlgorithm.get_car_location(car_id)
        
        if location:
            return f"The car with ID {car_id} is located at {location}."
        else:
            return f"The car with ID {car_id} could not be found."

    def retrieve(self, location):
        """Retrieve a car at a specific location within the wrecking yard."""
        
        car_id = self.retrieval.find_car_at_location(location)
        
        if car_id:
            return f"The car at location {location} has ID {car_id}."
        else:
            return f"No car found at location {location}."

    def update_location(self, car_id, new_location):
        """Update the location of a specific car within the wrecking yard."""
        
        success = self.locationAlgorithm.update_car_location(car_id, new_location)
        
        if success:
            return f"The location of car with ID {car_id} has been updated to {new_location}."
        else:
            return f"Failed to update the location of car with ID {car_id}."

if __name__ == "__main__":
    # Example usage:
    trackLocation = TrackLocation()

    car_location = trackLocation.track("ABC123")
    print(car_location)

    retrieved_car = trackLocation.retrieve("A4")
    print(retrieved_car)

    update_success = trackLocation.update_location("DEF456", "B8")
    print(update_success)