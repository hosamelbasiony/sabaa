import frappe
from frappe.model.document import Document
from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals

# erpnext/erpnext/controllers/taxes_and_totals.py

class my_calculate_taxes_and_totals(calculate_taxes_and_totals):
	def calculate_outstanding_amount(self):
		frappe.msgprint(
            msg='This file is fery goot',
            title='HI THERE'
        )
		super(my_calculate_taxes_and_totals, self).calculate_outstanding_amount()