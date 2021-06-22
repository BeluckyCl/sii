# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.main import serialize_exception,content_disposition
import base64
import logging
_logger = logging.getLogger(__name__)

class L10nClCert(http.Controller):
    @http.route('/l10n_cl_cert/enviodtes', auth='user', methods=['GET'])
    def index(self, **kw):
        values = dict(kw)
        
        # _logger.info('values: {}'.format(values))
        docs = values["doc"].split(",")
        model = http.request.env["account.move"]
        content = model._xml_dte_list(docs)
        # _logger.info('contenido: {}'.format(content))
        # _logger.info('fin de contenido')

        filecontent = content
        filename = "envio.xml"
        return http.request.make_response(filecontent,
                            [('Content-Type', 'application/octet-stream'),
                             ('Content-Disposition', content_disposition(filename))])
    
    @http.route('/l10n_cl_cert/enviolibro', auth='user', methods=['GET'])
    def index(self, **kw):
        
        model = http.request.env["account.move"]
        content = model._xml_libro_signed()
        _logger.info('contenido: {}'.format(content))

        filecontent = content
        filename = "libro.xml"
        return http.request.make_response(filecontent,
                            [('Content-Type', 'application/octet-stream'),
                             ('Content-Disposition', content_disposition(filename))])

#     @http.route('/l10n_cl_cert/l10n_cl_cert/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_cl_cert.listing', {
#             'root': '/l10n_cl_cert/l10n_cl_cert',
#             'objects': http.request.env['l10n_cl_cert.l10n_cl_cert'].search([]),
#         })

#     @http.route('/l10n_cl_cert/l10n_cl_cert/objects/<model("l10n_cl_cert.l10n_cl_cert"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_cl_cert.object', {
#             'object': obj
#         })
