from fpdf import FPDF
import os
from flask import current_app
from datetime import datetime


def _safe(text: str) -> str:
    return str(text).encode('latin-1', 'replace').decode('latin-1')


class InvoicePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, _safe("FUROR Y PASIÓN ESCUELA DE DANZA"), ln=True, align="C")

        self.set_font("Arial", "", 10)
        self.cell(0, 6, _safe("NIT: 000000000-0 | Calle 10 N 3a – 42"), ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, _safe(f"Página {self.page_no()}"), align="C")


class InvoiceService:

    @staticmethod
    def generate_invoice_pdf(payment, student, installment=None):

        pdf = InvoicePDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # ─── INFO FACTURA ─────────────────
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, _safe("FACTURA DE PAGO"), ln=True, align="C")

        pdf.set_font("Arial", "", 10)
        pdf.cell(100, 6, _safe(f"Factura #: {payment['receiptId']}"))
        pdf.cell(0, 6, _safe(f"Fecha: {datetime.now().strftime('%Y-%m-%d')}"), ln=True)

        pdf.ln(5)

        # ─── CLIENTE ─────────────────────
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "DATOS DEL ESTUDIANTE", ln=True)

        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, _safe(f"Nombre: {student['full_name']}"), ln=True)
        pdf.cell(0, 6, _safe(f"Correo: {student['email']}"), ln=True)

        pdf.ln(5)

        # ─── TABLA ───────────────────────
        pdf.set_font("Arial", "B", 10)

        headers = ["Concepto", "Detalle", "Valor"]
        widths = [50, 80, 40]

        for i in range(len(headers)):
            pdf.cell(widths[i], 8, headers[i], border=1, align="C")
        pdf.ln()

        pdf.set_font("Arial", "", 10)

        rows = [
            ("Plan adquirido", payment['planAcquired'], f"${payment['totalValue']}"),
            ("Total pagado", "", f"${payment['amountPaid']}"),
            ("Saldo pendiente", "", f"${payment['pendingBalance']}"),
            ("Método de pago", payment['paymentMethod'], ""),
            ("Estado", payment['status'], ""),
            ("Vigencia", payment['planStatus'], "")
        ]

        for row in rows:
            for i in range(len(row)):
                pdf.cell(widths[i], 8, _safe(str(row[i])), border=1)
            pdf.ln()

        # ─── ABONO ───────────────────────
        if installment:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 8, "DETALLE DEL ABONO", ln=True)

            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, _safe(f"Monto: ${installment['amount']}"), ln=True)
            pdf.cell(0, 6, _safe(f"Fecha: {installment['date']}"), ln=True)
            pdf.cell(0, 6, _safe(f"Notas: {installment['notes']}"), ln=True)

        # ─── TOTAL DESTACADO ─────────────
        pdf.ln(8)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, _safe(f"TOTAL PAGADO: ${payment['amountPaid']}"), ln=True, align="R")

        # ─── MENSAJE FINAL ───────────────
        pdf.ln(5)
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 5, _safe(
            "Gracias por confiar en Furor y Pasión. Este documento sirve como comprobante de pago."
        ))

        # ─── GUARDAR ─────────────────────
        invoices_dir = os.path.join(current_app.root_path, 'uploads', 'invoices')
        os.makedirs(invoices_dir, exist_ok=True)

        filename = f"factura_{payment['receiptId']}.pdf"
        filepath = os.path.join(invoices_dir, filename)

        pdf.output(filepath)

        return filepath