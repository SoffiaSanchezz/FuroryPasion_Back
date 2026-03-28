import os
from fpdf import FPDF
from flask import current_app
from datetime import datetime

class ContractService:
    @staticmethod
    def generate_student_contract(student_data, signature_path):
        """Genera un archivo PDF con el contrato y la firma del estudiante."""
        pdf = FPDF()
        pdf.add_page()
        
        # --- Header ---
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(177, 18, 38) # Color primario #B11226
        pdf.cell(0, 10, "REGLAMENTO PARA PROCESOS DE FORMACION", ln=True, align='C')
        pdf.cell(0, 10, "FUROR Y PASION ESCUELA DE DANZA", ln=True, align='C')
        pdf.ln(10)
        
        # --- Student Info ---
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"Datos del Estudiante:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 7, f"Nombre Completo: {student_data.full_name}", ln=True)
        pdf.cell(0, 7, f"Documento: {student_data.document_id}", ln=True)
        pdf.cell(0, 7, f"Fecha de Afiliacion: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
        pdf.ln(5)
        
        # --- Content (Simplified from frontend) ---
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Aspectos generales:", ln=True)
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
            "- Agredir verbalmente: suspension de 3 clases. Agresion fisica: expulsion permanente."
        ]
        
        for line in content:
            pdf.multi_cell(0, 6, line.encode('latin-1', 'replace').decode('latin-1'))
            
        pdf.ln(10)
        
        # --- Signature ---
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Firma del Estudiante/Acudiente:", ln=True)
        
        if signature_path:
            # La ruta guardada no incluye 'uploads', debemos añadirla para acceder al archivo
            full_sig_path = os.path.join(current_app.root_path, 'uploads', signature_path)
            if os.path.exists(full_sig_path):
                # Dibujar imagen de la firma (ajustar coordenadas y tamaño)
                pdf.image(full_sig_path, x=20, w=50) 
            else:
                pdf.cell(0, 10, "(Firma registrada en el sistema)", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 8)
        pdf.multi_cell(0, 5, "Al firmar, reconozco el compromiso y disciplina requeridos. Autorizo el manejo de mi imagen y contenido audiovisual para fines institucionales y publicitarios.")
        
        # Guardar el PDF temporalmente o en una carpeta de contratos
        contracts_dir = os.path.join(current_app.root_path, 'uploads', 'contracts')
        os.makedirs(contracts_dir, exist_ok=True)
        
        filename = f"contrato_{student_data.document_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(contracts_dir, filename)
        
        pdf.output(filepath)
        return filepath
