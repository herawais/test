# -*- coding: utf-'8' "-*-"
import logging
from werkzeug import urls
from urllib import parse
from odoo import api, fields, models
from odoo.addons.payment.models.payment_provider import ValidationError
# from odoo.exceptions import UserError, ValidationError
from odoo.addons.payment_payfast.controllers.main import PayfastController
from odoo.addons.payment import utils as payment_utils


_logger = logging.getLogger(__name__)


class TxPayfast(models.Model):
    _inherit = 'payment.transaction'

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    payfast_txn_id = fields.Char(string="Payfast Transaction ID")
    request_payload = fields.Text('Request Payload')
    response_payload = fields.Text('Response Payload')



    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Paypal-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'payfast':
            return res
        item_name = ''
        reference = processing_values.get('reference')
        tx = self.env['payment.transaction'].search([('reference', '=', reference)])
        if reference == tx.reference:
            tx.request_payload = processing_values
        sale_orders = tx.sale_order_ids
        for sale_order in sale_orders:
            for line in sale_order.order_line:
                item_name = item_name + line.product_id.name + '_'
        currency_id = self.env['res.currency'].sudo().search([('name', '=', 'ZAR')], limit=1)
        if currency_id.id != sale_orders[0].pricelist_id.currency_id.id:
            base_price = sale_order[0].pricelist_id.currency_id._compute(sale_order[0].pricelist_id.currency_id,
                                                                         currency_id, processing_values.get('amount'), True)
            base_price = float('%.2f' % (base_price))
        else:
            base_price = processing_values.get('amount')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        payfast_tx_values = dict(processing_values)
        payfast_tx_values.update({

            'merchant_id': self.provider_id.merchant_id,
            'merchant_key': self.provider_id.merchant_key,
            'amount': base_price,
            'item_name': item_name,
            'return_url': '%s' % parse.urljoin(base_url, PayfastController.return_url),
            'cancel_url': '%s' % parse.urljoin(base_url, PayfastController.cancel_url),
            # 'notify_url': '%s' % parse.urljoin(base_url, PayfastController.notify_url),
            'notify_url': 'https://d8ca-119-155-13-186.in.ngrok.io',
            'custom_str1': reference,
            'api_url': self.provider_id.payfast_get_form_action_url(),
        })
        return payfast_tx_values


    # @api.model
    # def _payfast_form_get_tx_from_data(self, data):
    #     reference = data.get('custom_str1')
    #     tx_ids = self.env['payment.transaction'].search([('reference', '=', reference)])
    #     if not tx_ids or len(tx_ids) > 1:
    #         error_msg = 'Payfast: received data for reference %s' % (reference)
    #         if not tx_ids:
    #             error_msg += '; no order found'
    #         else:
    #             error_msg += '; multiple order found'
    #         _logger.error(error_msg)
    #         raise ValidationError(error_msg)
    #
    #     return tx_ids[0]


    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on Paypal data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'payfast' or len(tx) == 1:
            return tx

        reference = notification_data.get('custom_str1')
        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'payfast')])
        if not tx:
            raise ValidationError(
                "PayFast: " + _("No transaction found matching reference %s.", reference)
            )
        return tx








    def _process_notification_data(self, notification_data):
        self.write({'payfast_txn_id': notification_data['pf_payment_id']})
        if notification_data['status'] == 'COMPLETE':
            self._set_done()
            return True
        else:
            self.write({'state': 'error'})
            return False