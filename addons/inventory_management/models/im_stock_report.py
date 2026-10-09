from odoo import models


class ReportImStockReport(models.AbstractModel):
    _name = "report.inventory_management.report_im_stock_report_document"
    _description = "Stock Report"

    def _get_report_values(self, docids, data=None):
        warehouses = self.env["im.warehouse"].browse(docids)
        report_data = {
            warehouse.id: warehouse.get_stock_report_lines() for warehouse in warehouses
        }
        return {
            "doc_ids": docids,
            "doc_model": "im.warehouse",
            "docs": warehouses,
            "report_data": report_data,
        }
