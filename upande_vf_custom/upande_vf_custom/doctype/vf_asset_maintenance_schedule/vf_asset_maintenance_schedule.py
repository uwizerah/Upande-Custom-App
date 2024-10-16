# Copyright (c) 2024, Upande Ltd and contributors
# For license information, please see license.txt
import json
import frappe
from frappe.model.document import Document


class VFAssetMaintenanceSchedule(Document):
    def on_save(self):
        if self.docstatus == 0 and not self.prepared_by:  # Only set prepared_by if not already set
            user_name = frappe.db.get_value("User", {"email": frappe.session.user}, "full_name")
            self.prepared_by = user_name
            frappe.log("Prepared By: {}".format(user_name))  # For debugging


    @frappe.whitelist()
    def create_asset_maintenance_task_record(self):
        if frappe.form_dict.message:
            data = json.loads(frappe.form_dict.message)
            doc = self
            check_date = data.get("log_date")
            asset = doc.get("asset")
            asset_name = doc.get("asset_name")
            schedule = doc.get("name")
            tasks = data.get("tasks")
            asset_maintenance_schedule_name = doc.get("asset_maintenance_schedule_name")
            maintenance_team = data.get("maintenance_team")
            signature = doc.get("signature")
            
            # Fetch prepared_by for the maintenance record
            prepared_by = frappe.db.get_value("User", {"email": frappe.session.user}, "full_name")

            if not asset_name or not tasks:
                frappe.throw("Asset name and tasks are required")

            # Create a new Asset Maintenance Record document
            maintenance_record = frappe.new_doc("VF Asset Maintenance Record")
            maintenance_record.asset = asset
            maintenance_record.asset_name = asset_name
            maintenance_record.check_date = check_date
            maintenance_record.asset_maintenance_schedule_name = asset_maintenance_schedule_name
            maintenance_record.schedule = schedule
            maintenance_record.maintenance_team = maintenance_team
            maintenance_record.signature = signature
            maintenance_record.prepared_by = prepared_by  # Set prepared_by

            # Append completed tasks to the maintenance record
            for maintenance_task in tasks:
                if maintenance_task.get("checked") == 1:
                    maintenance_record.append("asset_maintenance_tasks", {
                        "maintenance_task": maintenance_task.get("maintenance_task"),
                        "maintenance_status": maintenance_task.get("maintenance_status"),
                        "periodicity": maintenance_task.get("periodicity"),
                        "next_due_date": maintenance_task.get("next_due_date"),
                        "assign_to": maintenance_task.get("assign_to"),
                        "assign_to_name": maintenance_task.get("assign_to_name"),
                        "description": maintenance_task.get("description"),
                        "start_date": maintenance_task.get("start_date"),
                        "end_date": maintenance_task.get("end_date")
                    })

            maintenance_record.insert()
            maintenance_record.submit()
            
            frappe.response['message'] = maintenance_record.name
