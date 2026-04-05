from flask import jsonify, request, g
from src.models.Student import Student
from src.models.Payment import Payment
from src.models.Activity import Activity


class SearchController:

    @staticmethod
    def search():
        user_id = g.current_user_id
        q = (request.args.get('q') or '').strip()

        if not q or len(q) < 2:
            return jsonify({"students": [], "payments": [], "activities": []}), 200

        like = f"%{q}%"

        # Estudiantes: busca por nombre, documento o email
        students = Student.query.filter(
            Student.user_id == user_id,
            (Student.full_name.ilike(like)) |
            (Student.document_id.ilike(like)) |
            (Student.email.ilike(like))
        ).limit(8).all()

        # Pagos: busca por recibo o nombre del estudiante asociado
        payments = (
            Payment.query
            .join(Student, Payment.student_id == Student.id)
            .filter(
                Payment.user_id == user_id,
                (Payment.receipt_id.ilike(like)) |
                (Payment.plan_acquired.ilike(like)) |
                (Student.full_name.ilike(like))
            )
            .limit(8)
            .all()
        )

        # Actividades: busca por título o descripción
        activities = Activity.query.filter(
            Activity.user_id == user_id,
            (Activity.title.ilike(like)) |
            (Activity.description.ilike(like))
        ).limit(8).all()

        return jsonify({
            "students": [
                {
                    "id": str(s.id),
                    "full_name": s.full_name,
                    "document_id": s.document_id,
                    "status": s.status
                }
                for s in students
            ],
            "payments": [
                {
                    "id": str(p.id),
                    "studentName": p.student.full_name if p.student else "",
                    "receiptId": p.receipt_id,
                    "planAcquired": p.plan_acquired,
                    "amountPaid": p.amount_paid
                }
                for p in payments
            ],
            "activities": [a.serialize() for a in activities]
        }), 200
