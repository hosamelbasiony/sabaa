# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe.utils import flt

class custom_calculate_taxes_and_totals(object):

	def custom_calculate_outstanding_amount(self):
		# NOTE:
		# write_off_amount is only for POS Invoice
		# total_advance is only for non POS Invoice

		if self.doc.doctype == "Sales Invoice":
			self.calculate_paid_amount()

		if (
			self.doc.is_return
			and self.doc.return_against
			and not self.doc.get("is_pos")
			or self.is_internal_invoice()
		):
			return

		self.doc.round_floats_in(self.doc, ["grand_total", "total_advance", "write_off_amount"])
		self._set_in_company_currency(self.doc, ["write_off_amount"])

		if self.doc.doctype in ["Sales Invoice", "Purchase Invoice"]:
			grand_total = self.doc.rounded_total or self.doc.grand_total
			base_grand_total = self.doc.base_rounded_total or self.doc.base_grand_total

			if self.doc.party_account_currency == self.doc.currency:
				total_amount_to_pay = flt(
					grand_total - self.doc.total_advance - flt(self.doc.write_off_amount),
					self.doc.precision("grand_total"),
				)
			else:
				total_amount_to_pay = flt(
					flt(base_grand_total, self.doc.precision("base_grand_total"))
					- self.doc.total_advance
					- flt(self.doc.base_write_off_amount),
					self.doc.precision("base_grand_total"),
				)

			self.doc.round_floats_in(self.doc, ["paid_amount"])
			change_amount = 0

			if self.doc.doctype == "Sales Invoice" and not self.doc.get("is_return"):
				self.calculate_change_amount()
				change_amount = (
					self.doc.change_amount
					if self.doc.party_account_currency == self.doc.currency
					else self.doc.base_change_amount
				)

			paid_amount = (
				self.doc.paid_amount
				if self.doc.party_account_currency == self.doc.currency
				else self.doc.base_paid_amount
			)

			self.doc.outstanding_amount = flt(
				total_amount_to_pay - flt(paid_amount) + flt(change_amount),
				self.doc.precision("outstanding_amount"),
			)

			if (
				self.doc.doctype == "Sales Invoice"
				and self.doc.get("is_pos")
				and self.doc.get("pos_profile")
				and self.doc.get("is_consolidated")
			):
				write_off_limit = flt(
					frappe.db.get_value("POS Profile", self.doc.pos_profile, "write_off_limit")
				)
				if write_off_limit and abs(self.doc.outstanding_amount) <= write_off_limit:
					self.doc.write_off_outstanding_amount_automatically = 1

			if (
				self.doc.doctype == "Sales Invoice"
				and self.doc.get("is_pos")
				and self.doc.get("is_return")
				and not self.doc.get("is_consolidated")
			):
				self.set_total_amount_to_default_mop(total_amount_to_pay)
				self.calculate_paid_amount()
