import os
from fpdf import FPDF
from flask import current_app
from datetime import datetime


def _safe(text: str) -> str:
    """Convierte texto a latin-1 de forma segura para fpdf v1."""
    return str(text).encode('latin-1', 'replace').decode('latin-1')


class ContractService:
    @staticmethod
    def generate_student_contract(student_data, signature_path):
        """Genera un PDF con el contrato de afiliación del estudiante."""
        LEFT_MARGIN = 20
        RIGHT_MARGIN = 20
        TOP_MARGIN = 20

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_margins(LEFT_MARGIN, TOP_MARGIN, RIGHT_MARGIN)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Ancho efectivo: 210mm (A4) - márgenes
        W = pdf.w - LEFT_MARGIN - RIGHT_MARGIN  # ~170mm

        # ── Header ───────────────────────────────────────────────────────
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(177, 18, 38)
        pdf.cell(W, 10, _safe("REGLAMENTO PARA PROCESOS DE FORMACION"), ln=True, align='C')
        pdf.cell(W, 10, _safe("FUROR Y PASION ESCUELA DE DANZA"), ln=True, align='C')
        pdf.ln(8)

        # ── Datos del estudiante ──────────────────────────────────────────
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(W, 8, _safe("Datos del Estudiante:"), ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(W, 7, _safe(f"Nombre Completo: {student_data.full_name}"), ln=True)
        pdf.cell(W, 7, _safe(f"Documento: {student_data.document_id}"), ln=True)
        pdf.cell(W, 7, _safe(f"Fecha de Afiliacion: {datetime.now().strftime('%Y-%m-%d')}"), ln=True)
        pdf.ln(6)

        # ── Contenido ────────────────────────────────────────────────────
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(W, 8, _safe("Aspectos Generales:"), ln=True)
        pdf.set_font("Arial", '', 10)

        content = [
            "1. La Escuela de Artes Furor y Pasion es una institucion de aprendizaje enfocada en la danza profesional.",
            "2. Los ensayos se realizaran principalmente en el salon de la Calle 10 N 3a - 42.",
            "3. La inasistencia de clase menor a un mes se contara como falla, mas no como suspension.",
            "4. El pago de la mensualidad se recibira el mismo dia del mes que inicio clases.",
            "5. Las clases perdidas no generan reprogramacion o reembolso del dinero.",
            "",
            "Compromiso de los Estudiantes y Padres de Familia:",
            "- Me comprometo a participar de las actividades organizadas por la escuela.",
            "- Informar inmediatamente cualquier tipo de restriccion medica o terapeutica.",
            "- El compromiso con el proceso es de manera individual.",
            "",
            "Sanciones:",
            "- Llegar mas de 10 min tarde o sin ropa adecuada: multa de $4.000.",
            "- Faltar a mas de 2 ensayos: multa de $30.000.",
            "- Agredir verbalmente: suspension de 3 clases. Agresion fisica: expulsion permanente.",
        ]

        for line in content:
            if line == "":
                pdf.ln(3)
            else:
                pdf.multi_cell(W, 6, _safe(line))

        pdf.ln(8)

        # ── Firma ─────────────────────────────────────────────────────────
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(W, 8, _safe("Firma del Estudiante / Acudiente:"), ln=True)

        if signature_path:
            full_sig_path = os.path.join(current_app.root_path, 'uploads', signature_path)
            if os.path.exists(full_sig_path):
                pdf.image(full_sig_path, x=LEFT_MARGIN, w=50)
            else:
                pdf.set_font("Arial", 'I', 10)
                pdf.cell(W, 7, _safe("(Firma registrada en el sistema)"), ln=True)
        else:
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(W, 7, _safe("(Sin firma registrada)"), ln=True)

        pdf.ln(8)
        pdf.set_font("Arial", 'I', 8)
        pdf.multi_cell(W, 5, _safe(
            "Al firmar, reconozco el compromiso y disciplina requeridos. "
            "Autorizo el manejo de mi imagen y contenido audiovisual para fines institucionales y publicitarios."
        ))

        # ── Guardar ───────────────────────────────────────────────────────
        contracts_dir = os.path.join(current_app.root_path, 'uploads', 'contracts')
        os.makedirs(contracts_dir, exist_ok=True)

        filename = f"contrato_{student_data.document_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(contracts_dir, filename)
        pdf.output(filepath)

        return filepath
