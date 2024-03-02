######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Pet Store Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Pets from the inventory of pets in the PetShop
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import YourResourceModel
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...

############################################################
# Create product
############################################################
PRODUCTS: dict = {}

@app.route("/products", methods=["POST"])
def create_products():
    """Create a product"""
    app.logger.info("Request to Create product...")

    data = request.get_json()
    sku = data.get('sku')

    if sku in PRODUCTS:
        abort(status.HTTP_409_CONFLICT, f"Product with SKU'{sku}' already exists.")

    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    img_url = data.get('img_url')


    product = 0
    PRODUCTS[sku] = {
        'id': len(PRODUCTS) + 1,
        'name': name,
        'description': description,
        'price': price,
        'img_url': img_url,
    }

    app.logger.info("Product %s created.", sku)
    location_url = url_for("read_products", sku=sku, _external=True)
    return (
        jsonify(PRODUCTS[sku]),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )