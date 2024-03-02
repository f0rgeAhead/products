"""
TestYourResourceModel API Service Test Suite
"""
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, YourResourceModel

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """ REST API Server Tests """

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
        db.session.query(YourResourceModel).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # Todo: Add your test cases here...
    def test_create_product_success(self):
        response = self.client.post('/products', data=json.dumps(self.product_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Test Product', response.data.decode())

    def test_create_product_already_exists(self):
        self.client.post('/products', data=json.dumps(self.product_data), content_type='application/json')
        response = self.client.post('/products', data=json.dumps(self.product_data), content_type='application/json')
        self.assertEqual(response.status_code, 409)
        self.assertIn('already exists', response.data.decode())

    def test_create_product_invalid_data(self):
        invalid_data = self.product_data.copy()
        del invalid_data['price']
        response = self.client.post('/products', data=json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid data', response.data.decode())