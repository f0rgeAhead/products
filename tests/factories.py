"""
Test Factory to make fake objects for testing
"""

import factory
from factory.fuzzy import FuzzyChoice
from service.models import Product, Status


class ProductFactory(factory.Factory):
    """Creates fake products"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    img_url = factory.Faker("url")
    description = factory.Faker("text")
    price = factory.Faker("random_number", digits=2)
    rating = factory.Faker("random_number", digits=1)
    category = FuzzyChoice(
        choices=["clothes", "shoes", "electronics", "books", "movies", "music", "games"]
    )
    status = FuzzyChoice(choices=[Status.ACTIVE, Status.DISABLED])
