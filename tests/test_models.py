"""
Test cases for Product Model
"""

import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Product, db, DataValidationError
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Product   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProduct(TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_product(self):
        """It should create a product"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)
        found = Product.all()
        self.assertEqual(len(found), 1)
        data = Product.find(product.id)
        self.assertEqual(data.name, product.name)
        self.assertEqual(data.img_url, product.img_url)
        self.assertEqual(data.description, product.description)
        self.assertEqual(data.price, product.price)
        self.assertEqual(data.rating, product.rating)
        self.assertEqual(data.category, product.category)
        self.assertEqual(data.status, product.status)

    @patch("service.models.db.session.commit")
    def test_create_product_failed(self, exception_mock):
        """It should not create a product on database error"""
        exception_mock.side_effect = Exception()
        product = ProductFactory()
        self.assertRaises(DataValidationError, product.create)

    @patch("service.models.db.session.commit")
    def test_update_product_failed(self, exception_mock):
        """It should not update a product on database error"""
        exception_mock.side_effect = Exception()
        product = ProductFactory()
        self.assertRaises(DataValidationError, product.update)

    @patch("service.models.db.session.commit")
    def test_delete_product_failed(self, exception_mock):
        """It should not delete a product on database error"""
        exception_mock.side_effect = Exception()
        product = ProductFactory()
        self.assertRaises(DataValidationError, product.delete)

    # Todo: Add your test cases here
    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found = Product.find(product.id)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)
        self.assertEqual(found.img_url, product.img_url)
        self.assertEqual(found.description, product.description)
        self.assertEqual(found.price, product.price)
        self.assertEqual(found.rating, product.rating)
        self.assertEqual(found.category, product.category)
        self.assertEqual(found.status, product.status)

    def test_serialize_a_product(self):
        """It should serialize a Product"""
        product = ProductFactory()
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], product.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], product.name)
        self.assertIn("img_url", data)
        self.assertEqual(data["img_url"], product.img_url)
        self.assertIn("description", data)
        self.assertEqual(data["description"], product.description)
        self.assertIn("price", data)
        self.assertEqual(data["price"], product.price)
        self.assertIn("rating", data)
        self.assertEqual(data["rating"], product.rating)
        self.assertIn("category", data)
        self.assertEqual(data["category"], product.category)
        self.assertIn("status", data)
        self.assertEqual(data["status"], product.status.name)

    def test_deserialize_a_product(self):
        """It should de-serialize a Product"""
        data = ProductFactory().serialize()
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, data["name"])
        self.assertEqual(product.img_url, data["img_url"])
        self.assertEqual(product.description, data["description"])
        self.assertEqual(product.price, data["price"])
        self.assertEqual(product.rating, data["rating"])
        self.assertEqual(product.category, data["category"])
        self.assertEqual(product.status.name, data["status"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Product with missing data"""
        data = {"id": 1, "name": "Kola", "category": "drink", "price": 100}
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "Random Text"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_price(self):
        """It should not deserialize a bad price attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["price"] = "an random string"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_url(self):
        """It should not deserialize a bad img_url attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["img_url"] = 100  # wrong case
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)
