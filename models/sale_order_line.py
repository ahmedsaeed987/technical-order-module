from odoo import models, fields,api,_
from odoo.exceptions import ValidationError

class SaleOrderline(models.Model):

    _inherit = 'sale.order.line'

    technical_order_line_id = fields.Many2one('technical.order.lines')

    @api.constrains('product_uom_qty')
    def quantity_constrains(self):
     for rec in self:
       if rec.product_uom_qty > rec.technical_order_line_id.quantity:
         raise ValidationError("the total SOs lines quantities for the confirmedSOs shouldnt exceed the requested ones in the TO.")