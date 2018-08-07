# coding: utf-8
# Copyright 2018 Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class PurchaseOrderMerge(models.TransientModel):
    _name = 'purchase.order.merge'

    purchase_ids = fields.Many2many('purchase.order')

    @api.model
    def default_get(self, fields_list):
        res = super(PurchaseOrderMerge, self).default_get(fields_list)
        if not fields_list or 'purchase_ids' in fields_list:
            if self.env.context.get('active_model') == 'purchase.order':
                purchase_ids = self.env.context.get('active_ids', [])
                self.validate_purchase_orders(
                    self.env['purchase.order'].browse(purchase_ids))
                res['purchase_ids'] = [(6, 0, purchase_ids)]
        return res

    @api.model
    def validate_purchase_orders(self, orders):
        """ Check if the purchase orders are allowed to be merged. Raise if
        that is not the case. """
        orders = orders.sorted('id')
        confirmed = orders.filtered(lambda o: o.state not in ('draft', 'sent'))
        if confirmed:
            raise UserError(_(
                'Cannot merge confirmed or cancelled orders: %s' %
                ', '.join(confirmed.mapped('name'))))
        if not all(o.partner_id == orders[0].partner_id for o in orders[1:]):
            raise UserError(_(
                'Cannot merge orders from different suppliers: %s' %
                ', '.join(orders.mapped('partner_id.name'))))
        if not all(o.picking_type_id == orders[0].picking_type_id
                   for o in orders[1:]):
            raise UserError(_(
                'Cannot merge orders with different picking types: %s' %
                ', '.join(orders.mapped('picking_type_id.name'))))
        if not all(o.currency_id == orders[0].currency_id
                   for o in orders[1:]):
            raise UserError(_(
                'Cannot merge orders with different currencies: %s' %
                ', '.join(orders.mapped('currency_id.name'))))

    @api.multi
    def do_merge(self):
        """ Perform a sanity check, then call an extensible mechanism on all
        fields to harvest values to write on the target purchase order. Return
        a form view with this resulting target order. """
        self.ensure_one()
        if len(self.purchase_ids) < 2:
            raise UserError(_(
                'Please select two or more purchase orders from the same '
                'supplier.'))
        self.validate_purchase_orders(self.purchase_ids)

        # Merge all orders into the first order
        orders = self.purchase_ids.sorted('id')
        target = orders[0]
        others = orders[1:]

        vals = {}
        order_model = self.env['purchase.order']
        for field_name, field in orders._fields.items():
            if hasattr(order_model, 'merge_field_%s' % field_name):
                val = getattr(
                    order_model, 'merge_field_%s' % field_name)(target, others)
                if val is not None:
                    vals[field_name] = val

        target.write(vals)

        # Cancel the other orders and create a trail of notifications
        for order in others:
            order.refresh()
            order.message_post(body=_('Merged into %s') % target.name)
            order.button_cancel()
        target.message_post(
            body=_('Purchase order(s) %s were merged into this one') %
            ', '.join(others.mapped('name')))

        action = self.env.ref(
            'purchase.purchase_order_action_generic').read()[0]
        action.update({
            'res_id': target.id,
            'view_mode': 'form',
        })
        return action
