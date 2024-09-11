import frappe
import json
from frappe import _

@frappe.whitelist()
def asset_maintenance_tasks2(self):
        if frappe.form_dict.message:
            data = json.loads(frappe.form_dict.message)
            asset_name = data.get("asset_name")
            record = data.get("record")  
        
    
        if record:
            new_ms = frappe.new_doc("VF Asset Maintenance Schedule")
            new_ms.asset_name = asset_name
            new_ms.asset = asset_name  #record.get("name")
            new_ms.maintenance_team = record.get("maintenance_team")
            new_ms.company = record.get("company")
            new_ms.asset_maintenance_schedule_name = record.get("name") 
        
        for item in record.get("upande_vf_custom/upande_vf_custom/custom_asset_scripts/asset.py"):
            new_ms.append("asset_maintenance_tasks", {
                "maintenance_task": item.get("maintenance_task"),
                "maintenance_status": item.get("maintenance_status"),
                "periodicity": item.get("periodicity"),
                "assign_to": item.get("assign_to"),
                "next_due_date": item.get("next_due_date"),
                "assign_to_name": item.get("assign_to_name"),
                "description": item.get("description"),
                "start_date": item.get("start_date"),
                "end_date": item.get("end_date")
                
            })
        
        new_ms.insert()
        
        frappe.response['message'] = new_ms.name

