// Copyright (c) 2024, Upande Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('VF Asset Maintenance Schedule', {
    refresh: function(frm) {
        // Add the button if not already present
        if (!frm.fields_dict['create_button']) {
            frm.add_custom_button(__('Maintenance Record'), function() {
                // Ensure check_date and signature are provided
                if (!frm.doc.check_date) {
                    frappe.msgprint(__('Please indicate the check date before creating a maintenance record.'));
                    return;
                }
                
                if (!frm.doc.signature) {
                    frappe.msgprint(__('Please provide a signature before creating a maintenance record.'));
                    return;
                }
                
                let all_tasks = frm.doc.asset_maintenance_tasks || [];
                
                if (all_tasks.length === 0) {
                    frappe.msgprint(__('No tasks available to create a maintenance record.'));
                    return;
                }
                
                let checked_tasks = all_tasks.filter(maintenance_task => maintenance_task.checked);
                
                if (checked_tasks.length === 0) {
                    frappe.msgprint(__('No tasks are checked to create a maintenance record.'));
                    return;
                }

                frappe.call({
                    method: "create_asset_maintenance_task_record",
                    doc: frm.doc,
                    args: {
                        message: {
                            maintenance_team: frm.doc.maintenance_team,
                            tasks: checked_tasks.map(task => {
                                return {
                                    maintenance_task: task.maintenance_task,
                                    maintenance_type: task.maintenance_type,
                                    maintenance_status: task.maintenance_status,
                                    periodicity: task.periodicity,
                                    start_date: task.start_date,
                                    end_date: task.end_date,
                                    checked: task.checked,
                                    next_due_date: task.next_due_date,
                                    assign_to: task.assign_to,
                                    assign_to_name: task.assign_to_name,
                                    description: task.description
                                };
                            }),
                            log_date: frappe.datetime.now_date()
                        }
                    },
                    callback: function(response) {
                        if (response.message) {
                            // Reset the 'checked' status and update 'maintenance_status' for each task
                            checked_tasks.forEach(task => {
                                frappe.model.set_value(task.doctype, task.name, 'checked', 0);
                                frappe.model.set_value(task.doctype, task.name, 'maintenance_status', 'Pending');
                            });

                            frm.set_value('signature', ''); // Clear signature
                            frm.set_value('check_date', null); // Clear checkdate

                            frm.refresh_field('signature');
                            frm.refresh_field('check_date');
                            frm.refresh_field('asset_maintenance_tasks');

                            frm.save().then(() => {
                                frappe.msgprint(__('Maintenance Record Created: <a href="/app/vf-asset-maintenance-record/{0}" target="_blank">{0}</a>', [response.message]));
                            });

                        } else {
                            frappe.msgprint(__('Failed to create maintenance record.'));
                        }
                    }
                });
            }, 'Create', 'create_button');
        }
    }
});


frappe.ui.form.on('VF Asset Maintenance Task', {
    checked(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);

        if (row.checked == 1) {
            row.previous_due_date = row.next_due_date;
            row.end_date = frappe.datetime.nowdate();

            let next_due_date;

            if (row.next_due_date) {
                let start_date = row.next_due_date;

                switch (row.periodicity) {
                    case "Daily": next_due_date = frappe.datetime.add_days(start_date, 1); break;
                    case "Weekly": next_due_date = frappe.datetime.add_days(start_date, 7); break;
                    case "Bi-Weekly": next_due_date = frappe.datetime.add_days(start_date, 14); break;
                    case "Monthly": next_due_date = frappe.datetime.add_months(start_date, 1); break;
                    case "Quarterly": next_due_date = frappe.datetime.add_months(start_date, 3); break;
                    case "Half-Yearly": next_due_date = frappe.datetime.add_months(start_date, 6); break;
                    case "Annually": next_due_date = frappe.datetime.add_months(start_date, 12); break;
                    case "Bi-Yearly": next_due_date = frappe.datetime.add_months(start_date, 24); break;
                    case "Tri-Yearly": next_due_date = frappe.datetime.add_months(start_date, 36); break;
                    default: next_due_date = start_date;
                }
            } else {
                next_due_date = frappe.datetime.nowdate();
            }

            row.maintenance_status = "Completed";
            row.next_due_date = next_due_date;
            row.last_completion_date = frappe.datetime.nowdate();
            frm.refresh_field('asset_maintenance_tasks');

        } else {
            if (row.previous_due_date) {
                row.next_due_date = row.previous_due_date;
                row.previous_due_date = null;
            }

            row.maintenance_status = "Pending";
            row.end_date = null;
            row.last_completion_date = null;

            frm.refresh_field('asset_maintenance_tasks');
        }
    },
});