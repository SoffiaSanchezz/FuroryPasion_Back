import os
from fpdf import FPDF
from flask import current_app
from datetime import datetime


def _safe(text) -> str:
    return str(text).encode('latin-1', 'replace').decode('latin-1')


class PaymentReceiptService:

    @staticmethod
    def generate_receipt(payment, installment=None) -> str:
        """
        Genera un PDF de recibo de pago y retorna la ruta del archivo.
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        W = 170

        # ── ENCABEZADO ─────────────────────────────────────────────────
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(W, 8, _safe("FUROR Y PASION ESCUELA DE DANZA"), ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        pdf.cell(W, 6, _safe("Calle 10 N 3a - 42"), ln=True, align='C')
        pdf.ln(4)

        pdf.set_font("Arial", 'B', 13)
        pdf.cell(W, 8, _safe("RECIBO DE PAGO"), ln=True, align='C')
        pdf.ln(6)

        # ── DATOS DEL ESTUDIANTE ────────────────────────────────────────
        student = payment.student
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(W, 6, _safe("DATOS DEL ESTUDIANTE"), ln=True)
        pdf.set_font("Arial", '', 10)

        pdf.cell(90, 6, _safe(f"Nombre: {student.full_name}"))
        pdf.cell(80, 6, _safe(f"Documento: {student.document_id}"), ln=True)

        if student.email:
            pdf.cell(W, 6, _safe(f"Correo: {student.email}"), ln=True)
        if student.phone:
            pdf.cell(W, 6, _safe(f"Telefono: {student.phone}"), ln=True)

        pdf.ln(5)

        # ── DETALLE DEL PAGO ────────────────────────────────────────────
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(W, 6, _safe("DETALLE DEL PAGO"), ln=True)

        # Línea separadora
        pdf.set_draw_color(177, 18, 38)
        pdf.set_line_width(0.5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

        pdf.set_font("Arial", '', 10)

        serialized = payment.serialize()

        rows = [
            ("No. Recibo",       serialized['receiptId']),
            ("Plan adquirido",   serialized['planAcquired']),
            ("Metodo de pago",   serialized['paymentMethod']),
            ("Valor total",      f"${serialized['totalValue']:,.0f}"),
            ("Total pagado",     f"${serialized['amountPaid']:,.0f}"),
            ("Saldo pendiente",  f"${serialized['pendingBalance']:,.0f}"),
            ("Estado del pago",  serialized['status']),
            ("Vigencia del plan",serialized['planStatus']),
            ("Fecha inicio",     serialized['startDate']),
            ("Fecha fin",        serialized['endDate']),
            ("Fecha de registro",datetime.utcnow().strftime("%Y-%m-%d %H:%M")),
        ]

        for label, value in rows:
            pdf.cell(80, 7, _safe(f"{label}:"), border='B')
            pdf.cell(90, 7, _safe(str(value)), border='B', ln=True)

        pdf.ln(5)

        # ── DETALLE DEL ABONO (si aplica) ───────────────────────────────
        if installment:
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(W, 6, _safe("ABONO REGISTRADO"), ln=True)
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)

            pdf.set_font("Arial", '', 10)
            inst_rows = [
                ("Monto del abono", f"${installment.amount:,.0f}"),
                ("Metodo",          installment.payment_method),
                ("Fecha",           installment.date.strftime("%Y-%m-%d %H:%M")),
                ("Notas",           installment.notes or "-"),
            ]
            for label, value in inst_rows:
                pdf.cell(80, 7, _safe(f"{label}:"), border='B')
                pdf.cell(90, 7, _safe(str(value)), border='B', ln=True)

            pdf.ln(5)

        # ── TOTAL DESTACADO ─────────────────────────────────────────────
        pdf.set_fill_color(177, 18, 38)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(W, 10, _safe(f"  TOTAL PAGADO: ${serialized['amountPaid']:,.0f}"), ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)

        pdf.ln(10)

        # ── PIE ─────────────────────────────────────────────────────────
        pdf.set_font("Arial", 'I', 9)
        pdf.cell(W, 5, _safe("Gracias por confiar en nosotros. Este documento es su comprobante de pago."), ln=True, align='C')

        # ── GUARDAR ─────────────────────────────────────────────────────
        receipts_dir = os.path.join(current_app.root_path, 'uploads', 'receipts')
        os.makedirs(receipts_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"recibo_{payment.receipt_id}_{timestamp}.pdf"
        filepath = os.path.join(receipts_dir, filename)

        pdf.output(filepath)
        return filepath
