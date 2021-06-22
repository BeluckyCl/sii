# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
from html import unescape

import logging
_logger = logging.getLogger(__name__)

class AccountInvoiceReference(models.Model):
    _inherit = 'l10n_cl.account.invoice.reference'
    l10n_cl_reference_doc_type_selection = fields.Selection(selection_add=[("SET", "(SET) Set de Pruebas para SII"),],
                                                           ondelete={'SET': 'set default'}, default="34")
    
    

class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move']
    
    def _xml_dte_list(self, dte_names):
        first_doc = None
        subtotals = self.env["account.move"].read_group([("name", "in", dte_names)], 
                                                   fields=["l10n_latam_document_type_id"],
                                                   groupby=["l10n_latam_document_type_id"])
        tipodte_subtotals = []
        for each in subtotals:
            code = self.env["l10n_latam.document.type"].search([("id", "=", 
                                                             each["l10n_latam_document_type_id"][0])]).code
            count = each["l10n_latam_document_type_id_count"]
            tipodte_subtotals.append({'code': code,
                            'count': count})
        dtes = []
        for each in dte_names:
            dte_attachment = self.env["account.move"].search([("name", "=", each)])[0]
            dtes.append(base64.b64decode(dte_attachment.l10n_cl_dte_file.datas).decode('ISO-8859-1'))
            if not first_doc:
                first_doc = dte_attachment

        digital_signature = first_doc.company_id._get_digital_signature(user_id=self.env.user.id)
        template = self.env.ref('l10n_cl_cert.envio_dte_cert')
        # _logger.info('Previo a render: {}'.format(tipodte_subtotals))
        dte_rendered = template._render({
            'RutEmisor': self._l10n_cl_format_vat(first_doc.company_id.vat),
            'RutEnvia': first_doc.company_id._get_digital_signature(user_id=self.env.user.id).subject_serial_number,
            'RutReceptor': first_doc.partner_id.vat,
            'FchResol': first_doc.company_id.l10n_cl_dte_resolution_date,
            'NroResol': first_doc.company_id.l10n_cl_dte_resolution_number,
            'TmstFirmaEnv': self._get_cl_current_strftime(),
            'dtes': dtes,
            'tipodte_subtotals': tipodte_subtotals
        })
        #_logger.info('Despues del render')
        dte_rendered = unescape(dte_rendered.decode('utf-8')).replace('<?xml version="1.0" encoding="ISO-8859-1" ?>', '')
        _logger.info('Despues de Unescape: {}'.format(dte_rendered))
        dte_signed = self._sign_full_xml(
            dte_rendered, digital_signature, 'SetDoc',
            'env',
            False
        )
        dte_final = dte_signed.encode('iso-8859-1')
        # _logger.info('Despues de Sign')
        # _logger.info('Envío DTE: {}'.format(dte_final))
        return (dte_final)

    def _xml_libro_signed(self):
        company = self.env["res.company"].search([])[0]
        digital_signature = company._get_digital_signature(user_id=self.env.user.id)
        libro_venta = unescape(base64.b64decode(company.x_libro_venta).
                               decode("utf-8")).replace('<?xml version="1.0" encoding="ISO-8859-1"?>', '')
        _logger.info('Envío Libro: {}'.format(libro_venta))
        libro_signed = self._sign_full_xml(
            libro_venta, digital_signature, 'EnvioLibro',
            'book',
            False
            # SetDoc -> EnvioLibro
            # env -> libro (</LibroCompraVenta>)
        )
        libro_final = libro_signed.encode('iso-8859-1')
        # _logger.info('Despues de Sign')
        # _logger.info('Envío DTE: {}'.format(dte_final))
        return (libro_final)


    
class L10nClEdiUtilMixin(models.AbstractModel):
    _name = 'l10n_cl.edi.util'
    _inherit = ['l10n_cl.edi.util']

    def _l10n_cl_append_sig(self, xml_type, sign, message):
        tag_to_replace = {
            'doc': '</DTE>',
            'bol': '</EnvioBOLETA>',
            'env': '</EnvioDTE>',
            'recep': '</Recibo>',
            'env_recep': '</EnvioRecibos>',
            'env_resp': '</RespuestaDTE>',
            'consu': '</ConsumoFolios>',
            'token': '</getToken>',
            'book': '</LibroCompraVenta>',
        }
        tag = tag_to_replace.get(xml_type, '</EnvioBOLETA>')
        return message.replace(tag, sign + tag)
    
# class l10n_cl_cert(models.Model):
#     _name = 'l10n_cl_cert.l10n_cl_cert'
#     _description = 'l10n_cl_cert.l10n_cl_cert'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
