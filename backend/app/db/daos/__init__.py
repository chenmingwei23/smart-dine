from .restaurant import RestaurantDAO
from .review import ReviewDAO

# Initialize DAOs
restaurant_dao = RestaurantDAO()
review_dao = ReviewDAO()

__all__ = [
    "restaurant_dao",
    "review_dao",
    "RestaurantDAO",
    "ReviewDAO"
] 