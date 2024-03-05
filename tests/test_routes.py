"""
TestProduct API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Product, Status
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def _create_products(self, count):
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test product",
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def assert_product(self, product):
        """Assert that a product has all the correct attributes"""
        self.assertIn("id", product)
        self.assertIsInstance(product["id"], int)
        self.assertIn("name", product)
        self.assertIsInstance(product["name"], str)
        self.assertIn("url", product)
        self.assertIsInstance(product["url"], str)
        self.assertIn("description", product)
        self.assertIsInstance(product["description"], str)
        self.assertIn("price", product)
        self.assertIsInstance(product["price"], float)
        self.assertIn("rating", product)
        self.assertIsInstance(product["rating"], float)
        self.assertIn("category", product)
        self.assertIsInstance(product["category"], str)
        self.assertIn("status", product)
        self.assertIsInstance(product["status"], str)
        self.assertIn(product["status"], [s.name for s in Status])

    def assert_two_products_are_the_same(self, product1, product2):
        """Assert that two products are the same"""
        self.assertEqual(product1["name"], product2.name)
        self.assertEqual(product1["price"], product2.price)
        self.assertEqual(product1["description"], product2.description)
        self.assertEqual(product1["status"], product2.status.name)
        self.assertEqual(product1["url"], product2.url)
        self.assertEqual(product1["rating"], product2.rating)
        self.assertEqual(product1["category"], product2.category)

    def test_create_product(self):
        """It should Create a new Product"""

        test_product = ProductFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = response.get_json()
        self.assert_two_products_are_the_same(new_product, test_product)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_products(self):
        """It should Get a list of Products"""
        self._create_products(3)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)
        for product in data:
            self.assert_product(product)

    def test_list_products_empty(self):
        """It should Get an empty list of Products"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_read_product(self):
        """It should Get a single Product"""
        # get the id of a product
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assert_product(data)
        self.assert_two_products_are_the_same(data, test_product)

    def test_read_product_not_found(self):
        """It should not Get a Product thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_delete_product(self):
        """It should Delete a Product"""
        test_product = self._create_products(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexist_product(self):
        """It should return a HTTP 404 message"""
        response = self.client.delete(f"{BASE_URL}/10000000")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("does not exist", data["message"])

    # Todo: Add your test cases here...
    # def test_create_product_success(self):
    #     response = self.client.post(
    #         "/products",
    #         data=json.dumps(self.product_data),
    #         content_type="application/json",
    #     )
    #     self.assertEqual(response.status_code, 201)
    #     self.assertIn("Test Product", response.data.decode())

    # def test_create_product_already_exists(self):
    #     self.client.post(
    #         "/products",
    #         data=json.dumps(self.product_data),
    #         content_type="application/json",
    #     )
    #     response = self.client.post(
    #         "/products",
    #         data=json.dumps(self.product_data),
    #         content_type="application/json",
    #     )
    #     self.assertEqual(response.status_code, 409)
    #     self.assertIn("already exists", response.data.decode())

    # def test_create_product_invalid_data(self):
    #     invalid_data = self.product_data.copy()
    #     del invalid_data["price"]
    #     response = self.client.post(
    #         "/products", data=json.dumps(invalid_data), content_type="application/json"
    #     )
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn("Invalid data", response.data.decode())
