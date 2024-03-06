"""
Models for Product

All of the models are stored in this module
@see https://github.com/CSCI-GA-2820-SP24-003/products/issues/22
@see https://www.youtube.com/watch?v=k8-Aw-_xZR8
@see https://github.com/nyu-devops/lab-flask-tdd/blob/master/service/models.py

Models
------
Product - A Product sold in a Store

Attributes:
-----------
id (integer) - the unique identifier for a product
name (string, required) - the name of the product
img_url (string, required) - the image url of the product
description (string) - the description of the product
price (float, required) - the price of the product, in dollars (e.g. 9.99)
rating (integer, required, default=0.0) - the rating of the product (e.g. 4.5)
category (string) - the category of the product (e.g. "clothes")
status (enum, required, default="active") - the status of the product (i.e. "active" or "disabled")
"""

import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Status(Enum):
    """Enumeration of the status of a Product"""

    ACTIVE = 0
    DISABLED = 1


class Product(db.Model):
    """
    Class that represents a Product
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    img_url = db.Column(db.String(63), nullable=False)
    description = db.Column(db.String(1024))
    price = db.Column(db.Float(), nullable=False)
    rating = db.Column(db.Float(), nullable=False, server_default="0.0")
    category = db.Column(db.String(63))
    status = db.Column(
        db.Enum(Status), nullable=False, server_default=(Status.ACTIVE.name)
    )

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Product to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Product to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Product from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Product into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "img_url": self.img_url,
            "description": self.description,
            "price": self.price,
            "rating": self.rating,
            "category": self.category,
            "status": self.status.name,
        }

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            if isinstance(data["img_url"], str):
                self.img_url = data["img_url"]
            else:
                raise DataValidationError(
                    "Invalid type for str [img_url]: " + str(type(data["img_url"]))
                )
            self.description = data.get("description")
            if isinstance(data["price"], float) or isinstance(data["price"], int):
                self.price = float(data["price"])
            else:
                raise DataValidationError(
                    "Invalid type for float [price]: " + str(type(data["price"]))
                )

            self.rating = data.get("rating", 0.0)
            self.category = data.get("category")
            self.status = Status[data.get("status", "active").upper()]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Product: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Products in the database"""
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Product by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Products with the given name

        Args:
            name (string): the name of the Products you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
