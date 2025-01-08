from datetime import datetime
import frappe

@frappe.whitelist()
def add_hcf(doc, method):
    if doc.get("stock_entry_type") == "Harvesting of Fish":
    
        # hcf, l_warehouse, hcf_item= frappe.db.get_value("HCF Item",{"period": "Oct 2024", "company": doc.get("company")},["hcf", "lake_warehouse_name", "hcf_item"])
        hcf = frappe.db.get_value("HCF Item",{"period": "Oct 2024", "company": doc.get("company")}, "hcf")
        
        # if doc.from_warehouse:
        if doc.items:
            for item in doc.items:
                if item.t_warehouse:
                    doc.append("items",{
                        "item_code": "Feeds in Fish in Water",
                        "s_warehouse": "Lake - VFL",
                        "custom_hcf": hcf,
                        "qty": item.qty*hcf
                    })
        doc.save()
        
def after_insert(doc, method):
    if doc.get("stock_entry_type") == "Harvesting of Fish" and doc.posting_date:
        hcf_recs = frappe.db.get_all(
            "HCF Item", filters = {"company": doc.get("company")}, fields = ["hcf", "lake_warehouse_name", "hcf_item", "start_date", "end_date"]
        )
        posting_date = doc.posting_date
        
        if type(doc.posting_date) == str:
            posting_date = datetime.strptime(doc.posting_date, "%Y-%m-%d")
        
        if hcf_recs:
            for hcf_rec in hcf_recs:
                start_date = convert_time(hcf_rec.get("start_date"))
                end_date = convert_time(hcf_rec.get("end_date"))
                if posting_date >= start_date and posting_date <= end_date:
                    if doc.items:
                        for item in doc.items:
                            if item.t_warehouse:
                                doc.append("items",{
                                    "item_code": hcf_rec.get("hcf_item"),
                                    "s_warehouse": hcf_rec.get("lake_warehouse_name"),
                                    "custom_hcf": hcf_rec.get("hcf"),
                                    "allow_zero_valuation_rate": 1,
                                    "qty": item.qty*hcf_rec.get("hcf")
                                })
                    doc.save()
        
def convert_time(date_time):
    date_str = datetime.strftime(date_time, "%Y-%m-%d")
    r_date = datetime.strptime(date_str, "%Y-%m-%d")
    
    return r_date