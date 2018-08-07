# coding: utf-8
# Copyright 2018 Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def merge_field_message_follower_ids(self, target, others):
        existing = target.message_follower_ids.mapped(
            'partner_id')
        val = []
        for follower in others.mapped('message_follower_ids'):
            if follower.partner_id not in existing:
                existing += follower.partner_id
                val.append((4, follower.id))
        return val

    @api.model
    def merge_field_message_ids(*args):
        return None

    @api.model
    def merge_field_order_line(self, target, others):
        return [(6, 0, (target + others).mapped('order_line').ids)]

    @api.model
    def merge_field_origin(self, target, others):
        return ','.join(
            set((target + others).filtered('origin').mapped('origin')))

    @api.model
    def merge_field_state(self, target, others):
        return 'draft' if target.state == 'sent' else None
