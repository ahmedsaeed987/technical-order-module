from odoo import models, fields,api

class TechnicalOrderLine(models.Model):
    _name = 'technical.order.lines'
    _description = 'Technical Order Line'

    order_id = fields.Many2one('technical.order', string='order_id')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    Description = fields.Char(string='Description', related='product_id.name', store=True)
    quantity = fields.Float(string='Quantity', default=1)
    price = fields.Float(string='Price', related='product_id.standard_price', readonly=True)
    total = fields.Float(string='Total', compute='_compute_total', store=True)
    sup_quantity=fields.Float(compute='_compute_sup_quantity', store=True)
    sale_order_ids=fields.One2many('sale.order.line',"technical_order_line_id")

    @api.depends('quantity', 'sale_order_ids.product_uom_qty')
    def _compute_sup_quantity(self):
        for rec in self:
            total_quan=sum(rec.product_uom_qty for line in rec.sale_order_ids if line.state =='sale')
            rec.sup_quantity = rec.quantity - total_quan


    @api.depends('quantity', 'price')
    def _compute_total(self):
        for line in self:
            line.total = line.quantity * line.price
