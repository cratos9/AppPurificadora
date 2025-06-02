import random
from flask import session 
from src.database.coneccion import db, Rutina, Repartidor, Ruta, Visita, Usuario
from datetime import datetime, timedelta, time

def CrearRutina(usuario_id, dias, hora, cantidad, marcas):
    try:
        cantidad = int(cantidad)  
        repartidores = db.session.query(Repartidor).all()
        repartidor_seleccionado = None
        for r in repartidores:
            if r.cantidad + cantidad <= 20:
                r.cantidad += cantidad
                repartidor_seleccionado = r
                break
        if not repartidor_seleccionado:
            return False

        usuario = db.session.query(Usuario).filter_by(id=usuario_id).first()
        if not usuario:
            return False
        ruta_existe = db.session.query(Ruta).filter_by(zona=usuario.colonia).first()
        if ruta_existe:
            ruta_existe.clientes += 1
        else:
            return False

        rutina = Rutina(
            usuario_id=usuario_id,
            dias=",".join(dias),
            hora=hora if isinstance(hora, time) else datetime.strptime(hora, '%H:%M').time(),
            cantidad=cantidad,
            marca=",".join(marcas),
            repartidor_id=repartidor_seleccionado.id,
            ruta_id=ruta_existe.id
        )
        db.session.add(rutina)
        db.session.commit()  
        
        weekday_mapping = {
            'lunes': 0,
            'martes': 1,
            'miercoles': 2,
            'jueves': 3,
            'viernes': 4,
            'sabado': 5,
            'domingo': 6
        }
        today = datetime.today()
        for dia in dias:
            dia_lower = dia.lower()
            if dia_lower in weekday_mapping:
                target_weekday = weekday_mapping[dia_lower]
                days_ahead = (target_weekday - today.weekday() + 7) % 7
                if days_ahead == 0:
                    days_ahead = 7
                first_date = today + timedelta(days=days_ahead)
                for i in range(cantidad):
                    visit_date = first_date + timedelta(weeks=i)
                    final_datetime = datetime.combine(visit_date.date(), rutina.hora)
                    nueva_visita = Visita(
                        rutina_id=rutina.id,
                        fecha=final_datetime,
                        qr_codigo=str(random.randint(100000, 999999)),
                        verificado=False
                    )
                    db.session.add(nueva_visita)
        db.session.commit()
        return rutina
    except Exception as e:
        print(f"Error al crear rutina: {e}")
        db.session.rollback()
        return False
    
def ModificarRutina(rutina_id, dias=None, hora=None, cantidad=None, marcas=None, repartidor_id=None, ruta_id=None):
    try:
        rutina = db.session.query(Rutina).filter_by(id=rutina_id).first()
        if not rutina:
            return False

        # Actualizar cantidad y ajustar repartidor si fuera necesario
        if cantidad is not None:
            cantidad = int(cantidad)
            if cantidad != rutina.cantidad:
                repartidor = db.session.query(Repartidor).filter_by(id=rutina.repartidor_id).first()
                if repartidor:
                    repartidor.cantidad -= rutina.cantidad
                    repartidor.cantidad += cantidad
                rutina.cantidad = cantidad

        # Actualizar los campos de días y marcas convirtiendo las listas a cadenas
        if dias is not None:
            rutina.dias = ",".join(dias)
        if hora is not None:
            try:
                parsed_time = datetime.strptime(hora, '%H:%M:%S').time()
            except ValueError:
                parsed_time = datetime.strptime(hora, '%H:%M').time()
            rutina.hora = parsed_time
        if marcas is not None:
            rutina.marca = ",".join(marcas)
        if repartidor_id is not None:
            rutina.repartidor_id = repartidor_id

        # Eliminar visitas existentes asociadas a la rutina
        visitas = db.session.query(Visita).filter_by(rutina_id=rutina_id).all()
        for visita in visitas:
            db.session.delete(visita)

        # Generar nuevas visitas basadas en los nuevos datos
        weekday_mapping = {
            'lunes': 0,
            'martes': 1,
            'miercoles': 2,
            'jueves': 3,
            'viernes': 4,
            'sabado': 5,
            'domingo': 6
        }
        today = datetime.today()
        # Usar la cantidad actualizada de la rutina
        nueva_cantidad = rutina.cantidad  
        # Se toma la lista de días desde el parámetro o se reconstruye a partir de la cadena almacenada
        nuevos_dias = dias if dias is not None else rutina.dias.split(",")
        for dia in nuevos_dias:
            dia_lower = dia.lower()
            if dia_lower in weekday_mapping:
                target_weekday = weekday_mapping[dia_lower]
                days_ahead = (target_weekday - today.weekday() + 7) % 7
                if days_ahead == 0:
                    days_ahead = 7
                first_date = today + timedelta(days=days_ahead)
                for i in range(nueva_cantidad):
                    visit_date = first_date + timedelta(weeks=i)
                    final_datetime = datetime.combine(visit_date.date(), rutina.hora)
                    nueva_visita = Visita(
                        rutina_id=rutina.id,
                        fecha=final_datetime,
                        qr_codigo=str(random.randint(100000, 999999)),
                        verificado=False
                    )
                    db.session.add(nueva_visita)
                    
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al modificar rutina: {e}")
        return False
    
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