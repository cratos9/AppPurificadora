from datetime import datetime, timedelta, time
import uuid
from src.database.coneccion import db, Usuario, Rutina, Repartidor, Ruta, Visita, AsignacionRepartidor

def generate_unique_qr():
    """Genera un código QR corto de 6 caracteres, asegurándose de que no exista ya en la base de datos."""
    while True:
        code = uuid.uuid4().hex[:6].upper()
        if not db.session.query(Visita).filter_by(qr_codigo=code).first():
            return code

def CrearRutina(usuario_id, dias, hora, cantidad, marcas):
    try:
        cantidad = int(cantidad)
        
        usuario = db.session.query(Usuario).filter_by(id=usuario_id).first()
        if not usuario:
            return {"error": "Usuario no encontrado"}
            
        ruta = db.session.query(Ruta).filter_by(zona=usuario.colonia).first()
        if not ruta:
            return {"error": "No se encontró ruta para la colonia del usuario"}
        
        weekday_mapping = {
            "lunes": 0,
            "martes": 1,
            "miercoles": 2,
            "jueves": 3,
            "viernes": 4,
            "sabado": 5,
            "domingo": 6
        }
        
        def get_first_future_date(weekday_number):
            now_dt = datetime.now()
            days_ahead = (weekday_number - now_dt.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7
            return (now_dt + timedelta(days=days_ahead)).date()
        
        repartidor_seleccionado = None
        repartidores = db.session.query(Repartidor).all()
        for r in repartidores:
            disponible = True
            for dia in dias:
                dia_lower = dia.lower()
                if dia_lower not in weekday_mapping:
                    continue
                target_date = get_first_future_date( weekday_mapping[dia_lower] )
                asignacion = db.session.query(AsignacionRepartidor).filter_by(
                    repartidor_id=r.id,
                    fecha=target_date
                ).first()
                current_assigned = asignacion.total_asignado if asignacion else 0
                if current_assigned + cantidad > r.capacidad_maxima:
                    disponible = False
                    break
            if disponible:
                repartidor_seleccionado = r
                break
                
        if not repartidor_seleccionado:
            return {"error": "No hay repartidores disponibles con capacidad suficiente"}
        
        if not isinstance(hora, time):
            hora_obj = datetime.strptime(hora, "%H:%M").time()
        else:
            hora_obj = hora
            
        rutina = Rutina(
            usuario_id=usuario_id,
            dias=",".join(dias),
            hora=hora_obj,
            cantidad=cantidad,
            marca=",".join(marcas),
            ruta_id=ruta.id,
            repartidor_id=repartidor_seleccionado.id
        )
        db.session.add(rutina)
        db.session.commit()
        
        for dia in dias:
            dia_lower = dia.lower()
            if dia_lower not in weekday_mapping:
                continue
            target_date = get_first_future_date( weekday_mapping[dia_lower] )
            visita_fecha = datetime.combine(target_date, rutina.hora)
            nueva_visita = Visita(
                rutina_id=rutina.id,
                fecha=visita_fecha,
                qr_codigo=generate_unique_qr(),
                verificado=False
            )
            db.session.add(nueva_visita)
            
            asignacion = db.session.query(AsignacionRepartidor).filter_by(
                repartidor_id=repartidor_seleccionado.id,
                fecha=target_date
            ).first()
            if asignacion:
                asignacion.total_asignado += cantidad
            else:
                nueva_asignacion = AsignacionRepartidor(
                    repartidor_id=repartidor_seleccionado.id,
                    fecha=target_date,
                    total_asignado=cantidad
                )
                db.session.add(nueva_asignacion)
        
        db.session.commit()
        return rutina
        
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}
    
