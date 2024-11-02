import frappe
from frappe import _

def on_submit(doc, method):
    # Check if there are any attachments linked to the document
    attachments = frappe.get_all('File', filters={'attached_to_doctype': doc.doctype, 'attached_to_name': doc.name})
    
    if not attachments:
        frappe.throw(_("Please Attach a Reference Document."))