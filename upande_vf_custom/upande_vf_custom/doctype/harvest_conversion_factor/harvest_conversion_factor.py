# Copyright (c) 2024, Upande Ltd and contributors
# For license information, please see license.txt
from datetime import datetime, timedelta

import frappe
from frappe.model.document import Document


class HarvestConversionFactor(Document):
    @frappe.whitelist()
    def get_end_date(self):
        date = self.start_of_the_year
        
        end_date = frappe.utils.add_to_date(date, years=0, months=12, weeks=0, days=0, hours=0, minutes=0, seconds=0, as_string=True, as_datetime=False)
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        year_end_date = end_datetime - timedelta(days=1)

        frappe.response['message'] = year_end_date
        
    # def get_months_for_hcf(self):
    #     start_date = self.start_of_the_year
    #     end_date = self.end_of_the_year
        
    #     if start_date and end_date:
    #         months_btwn = 