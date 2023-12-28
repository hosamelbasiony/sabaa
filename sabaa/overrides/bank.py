import frappe
from frappe.model.document import Document
from erpnext.accounts.doctype.bank.bank import Bank

from frappe.contacts.address_and_contact import (
	delete_contact_and_address,
	load_address_and_contact,
)

class MyBank(Bank):
	def onload(self):
		super(MyBank, self).onload()
		# frappe.msgprint("After super onload")

	def validate(self):
		if len(self.swift_number) < 3:
			frappe.msgprint("Swift number must be at least 3 digits")
			raise frappe.ValidationError

# @frappe.whitelist(allow_guest=True)
# def get_user_info():
# 	return {
# 		"user": "I am a dummy user", # frappe.session.user,
# 		"user_type": "Dummy", # frappe.session.data.user_type,
# 	}