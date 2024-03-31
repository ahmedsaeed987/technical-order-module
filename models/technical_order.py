from odoo import models, fields,api
from datetime import date, datetime, time
from odoo.exceptions import UserError

class TechnicalOrder(models.Model):
    _name = 'technical.order'
    _description = 'Technical Order'

    name_seq = fields.Char(string='Sequence',readonly=True,attrs="{'readonly': [('status', 'in',('approve','reject','cancel'))]}")
    request_name = fields.Char(string='Request Name', required=True,attrs="{'readonly': [('status', 'in',('approve','reject','cancel'))]}")
    requested_by = fields.Many2one('res.users', string='Requested By', required=True, default=lambda self: self.env.user,attrs="{'readonly': [('status', 'in',('approve','reject','cancel'))]}")
    customer = fields.Many2one('res.partner', string='Customer',attrs="{'readonly': [('status', 'in',('approve','reject','cancel'))]}")
    start_date = fields.Date(string='Start Date', default=fields.Date.today,attrs="{'readonly': [('status', 'in',('approve','reject','cancel'))]}")
    end_date = fields.Date(string='End Date',attrs="{'readonly': [('status', 'in',('approve','reject','cancel'))]}")
    rejection_reason = fields.Text(string='Rejection Reason',attrs="{'readonly': [('status', 'in',('approve','reject','cancel'))]}")
    order_lines = fields.One2many('technical.order.lines', 'order_id', string='Order Lines',attrs="{'readonly': [('status', 'in','(approve','reject','cancel'))]}")
    sales_id = fields.Many2one('sale.order')
    technical_id=fields.One2many('sale.order',"sale_order_id")
    order_count=fields.Integer(string='Order Count',compute='compute_order_count')
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True,attrs="{'readonly': [('status', 'in',('approve','reject','cancel'))]}")
    status = fields.Selection(
        [('draft', 'Draft'),
        ('to_be_approved', 'To be Approved'),
        ('approve', 'Approve'),
         ('reject', 'Reject'),
        ('cancel', 'Cancel'), ]
        , string='Status', default='draft')


    @api.model
    def create(self, values):
        values['name_seq'] = self.env["ir.sequence"].next_by_code("technical_order")
        return super(TechnicalOrder, self).create(values)

    ###########################

    @api.depends('order_lines.total')
    def _compute_total_price(self):
        for order in self:
            order.total_price = sum(order.order_lines.mapped('total'))

    def compute_order_count(self):
        for reccord in self:
            reccord.order_count = self.env['sale.order'].search_count([('sale_order_id', '=', reccord.id)])


    def action_order_count(self):
        return {
            'name': 'Technical Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': ' tree,form',
            'domain': [('sale_order_id', '=', self.id)],


        }




    def action_submit_for_approval(self):
        self.status = 'to_be_approved'

    def action_cancel(self):
        self.status = 'cancel'

    def action_reset_to_draft(self):
        self.status = 'draft'

    def action_approve(self):
            self.status = 'approve'
            # Send email to all users in sale manager group
            sale_managers = self.env.ref("technical_order_module.group_sale_manager").users
            email_list = sale_managers.mapped('email')
            email_subject = f"Technical Order ({self.name_seq}) has been approved"
            email_body = f"The Technical Order {self.name_seq} has been approved"
            self.env['mail.mail'].create({
                'email_to': ','.join(email_list),
                'subject': email_subject,
                'body_html': email_body,
            }).send()



    def action_reject(self):
        return {
            'name': 'Rejection Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'rejection.reason',
            'target': 'new',
        }

    def action_create_so(self):
        sale_list = []
        for sale in self.order_lines:
            sup_quantity = sale.sup_quantity
            if sup_quantity > 0:
                sale_list.append(
                    (0, 0, {
                        'product_id': sale.product_id.id,
                        'product_uom_qty': sup_quantity,
                        'price_unit': sale.price,
                        'name': sale.Description,
                        'technical_order_line_id': sale.id  # Assuming this field expects a single record
                    })
                )

        # Create the sale order and obtain its ID
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'sale_order_id': self.id,
            'state': 'draft',
            'order_line': sale_list,
        })




class SaleOrder(models.Model):
        _inherit = "sale.order"

        sale_order_id = fields.Many2one("technical.order", "Technical Order")


