"""
TestProduct API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Product
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
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["price"], test_product.price)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(new_product["status"], test_product.status.name)
        self.assertEqual(new_product["url"], test_product.url)
        self.assertEqual(new_product["rating"], test_product.rating)
        self.assertEqual(new_product["category"], test_product.category)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_product(self):
        """It should Get a single Product"""
        # get the id of a product
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)
        self.assertEqual(data["price"], test_product.price)
        self.assertEqual(data["description"], test_product.description)
        self.assertEqual(data["status"], test_product.status.name)

    def test_read_product_not_found(self):
        """It should not Get a Product thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])
    
    def test_delete_product(self):
        """It should Delete a Pet"""
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
