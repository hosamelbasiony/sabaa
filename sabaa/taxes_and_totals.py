# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
import json
from frappe.utils import flt
from frappe.utils import cstr, flt, get_link_to_form, rounded, time_diff_in_hours
from math import ceil

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

def calculate_patient_insurance_coverage(selfie):
	self = selfie.doc
	total_amount_to_pay = 0.0
	total_coverage_amount = 0.0

	included = []
	# included.append("Cricket")

	patient_policies = frappe.get_list(
		'Patient Insurance Policy',
		fields = '*',
		# filters = {'patient': self.patient} 
	)

	if len(patient_policies):

		patient_policy = patient_policies[0]

		eligibility_list = frappe.get_list(
				'Item Insurance Eligibility',
				fields = '*',
				filters = [
					{'insurance_plan': patient_policy["insurance_plan"]},
				]
			)
		
		price_list = frappe.get_list(
				'Item Price',
				fields = '*',
				filters = [
					{'price_list':  "تأمين 1"}
				]
			)
		
		# print(price_list)
		
		for item in self.items:				
			for x in price_list:
				if x.item_code == item.item_code:
					item.rate = x.price_list_rate
					item.amount = x.price_list_rate
					# pass

			for x in eligibility_list:
				if x.item_code == item.item_code:
					if x.coverage != 0 and item.amount:
						item.custom_insurance_coverage = flt(x.coverage)
						item.custom_insurance_coverage_amount = flt(item.qty) * flt(item.amount) * 0.01 * flt(item.custom_insurance_coverage)

					if item.custom_insurance_coverage_amount and flt(item.custom_insurance_coverage_amount) > 0:
						total_coverage_amount += flt(item.custom_insurance_coverage_amount)
						print("***************************")
						print(item.qty)
						print(item.amount)

			total_amount_to_pay += flt(item.qty) * flt(item.amount)
		    # ceil()

		self.custom_total_insurance_coverage_amount = ceil(total_coverage_amount)

		# self.custom_patient_payable_amount = 111

		frappe.msgprint(str(self.custom_total_insurance_coverage_amount))

		if self.custom_total_insurance_coverage_amount:
			self.custom_patient_payable_amount = self.outstanding_amount - self.custom_total_insurance_coverage_amount
		else:
			self.custom_patient_payable_amount = self.outstanding_amount


class custom_calculate_taxes_and_totals(object):	

	def calculate_outstanding_amount(self):
		# NOTE:
		# write_off_amount is only for POS Invoice
		# total_advance is only for non POS Invoice
		frappe.msgprint("Custom calculate_outstanding_amount")
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
		
		print("🏠🏠🏠🏠🏠 calculate patient and insurance fees in sabaa taxes and totals  🏠🏠🏠🏠🏠🏠🏠")
		
		calculate_patient_insurance_coverage(self)

	
	def calculate_outstanding_amount_bak(self):
		frappe.msgprint("HERE HERE HERE HERE HERE HERE HERE HERE")
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

		print("🏠🏠🏠🏠🏠 calculate patient and insurance fees in sabaa taxes and totals  🏠🏠🏠🏠🏠🏠🏠")
		
		calculate_patient_insurance_coverage(self)

	
	
	def calculate_patient_insurance_coveragee(self):
		# total_coverage_amount = 0.0

		# for item in self.items:
		# 	if item.amount and item.custom_insurance_coverage:
		# 		item.custom_insurance_coverage_amount = item.amount * 0.01 * flt(item.coverage_percentage)

		# 	if item.custom_insurance_coverage_amount and flt(item.custom_insurance_coverage_amount) > 0:
		# 		total_coverage_amount += flt(item.custom_insurance_coverage_amount)

		# self.total_insurance_coverage_amount = total_coverage_amount
		# if self.total_insurance_coverage_amount:
		# 	self.patient_payable_amount = self.outstanding_amount - self.total_insurance_coverage_amount
		# else:
		# 	self.patient_payable_amount = self.
		
		total_amount_to_pay = 0.0
		total_coverage_amount = 0.0

		patient_policies = frappe.get_list(
			'Patient Insurance Policy',
			fields = '*',
			filters = {'patient': self.patient} #, 'active': True}
		)

		print(patient_policies)

		self.custom_patient_payable_amount = 17.5

		# if len(patient_policies):

		# 	patient_policy = patient_policies[0]

		# 	self.custom_patient_insurance_policy = patient_policy.name
		# 	self.custom_insurance_eligibility_plan = patient_policy.insurance_plan
		# 	self.custom_insurance_payor = patient_policy.insurance_payor


		# 	eligibility_list = frappe.get_list(
		# 			'Item Insurance Eligibility',
		# 			fields = '*',
		# 			filters = [
		# 				{'insurance_plan': patient_policy.insurance_plan},
		# 				{'item_code': item.item_code}
		# 			]
		# 		)
			
		# 	price_list = frappe.get_list(
		# 			'Item Price',
		# 			fields = '*',
		# 			filters = [
		# 				{'price_list':  "تأمين 1"}
		# 			]
		# 		)
		# 	print(price_list)
			
		# 	for item in self.items:
		# 		for x in price_list:
		# 			if x.item_code == item.item_code:
		# 				item.rate = x.price_list_rate
		# 				item.amount = x.price_list_rate
		# 				item.base_rate = x.price_list_rate
		# 				item.base_net_rate = x.price_list_rate
		# 				item.stock_uom_rate = x.price_list_rate
		# 				item.net_rate = x.price_list_rate

		# 		for x in eligibility_list:
		# 			if x.item_code == item.item_code:
		# 				if x.coverage != 0 and item.amount:
		# 					# base_net_rate
		# 					# amount
		# 					# base_rate
		# 					# stock_uom_rate
		# 					# net_rate

		# 					# base_amount
		# 					# base_net_amount
		# 					# net_amount
		# 					# custom_insurance_coverage_amount
		# 					item.custom_insurance_coverage = flt(x.coverage)
		# 					item.custom_insurance_coverage_amount = flt(item.amount) * flt(item.qty) * 0.01 * flt(item.custom_insurance_coverage)

		# 					item.base_amount = item.custom_insurance_coverage_amount
		# 					item.base_net_amount = item.custom_insurance_coverage_amount
		# 					item.net_amount = item.custom_insurance_coverage_amount

		# 				if item.custom_insurance_coverage_amount and flt(item.custom_insurance_coverage_amount) > 0:
		# 					total_coverage_amount += flt(item.custom_insurance_coverage_amount)

		# 	self.custom_insurance_coverage_amount = total_coverage_amount

		# for item in self.items:
		# 	total_amount_to_pay += flt(item.amount) * flt(item.qty)
		# 	frappe.msgprint(item.item_code + " - amount_to_pay - " + str(flt(item.amount) * flt(item.qty)))

		# self.custom_patient_payable_amount = total_amount_to_pay - total_coverage_amount
