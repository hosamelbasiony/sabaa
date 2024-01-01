import frappe

from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.utils import flt

class SabaaHealthcareSalesInvoice(SalesInvoice):
	print("🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀")
	print("🚀🚀🚀🚀🚀🚀🚀 SABAA SI OVERRIDE 🚀🚀🚀🚀🚀🚀")
	print("🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀")

	def validate(self):
		frappe.msgprint("validate yanma kont nawy abarbahakk")
		super(SabaaHealthcareSalesInvoice, self).validate()
		self.calculate_patient_insurance_coverage()
	

	@frappe.whitelist()
	def set_healthcare_services(self, checked_values):
		from erpnext.stock.get_item_details import get_item_details

		for checked_item in checked_values:
			item_line = self.append("items", {})
			price_list, price_list_currency = frappe.db.get_values(
				"Price List", {"selling": 1}, ["name", "currency"]
			)[0]
			args = {
				"doctype": "Sales Invoice",
				"item_code": checked_item["item"],
				"company": self.company,
				"customer": frappe.db.get_value("Patient", self.patient, "customer"),
				"selling_price_list": price_list,
				"price_list_currency": price_list_currency,
				"plc_conversion_rate": 1.0,
				"conversion_rate": 1.0,
			}
			item_details = get_item_details(args)
			item_line.item_code = checked_item["item"]
			item_line.qty = 1
			if checked_item["qty"]:
				item_line.qty = checked_item["qty"]
			if checked_item["rate"]:
				item_line.rate = checked_item["rate"]
			else:
				item_line.rate = item_details.price_list_rate
			item_line.amount = float(item_line.rate) * float(item_line.qty)
			if checked_item["income_account"]:
				item_line.income_account = checked_item["income_account"]
			if checked_item["dt"]:
				item_line.reference_dt = checked_item["dt"]
			if checked_item["dn"]:
				item_line.reference_dn = checked_item["dn"]
			if checked_item["description"]:
				item_line.description = checked_item["description"]
			if checked_item["dt"] == "Lab Test":
				lab_test = frappe.get_doc("Lab Test", checked_item["dn"])
				item_line.service_unit = lab_test.service_unit
				item_line.practitioner = lab_test.practitioner
				item_line.medical_department = lab_test.department

		frappe.msgprint("hhhhhhhhhhhhhhhhh")

		self.set_missing_values(for_validate=True)
		super(SalesInvoice, self).calculate_taxes_and_totals()
		super(SabaaHealthcareSalesInvoice, self).set_missing_values(for_validate=True)
		self.calculate_patient_insurance_coverage()

	def calculate_patient_insurance_coverage(self):
		total_amount_to_pay = 0.0
		total_coverage_amount = 0.0

		patient_policies = frappe.get_list(
			'Patient Insurance Policy',
			fields = '*',
			filters = {'patient': self.patient} #, 'active': True}
		)

		if len(patient_policies):

			patient_policy = patient_policies[0]


			eligibility_list = frappe.get_list(
					'Item Insurance Eligibility',
					fields = '*',
					filters = [
						{'insurance_plan': patient_policy["insurance_plan"]},
						# {'item_code': item.item_code}
					]
				)
			
			price_list = frappe.get_list(
					'Item Price',
					fields = '*',
					filters = [
						{'price_list':  "تأمين 1"}
					]
				)
			print(price_list)
			
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
							item.custom_insurance_coverage_amount = flt(item.amount) * 0.01 * flt(item.custom_insurance_coverage)

						if item.custom_insurance_coverage_amount and flt(item.custom_insurance_coverage_amount) > 0:
							total_coverage_amount += flt(item.custom_insurance_coverage_amount)

				total_amount_to_pay += item.rate

			self.custom_total_insurance_coverage_amount = total_coverage_amount

			super(SalesInvoice, self).calculate_taxes_and_totals()
			
			# if self.custom_total_insurance_coverage_amount:
			# 	self.custom_patient_payable_amount = self.outstanding_amount - self.custom_total_insurance_coverage_amount
			# else:
			# 	self.custom_patient_payable_amount = self.outstanding_amount
