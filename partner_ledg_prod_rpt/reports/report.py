from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class PartnerLedgerReport(models.AbstractModel):
    _name = 'report.partner_ledg_prod_rpt.prtnr_ldgr_rpt_prod_wise'
    _description = "Partner ledger report product Wise"

    @api.model
    def _get_report_values(self, docids, data=None):
        if self.env.context.get('from_wizard'):
            docs = self.env['res.partner'].browse(data['active_id'])
            account_data = self.env['account.move.line'].search(
                [('partner_id', '=', docs.id), ('create_date', '>=', datetime.fromisoformat(data['date_from'])),
                 ('create_date', '<=', datetime.fromisoformat(data['to_date']))], order='create_date asc')
        else:
            docs = self.env['res.partner'].browse(docids)
            account_data = self.env['account.move.line'].search(
                [('partner_id', '=', docs.id)], order='create_date asc')

        ledger_data = []

        if self.env.context.get('from_wizard'):
            filter_rec = account_data.filtered(
                lambda x: x.move_id.journal_id.id in data['journal_ids']
            )

            invoices_bills = filter_rec.filtered(lambda move: move.move_id.move_type in ['out_invoice', 'in_invoice'])
            invoices_bills = filter_rec.filtered(
                lambda move: move.account_id.user_type_id.name not in ['Payable', 'Receivable'])
            filter_rec = invoices_bills
            filter_rec = self.filter_data(filter_rec)

        for rec in filter_rec:
            ledger_data.append(
                {
                    'date': rec.date,
                    'journal': rec.move_id.name,
                    'account': rec.account_id.name,
                    'label': rec.name,
                    'debit': rec.debit,
                    'credit': rec.credit,
                    'balance': rec.balance,
                    'ref': rec.payment_id.ref
                }
            )

        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': docs,
            'ledger_data': ledger_data
        }

    def filter_data(self, filter_rec=None):

        # Output account
        prod_catg_output_acc_ids = list(
            set([filter_rec[i].product_id.categ_id.property_stock_account_output_categ_id.id for i in
                 range(len(filter_rec))]))

        # Expense Account
        prod_catg_expense_acc_ids = list(
            set([filter_rec[i].product_id.categ_id.property_account_expense_categ_id.id for i in
                 range(len(filter_rec))]))

        # Remove False Values
        combine_all_acc_ids = set(prod_catg_output_acc_ids + prod_catg_expense_acc_ids)
        combine_all_acc_ids = list(filter(bool, combine_all_acc_ids))

        filter_rec = filter_rec.filtered(
            lambda x: x.account_id.id not in combine_all_acc_ids
        )
        return filter_rec
