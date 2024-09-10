frappe.ui.form.on('Project', {
    refresh: function(frm) {
        // Add or remove the button based on project type
        manage_create_asset_button(frm);
        // Calculate and set total project cost when the form is refreshed
        calculate_and_set_custom_total_project_cost(frm);
    },
    project_type: function(frm) {
        // Add or remove the button based on project type change
        manage_create_asset_button(frm);
        // Recalculate project cost when the project type changes
        calculate_and_set_custom_total_project_cost(frm);
    }
});

function manage_create_asset_button(frm) {
    // Check if the project type is "Capital Work in Progress"
    if (frm.doc.project_type === "Capital Work in Progress") {
        // Ensure the button is added only once
        if (!frm.custom_buttons || !frm.custom_buttons['Create Asset']) {
            frm.page.set_primary_action(__('Create Asset'), function() {
                if (frm.doc.status !== "Completed") {
                    frappe.msgprint(__('The project must be marked as completed before creating an asset.'));
                    return;
                }
                frappe.confirm(
                    'Are you sure you want to create an asset?',
                    function() {
                        frappe.prompt([
                            {
                                'label': 'Item Code',
                                'fieldname': 'item_code',
                                'fieldtype': 'Link',
                                'options': 'Item',
                                'reqd': 1,
                                'description': 'Select an existing Item Code or create a new one.',
                                'filters': {
                                    'item_group': 'Fixed Assets' // Filter for fixed assets only
                                }
                            },
                            {
                                'label': 'Location',
                                'fieldname': 'location',
                                'fieldtype': 'Link',
                                'options': 'Location',
                                'reqd': 1,
                                'description': 'Select an existing Location or create a new one.'
                            }
                        ],
                        function(values) {
                            // Fetch the total project cost
                            let gross_purchase_amount = frm.doc.custom_total_project_cost || 0;

                            console.log('Gross Purchase Amount:', gross_purchase_amount);
                            // Check if gross_purchase_amount is valid
                            if (gross_purchase_amount <= 0) {
                                frappe.msgprint(__('Total Project Cost cannot be zero. Please ensure there are valid expenses linked to the project.'));
                                return;
                            }

                            // Check if asset already exists
                            frappe.call({
                                method: "frappe.client.get_list",
                                args: {
                                    doctype: "Asset",
                                    filters: {
                                        "asset_name": frm.doc.project_name,
                                        "item_code": values.item_code,
                                        "company": frm.doc.company
                                    },
                                    fields: ["name"]
                                },
                                callback: function(response) {
                                    if (response.message && response.message.length > 0) {
                                        frappe.msgprint(__('An asset already exists.'));
                                    } else {
                                        // Create Asset
                                        frappe.call({
                                            method: "frappe.client.insert",
                                            args: {
                                                doc: {
                                                    "doctype": "Asset",
                                                    "item_code": values.item_code,
                                                    "asset_name": frm.doc.project_name,
                                                    "purchase_date": frm.doc.expected_end_date || frappe.datetime.get_today(),
                                                    "gross_purchase_amount": gross_purchase_amount,
                                                    "custom_project_": frm.doc.name,
                                                    "cost_center": frm.doc.cost_center,
                                                    "company": frm.doc.company,
                                                    "is_existing_asset": 1,
                                                    "location": values.location
                                                }
                                            },
                                            callback: function(response) {
                                                if (response.message) {
                                                    let created_asset_name = response.message.name;  // Capture the asset name
                                                    frappe.msgprint(__('Asset {0} created successfully.', [created_asset_name]));

                                                    // Create journal entry (in draft form)
                                                    frappe.call({
                                                        method: "frappe.client.insert",
                                                        args: {
                                                            doc: {
                                                                "doctype": "Journal Entry",
                                                                "posting_date": frappe.datetime.get_today(),
                                                                "company": frm.doc.company,
                                                                "accounts": [
                                                                    {
                                                                        "account": "CWIP Account - VF",  // Replace with your CWIP account
                                                                        "credit_in_account_currency": gross_purchase_amount
                                                                    },
                                                                    {
                                                                        "account": "Buildings - VF",  // Replace with your Asset account
                                                                        "debit_in_account_currency": gross_purchase_amount,
                                                                        "reference_type": "Asset",
                                                                        "reference_name": created_asset_name,
                                                                        "project": frm.doc.name
                                                                    }
                                                                ],
                                                                "project": frm.doc.name
                                                            }
                                                        },
                                                        callback: function(response) {
                                                            console.log('Journal Entry Callback Executed');
                                                            if (response.message) {
                                                                console.log('Journal Entry Created:', response.message.name);
                                                                frappe.msgprint(__('Journal Entry {0} created successfully.', [response.message.name]));
                                                            } else {
                                                                console.log('Journal Entry Creation Failed');
                                                                frappe.msgprint(__('An error occurred while creating the Journal Entry.'));
                                                            }
                                                        }
                                                    });
                                                }
                                            }
                                        });
                                    }
                                }
                            });
                        },
                        'Select Item Code and Location',
                        'Create');
                    }
                );
            }).addClass('btn-primary');
        }
    } else {
        // Remove the button if project type is not CWIP
        if (frm.custom_buttons && frm.custom_buttons['Create Asset']) {
            frm.page.remove_action('Create Asset');
        }
    }
}

function calculate_and_set_custom_total_project_cost(frm) {
    if (frm.doc.project_type === "Capital Work in Progress") {
        // Fetch individual GL entries for the CWIP account and project
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "GL Entry",
                filters: {
                    project: frm.doc.name,
                    account: "CWIP Account - VF"  // Replace with your CWIP account
                },
                fields: ["debit_in_account_currency", "credit_in_account_currency"]
            },
            callback: function(response) {
                if (response.message) {
                    console.log(response.message);
                    let custom_total_project_cost = 0;
                    let acc_bal = response.message;
                    console.log(acc_bal);
                    
                    acc_bal.forEach(entry => {
                        console.log(entry);
                        custom_total_project_cost += (entry.debit_in_account_currency || 0) - (entry.credit_in_account_currency || 0);
                    });
                    
                    console.log('Total Project Cost:', custom_total_project_cost); // Debugging line
                    
                    frm.set_value('custom_total_project_cost', custom_total_project_cost);
                } else {
                    frm.set_value('custom_total_project_cost', 0);
                }
            }
        });
    }
}
