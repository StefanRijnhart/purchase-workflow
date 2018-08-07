# coding: utf-8
# Copyright 2018 Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Merge",
    "summary": "Merge unconfirmed purchase orders from the same supplier",
    "version": "10.0.1.0.0",
    "development_status": "Beta",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Opener B.V., Odoo Community Association (OCA)",
    "maintainers": [],
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_order_merge.xml",
    ],
}
