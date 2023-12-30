# Copyright (c) 2023, Hosam and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MedicalCode(Document):
	def autoname(self):
		self.name = self.medical_code_standard + " " + self.code
