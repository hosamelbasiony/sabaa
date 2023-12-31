import frappe
from frappe import _
from frappe.utils import flt, money_in_words, round_based_on_smallest_currency_fraction
from functools import reduce
import json

@frappe.whitelist()
def get_insurance_data(patient_name, items):
	patient = frappe.get_doc("Patient", patient_name);
	patient_policies = []
	eligibility = []
	items = json.loads(items)
	item_codes = tuple(items)

	if patient:		
		
		patient_policies = frappe.get_list(
			'Patient Insurance Policy',
			fields = '*',
			filters = {'patient': patient_name} #, 'active': True}
		)

		if len(patient_policies):
			patient_policy = patient_policies[0]
			# http://192.168.1.211:8002/api/resource/Item Insurance Eligibility?fields=["*"]&filters=[["insurance_plan", "=", "خطة التأمين الذهبي"]]
			# insurance_plan
			eligibility = frappe.get_list(
				'Item Insurance Eligibility',
				fields = '*',
				filters = [
					{'insurance_plan': patient_policy["insurance_plan"]},
					{'item_code': ('in', item_codes)}
				] #, 'active': True}
			)

			if len(eligibility):
				# item_codes = tuple([x["item_code"] for x in eligibility])				
				included_procedures = frappe.get_list(
					'Clinical Procedure',
					fields = '*',
					filters={'procedure_template':('in', item_codes)}
				)

				included_items = frappe.get_list(
					'Item',
					fields = '*',
					filters={'name':('in', item_codes)}
				)

				return {
					"patient": patient,
					"patient_policies": patient_policies,
					"eligibility": eligibility,
					"included_procedures": [],
					"included_items": included_items
				}

	return {
		"patient": patient,
		"patient_policies": patient_policies,
		"eligibility": eligibility,
	}

	if patient and False:
		patient = frappe.get_doc("Patient", encounter.patient)
		if patient:
			if patient.customer:
				orders_to_invoice = []
				medication_requests = frappe.get_list(
					'Medication Request',
					fields=['*'],
					filters={
						'patient': patient.name,
						'order_group': encounter.name,
						'billing_status': ['in', ['Pending', 'Partly Invoiced']],
						'docstatus': 1
					}
				)
				for medication_request in medication_requests:
					item, is_billable = frappe.get_cached_value('Medication', medication_request.medication,
						['item', 'is_billable'])

					description = ''
					if medication_request.dosage and medication_request.period:
						description = _('{0} for {1}').format(medication_request.dosage, medication_request.period)

					if is_billable:
						billable_order_qty = medication_request.get('quantity', 1) - medication_request.get('qty_invoiced', 0)
						if medication_request.number_of_repeats_allowed:
							if medication_request.total_dispensable_quantity >= medication_request.quantity + medication_request.qty_invoiced:
								billable_order_qty = medication_request.get('quantity', 1)
							else:
								billable_order_qty = medication_request.total_dispensable_quantity - medication_request.get('qty_invoiced', 0)

						orders_to_invoice.append({
							'reference_type': 'Medication Request',
							'reference_name': medication_request.name,
							'drug_code': item,
							'quantity': billable_order_qty,
							'description': description,
						})
				return orders_to_invoice
