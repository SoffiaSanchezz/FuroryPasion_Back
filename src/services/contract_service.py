import os
from fpdf import FPDF
from flask import current_app
from datetime import datetime


def _safe(text: str) -> str:
    return str(text).encode('latin-1', 'replace').decode('latin-1')


class ContractService:
    @staticmethod
    def generate_student_contract(student_data, signature_path):

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        W = 170

        # ── HEADER ─────────────────────────────
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(W, 8, _safe("REGLAMENTO PARA PROCESOS DE FORMACION"), ln=True, align='C')
        pdf.cell(W, 8, _safe("FUROR Y PASION ESCUELA DE DANZA"), ln=True, align='C')
        pdf.ln(5)

        # ── FORMULARIO (COMO TU PDF) ───────────
        pdf.set_font("Arial", '', 10)

        pdf.cell(100, 6, _safe("FECHA DE INGRESO: _______________________"))
        pdf.ln(8)

        pdf.set_font("Arial", 'B', 10)
        pdf.cell(W, 6, _safe("DATOS DEL ALUMNO"), ln=True)

        pdf.set_font("Arial", '', 10)

        pdf.cell(90, 6, _safe("NOMBRE: ________________________________"))
        pdf.cell(80, 6, _safe("T.I./C.C.: _______________________"), ln=True)

        pdf.cell(90, 6, _safe("EDAD: ______"))
        pdf.cell(80, 6, _safe("FECHA DE NACIMIENTO: ____________"), ln=True)

        pdf.cell(90, 6, _safe("CEL: ____________________________"))

        pdf.cell(W, 6, _safe("DIRECCION: ______________________________________________"), ln=True)
        pdf.cell(W, 6, _safe("CORREO: ______________________________________________"), ln=True)

        pdf.ln(4)

        # ── ACUDIENTE ──────────────────────────
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(W, 6, _safe("DATOS DEL ACUDIENTE"), ln=True)

        pdf.set_font("Arial", '', 10)

        pdf.cell(90, 6, _safe("NOMBRE: ________________________________"))
        pdf.cell(80, 6, _safe("CEL: _______________________"), ln=True)

        pdf.cell(W, 6, _safe("DIRECCION: ______________________________________________"), ln=True)
        pdf.cell(W, 6, _safe("CORREO: ______________________________________________"), ln=True)

        pdf.ln(5)

        # ── CONTENIDO COMPLETO ─────────────────
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(W, 6, _safe("Aspectos generales:"), ln=True)

        pdf.set_font("Arial", '', 9)

        contenido = [
            "1. La Escuela de Artes Furor y Pasión es una institución de aprendizaje enfocada en la danza profesional, que tiene como función la formación y perfeccionamiento de las capacidades de aspirantes y bailarines. Como institución, nos distinguimos de los grupos de baile principalmente por manejar programas académicos basados en competencias y diferenciación por niveles y edad, lo que le permite a estudiante llegar al conocimiento y la experiencia de baile.",
            "2. Los ensayos se realizarán principalmente en el salón de la Calle 10 N 3a – 42. Adicionalmente si no es posible por causas ajenas o se requiere un espacio diferente. Cualquier cambio de horario o cancelación de ensayo se realizará por vía telefónica o por mensaje a los grupos de WhatsApp de la escuela"
            "3. La inasistencia de clase menor a un mes se contará como falla, mas no como suspensión o aplazamiento del curso. Lo cual mantendrá la misma fecha de pago y se realizará cobro.",
            "4. El pago de la mensualidad se recibirá durante los ensayos el mismo día del mes que inicio clases",
            "5. Las clases perdidas independiente de cuál sea la razón no generan reprogramación o reembolso del dinero."
        ] 

        for c in contenido:
            pdf.multi_cell(W, 5, _safe(c))
            pdf.ln(1)

        # ── COMPROMISOS ───────────────────────
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(W, 6, _safe("COMPROMISO DE LOS ESTUDIANTES Y PADRES"), ln=True)

        pdf.set_font("Arial", '', 9)

        compromisos = [
            "1. Me comprometo a participar de las actividades organizadas por la escuela aparte de las clases del curso.",
            "2. Me comprometo a informar inmediatamente cualquier tipo de restricción médica o terapéutica que me impida realizar total o parcialmente cualquiera de los ejercicios establecidos y a presentar soportes del mismo",
            "3. El proceso es individual.",
            "4. El estudiante mayor de edad es su propio representante",
            "5. En el caso de pertenecer a grupos de competencia, es obligatorio adquirir vestuario, zapatos o utensilios necesarios."
        ]

        for c in compromisos:
            pdf.multi_cell(W, 5, _safe(c))

        # ── SANCIONES ─────────────────────────
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(W, 6, _safe("SANCIONES GRUPOS DE COMPETENCIA"), ln=True)

        pdf.set_font("Arial", '', 9)

        sanciones = [
            "1. El llegar más de 10 minutos tarde al ensayo o sin la ropa adecuada, representa una multa de $4.000 y una rutina de acondicionamiento físico intermedio. Faltar a más de 2 ensayos en un mes acarrea una multa de $30.000 y una rutina de acondicionamiento físico intensa.",
            "2. El no lograr las técnicas o ejercicios establecidos como requerimientos para participar de coreografías, dará como sanción la no participación del estudiante en el espectáculo hasta lograr los requerimientos mínimos.",
            "3. El no cumplir las órdenes del profesor o tener un comportamiento que se considere inadecuado durante las salidas académicas o en competencias, dará como resultado la suspensión de la participación del estudiante o del grupo en el evento.",
            "4. Agredir de forma verbal a un compañero o profesor acarrea la suspensión de 3 clases consecutivas y una multa económica de $30.000. Agredir de forma física a un compañero o profesor acarrea la expulsión permanente de la escuela",
        ]

        for s in sanciones:
            pdf.multi_cell(W, 5, _safe(s))

        pdf.ln(5)

        # ── TEXTO FINAL ───────────────────────
        pdf.set_font("Arial", '', 9)
        pdf.multi_cell(W, 5, _safe(
            "Furor y Pasión Escuela de Danza, encuentra en las redes sociales y medios digitales una gran oportunidad de expansión. Por ende, se realizarán tomas fotográficas y de video, de ensayos, eventos o sesiones, para difundir en las diferentes plataformas institucionales. Y es importante contar la autorización de los estudiantes y acudientes para poder difundir dicho material. Al firmar el presente reglamento reconozco el compromiso y disciplina que se requiere para cumplir el programa planteado, el cual conocí previamente y acepto en totalidad. Confirmo que leí y acepto las normas aquí establecidas, así como doy mi autorización para el manejo de imagen y contenido audiovisual de manera pública como se solicita en este formato."
        ))

        pdf.ln(10)

        # ── FIRMAS ───────────────────────────
        pdf.cell(80, 10, "__________________________________", 0, 0, 'C')
        pdf.cell(10)
        pdf.cell(80, 10, "__________________________________", 0, 1, 'C')

        pdf.cell(80, 6, _safe("Estudiante"), 0, 0, 'C')
        pdf.cell(10)
        pdf.cell(80, 6, _safe("Acudiente"), 0, 1, 'C')

        pdf.ln(5)

        # ── GUARDAR ───────────────────────────
        contracts_dir = os.path.join(current_app.root_path, 'uploads', 'contracts')
        os.makedirs(contracts_dir, exist_ok=True)

        filename = f"contrato_{student_data.document_id}.pdf"
        filepath = os.path.join(contracts_dir, filename)

        pdf.output(filepath)

        return filepath