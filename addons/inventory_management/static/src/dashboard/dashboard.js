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
        this.movesCanvasRef = useRef("movesChart");
        this.categoryChart = null;
        this.roleChart = null;
        this.movesChart = null;

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

    get formattedStockValue() {
        return this.state.data.stock_value.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }

    renderCharts() {
        this.renderPieChart(this.categoryCanvasRef, this.categoryChart, this.state.data.product_by_category);
        this.renderPieChart(this.roleCanvasRef, this.roleChart, this.state.data.partner_by_role);
        this.renderMovesChart();
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

    renderMovesChart() {
        if (!this.movesCanvasRef.el) {
            return;
        }
        if (this.movesChart) {
            this.movesChart.destroy();
        }
        const breakdown = this.state.data.recent_moves;
        this.movesChart = new Chart(this.movesCanvasRef.el, {
            type: "bar",
            data: {
                labels: ["Receipts", "Deliveries", "Adjustments", "Transfers"],
                datasets: [
                    {
                        data: [
                            breakdown.receipts,
                            breakdown.deliveries,
                            breakdown.adjustments,
                            breakdown.transfers,
                        ],
                        backgroundColor: CHART_COLORS,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
            },
        });
    }
}

registry.category("actions").add("inventory_management.dashboard", InventoryManagementDashboard);
