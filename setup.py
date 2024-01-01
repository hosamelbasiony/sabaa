import frappe

def after_install():
	delete_bad_gender_fields()


def before_uninstall():
    pass

def delete_bad_gender_fields():
	genders = frappe.get_list('Gender')
    for gender in genders:
        if gender["name"] not in ["Male", "Female"]:
            frappe.db.delete('Gender', gender)
		    frappe.clear_cache()