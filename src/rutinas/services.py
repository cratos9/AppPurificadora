import random
from flask import session 
from src.database.coneccion import db, Rutina, Repartidor, Ruta, Visita, Usuario
from datetime import datetime, timedelta, time

def CrearRutina(usuario_id, dias, hora, cantidad, marcas):
    try:
        cantidad = int(cantidad)  # Conversión a entero para evitar error en la suma
        # Seleccionar repartidor disponible
        repartidores = db.session.query(Repartidor).all()
        repartidor_seleccionado = None
        for r in repartidores:
            if r.cantidad + cantidad <= 20:
                r.cantidad += cantidad
                repartidor_seleccionado = r
                break
        if not repartidor_seleccionado:
            return False

        # Buscar la ruta correspondiente según la zona del usuario
        usuario = db.session.query(Usuario).filter_by(id=usuario_id).first()
        if not usuario:
            return False
        ruta_existe = db.session.query(Ruta).filter_by(zona=usuario.colonia).first()
        if ruta_existe:
            ruta_existe.clientes += 1
        else:
            return False

        # Crear la nueva rutina incluyendo repartidor_id y ruta_id
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
        db.session.commit()  # Necesario para obtener rutina.id

        # Mapeo de días de la semana en español (en minúsculas)
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
        # Para cada día seleccionado, generar visitas pendientes para las próximas "cantidad" semanas
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
    
def ModificarRutina(rutina_id, dias=None, hora=None, cantidad=None, marca=None, repartidor_id=None, ruta_id=None):
    try:
        rutina = db.session.query(Rutina).filter_by(id=rutina_id).first()
        if not rutina:
            return False
        
        if cantidad is not None and cantidad > rutina.cantidad:
            repartidores_disponibles = db.session.query(Repartidor).all()
            antiguo_repartidor = db.session.query(Repartidor).filter_by(id=rutina.repartidor_id).first()
            if antiguo_repartidor:
                antiguo_repartidor.cantidad -= rutina.cantidad
            asignado = False
            for rep in repartidores_disponibles:
                if rep.cantidad + cantidad <= 20:
                    rep.cantidad += cantidad
                    Repartidor.cantidad += cantidad
                    db.session.commit()
                    rutina.cantidad = cantidad
                    asignado = True
                    break
            if not asignado:
                return False
            
        if dias is not None:
            rutina.dias = dias
        if hora is not None:
            rutina.hora = hora
        if cantidad is not None:
            rutina.cantidad = cantidad
        if marca is not None:
            rutina.marca = marca
        if repartidor_id is not None:
            rutina.repartidor_id = repartidor_id
        
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False
    
def EliminarRutina(rutina_id):
    try:
        rutina = db.session.query(Rutina).filter_by(id=rutina_id).first()
        if not rutina:
            return False
        
        db.session.delete(rutina)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False
    
def get_visita_mas_proxima(usuario_id):
    now = datetime.now()
    visita = Visita.query.join(Rutina).filter(
        Visita.fecha >= now,
        Rutina.usuario_id == usuario_id
    ).order_by(Visita.fecha.asc()).first()
    return visita