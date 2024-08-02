from odoo import api, models, fields, _
from datetime import date, timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta


class PartnerLedgerReport(models.TransientModel):
    _name = 'partner.ledger.report'

    date_from = fields.Datetime("Date From", default=lambda self: self._get_date())
    to_date = fields.Datetime("To Date", default=fields.datetime.now())
    journal_ids = fields.Many2many('account.journal',
                                   'partner_ledger_item_report_rel',
                                   'account_id', 'journal_id',
                                   string='Journals', required=True, default=lambda self: self._get_default_ids())

    def print_report(self):
        self.with_context(date_from=self.date_from)
        data = {'date_from': self.date_from, 'to_date': self.to_date, 'active_id': self.env.context['active_id'],
                'journal_ids': self.journal_ids.ids}
        return self.env.ref('partner_ledg_prod_rpt.prtnr_ldgr_rpt_prod_wise').report_action(self, data=data,
                                                                                            config=False)

    def _get_date(self):
        minus_month = datetime.now() - relativedelta(months=1)
        return minus_month

    def _get_default_ids(self):
        all_ids = self.env['account.journal'].search([('id', 'not in', [16, 5])])
        return all_ids
