import { registry } from "@web/core/registry";
import { loadBundle } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, useRef, onWillStart, useEffect } from "@odoo/owl";

const CHART_COLORS = ["#714B67", "#00A09D", "#F1C232", "#DC6E6E", "#6B8E23", "#4A6FA5"];

export class InventoryManagementDashboard extends Component {
    static template = "inventory_management.Dashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.state = useState({ data: null });
        this.categoryCanvasRef = useRef("categoryChart");
        this.roleCanvasRef = useRef("roleChart");
        this.categoryChart = null;
        this.roleChart = null;

        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            this.state.data = await this.orm.call("im.dashboard", "get_dashboard_data", []);
        });

        useEffect(() => {
            if (this.state.data) {
                this.renderCharts();
            }
        });
    }

    renderCharts() {
        this.renderPieChart(this.categoryCanvasRef, this.categoryChart, this.state.data.product_by_category);
        this.renderPieChart(this.roleCanvasRef, this.roleChart, this.state.data.partner_by_role);
    }

    renderPieChart(canvasRef, existingChart, breakdown) {
        if (!canvasRef.el) {
            return;
        }
        if (existingChart) {
            existingChart.destroy();
        }
        const chart = new Chart(canvasRef.el, {
            type: "pie",
            data: {
                labels: breakdown.map((entry) => entry.label),
                datasets: [
                    {
                        data: breakdown.map((entry) => entry.value),
                        backgroundColor: breakdown.map(
                            (_, index) => CHART_COLORS[index % CHART_COLORS.length]
                        ),
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            },
        });
        if (canvasRef === this.categoryCanvasRef) {
            this.categoryChart = chart;
        } else {
            this.roleChart = chart;
        }
    }
}

registry.category("actions").add("inventory_management.dashboard", InventoryManagementDashboard);
