import frappe

def before_submit(doc, method):
    # #  'Pending Approval (Finance Manager)' state
    # if doc.workflow_state == 'Pending Approval (Finance Manager)' and not doc.custom_approved_by_supervisor:
    #     user_name = frappe.db.get_value("User", {"email": frappe.session.user}, "full_name")
    #     doc.custom_approved_by_supervisor = user_name
    #     frappe.msgprint(f"Supervisor approval: {user_name}")
    
    # 'Approved' state
    if doc.workflow_state == 'Approved' and not doc.custom_approved_by:
        user_name = frappe.db.get_value("User", {"email": frappe.session.user}, "full_name")
        doc.custom_approved_by = user_name
        
        
        # frappe.msgprint(f"User name fetched: {user_name}")

   

