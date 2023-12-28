import frappe
from frappe.model.document import Document
from healthcare.healthcare.doctype.patient.patient import Patient

class MyPatient(Patient):
	# def onload(self):
	# 	super(MyPatient, self).onload()

	def set_full_name(self):
		print("###########################################################")
		print("###########################################################")
		print("###########################################################")
		if self.last_name:
			if self.middle_name:
				self.patient_name = " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))
			else:
				self.patient_name = " ".join(filter(None, [self.first_name, self.last_name]))
		else:
			self.patient_name = self.first_name

	def validate(self):
		super(MyPatient, self).validate()
		self.set_full_name()
		# self.flags.is_new_doc = self.is_new()
		# self.flags.existing_customer = self.is_new() and bool(self.customer)