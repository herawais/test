# -*- coding: utf-'8' "-*-"
import logging
from urllib import parse
from odoo import api, fields, models
from odoo.addons.payment.models.payment_provider import ValidationError
# from odoo.exceptions import UserError, ValidationError
from odoo.addons.payment_payfast.controllers.main import PayfastController

_logger = logging.getLogger(__name__)


# class AcquirerPayfast(models.Model):
#     _inherit = 'payment.provider'
#
#     merchant_id = fields.Integer('Merchant ID', required_if_provider='payfast')
#     merchant_key = fields.Char('Merchant Key', required_if_provider='payfast')
#     code = fields.Selection(selection_add=[('payfast', 'Payfast')], ondelete={'payfast': 'set default'})
#
#
#     def payfast_form_generate_values(self, values):
#         item_name = ''
#         reference = values.get('reference')
#         tx = self.env['payment.transaction'].search([('reference', '=', reference)])
#         if reference == tx.reference:
#             tx.request_payload = values
#         sale_orders = tx.sale_order_ids
#         for sale_order in sale_orders:
#             for line in sale_order.order_line:
#                 item_name = item_name + line.product_id.name + '_'
#         currency_id =  self.env['res.currency'].sudo().search([('name','=','ZAR')], limit=1)
#         if currency_id.id != sale_orders[0].pricelist_id.currency_id.id:
#             base_price = sale_order[0].pricelist_id.currency_id._compute(sale_order[0].pricelist_id.currency_id, currency_id, values.get('amount'),True)
#             base_price = float('%.2f' % (base_price))
#         else:
#             base_price = values.get('amount')
#         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
#         payfast_tx_values = dict(values)
#         payfast_tx_values.update({
#             'merchant_id': self.merchant_id,
#             'merchant_key': self.merchant_key,
#             'amount': base_price,
#             'item_name': item_name,
#             'return_url': '%s' % parse.urljoin(base_url, PayfastController.return_url),
#             'cancel_url': '%s' % parse.urljoin(base_url, PayfastController.cancel_url),
#             'notify_url': '%s' % parse.urljoin(base_url, PayfastController.notify_url),
#             'custom_str1': reference,
#         })
#         return payfast_tx_values
#
#
#     def payfast_get_form_action_url(self):
#         if self.state == 'enabled':
#             return 'https://www.payfast.co.za/eng/process'
#         else:
#             return 'https://sandbox.payfast.co.za/eng/process'


# class TxPayfast(models.Model):
#     _inherit = 'payment.transaction'
#
#     # --------------------------------------------------
#     # FORM RELATED METHODS
#     # --------------------------------------------------
#
#     payfast_txn_id = fields.Char(string="Payfast Transaction ID")
#     request_payload = fields.Text('Request Payload')
#     response_payload = fields.Text('Response Payload')
#
#     @api.model
#     def _payfast_form_get_tx_from_data(self, data):
#         reference = data.get('custom_str1')
#         tx_ids = self.env['payment.transaction'].search([('reference', '=', reference)])
#         if not tx_ids or len(tx_ids) > 1:
#             error_msg = 'Payfast: received data for reference %s' % (reference)
#             if not tx_ids:
#                 error_msg += '; no order found'
#             else:
#                 error_msg += '; multiple order found'
#             _logger.error(error_msg)
#             raise ValidationError(error_msg)
#
#         return tx_ids[0]
#
#
#     def _payfast_form_validate(self, data):
#         self.write({'payfast_txn_id': data['pf_payment_id']})
#         if data['status'] == 'COMPLETE':
#             self._set_done()
#             return True
#         else:
#             self.write({'state': 'error'})
#             return False