def ModificarRutina(rutina_id, dias=None, hora=None, cantidad=None, marcas=None, repartidor_id=None, ruta_id=None):
    try:
        rutina = db.session.query(Rutina).filter_by(id=rutina_id).first()
        if not rutina:
            return {"error": "Rutina no encontrada"}
        
        weekday_mapping = {
            "lunes": 0,
            "martes": 1,
            "miercoles": 2,
            "jueves": 3,
            "viernes": 4,
            "sabado": 5,
            "domingo": 6
        }
        def get_first_future_date(weekday_number):
            now_dt = datetime.now()
            days_ahead = (weekday_number - now_dt.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7
            return (now_dt + timedelta(days=days_ahead)).date()
        
        old_dias = rutina.dias.split(",")  if rutina.dias else []
        old_cantidad = rutina.cantidad
        
        if cantidad is not None:
            cantidad = int(cantidad)
        
        if dias is not None:
            rutina.dias = ",".join(dias)
        if hora is not None:
            if not isinstance(hora, time):
                try:
                    rutina.hora = datetime.strptime(hora, "%H:%M:%S").time()
                except ValueError:
                    rutina.hora = datetime.strptime(hora, "%H:%M").time()
            else:
                rutina.hora = hora
        if cantidad is not None:
            rutina.cantidad = cantidad
        if marcas is not None:
            rutina.marca = ",".join(marcas)
        if repartidor_id is not None:
            rutina.repartidor_id = repartidor_id
        if ruta_id is not None:
            rutina.ruta_id = ruta_id
        
        visitas_previas = db.session.query(Visita).filter_by(rutina_id=rutina.id).all()
        for visita in visitas_previas:
            db.session.delete(visita)
            
        repartidor_asignado = rutina.repartidor_id
        for dia in old_dias:
            dia_lower = dia.lower().strip()
            if dia_lower not in weekday_mapping:
                continue
            target_date = get_first_future_date( weekday_mapping[dia_lower] )
            asignacion_old = db.session.query(AsignacionRepartidor).filter_by(
                repartidor_id=repartidor_asignado,
                fecha=target_date
            ).first()
            if asignacion_old:
                asignacion_old.total_asignado -= old_cantidad
                if asignacion_old.total_asignado < 0:
                    asignacion_old.total_asignado = 0
        
        nuevos_dias = dias if dias is not None else old_dias
        
        for dia in nuevos_dias:
            dia_lower = dia.lower().strip()
            if dia_lower not in weekday_mapping:
                continue
            target_date = get_first_future_date( weekday_mapping[dia_lower] )
            visita_fecha = datetime.combine(target_date, rutina.hora)
            nueva_visita = Visita(
                rutina_id=rutina.id,
                fecha=visita_fecha,
                qr_codigo=generate_unique_qr(),
                verificado=False
            )
            db.session.add(nueva_visita)
            
            asignacion = db.session.query(AsignacionRepartidor).filter_by(
                repartidor_id=rutina.repartidor_id,
                fecha=target_date
            ).first()
            aporte = cantidad if cantidad is not None else old_cantidad
            if asignacion:
                asignacion.total_asignado += aporte
            else:
                nueva_asignacion = AsignacionRepartidor(
                    repartidor_id=rutina.repartidor_id,
                    fecha=target_date,
                    total_asignado=aporte
                )
                db.session.add(nueva_asignacion)
        
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error al modificar rutina: {e}")
        return {"error": str(e)}
    
def EliminarRutina(rutina_id):
    try:
        rutina = db.session.query(Rutina).filter_by(id=rutina_id).first()
        if not rutina:
            return False
        
        visitas = db.session.query(Visita).filter_by(rutina_id=rutina_id).all()
        for visita in visitas:
            db.session.delete(visita)
        
        db.session.delete(rutina)
        db.session.commit()
        print("Cambios guardados en la base de datos.")
        return True
    except Exception as e:
        print(f"Error al eliminar la rutina: {e}")
        db.session.rollback()
        return False
    
def get_visita_mas_proxima(usuario_id):
    now = datetime.now()
    visitas = Visita.query.join(Rutina).filter(
        Visita.fecha >= now,
        Rutina.usuario_id == usuario_id
    ).order_by(Visita.fecha.asc()).all()
    return visitas