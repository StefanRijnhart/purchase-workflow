# coding: utf-8
# Copyright 2018 Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase


class TestPurchaseOrderMerge(SavepointCase):
    def test_01_purchase_order_merge(self):
        po1 = self.env.ref('purchase.purchase_order_1').copy()
        po2 = self.env.ref('purchase.purchase_order_6').copy()
        amount = po1.amount_total + po2.amount_total
        po1_lines = po1.order_line
        po2_lines = po2.order_line

        wizard = self.env['purchase.order.merge'].with_context(
            active_model='purchase.order', active_ids=[po1.id, po2.id]
        ).create({})
        wizard.do_merge()
        self.assertFalse(po2.order_line)
        self.assertEqual(po1.order_line, po1_lines + po2_lines)
        self.assertEqual(po1.amount_total, amount)
        self.assertEqual(po2.state, 'cancel')
