from datetime import datetime, timedelta, time
import uuid
from src.database.coneccion import db, Usuario, Rutina, Repartidor, Ruta, Visita, AsignacionRepartidor

def generar_codigo_qr_unico():
    while True:
        codigo = uuid.uuid4().hex[:6].upper()
        existe = db.session.query(Visita).filter_by(qr_codigo=codigo).first()
        if not existe:
            return codigo

def CrearRutina(usuario_id, dias, hora_programada, cantidad, marcas):
    try:
        cantidad = int(cantidad)
        usuario = db.session.query(Usuario).get(usuario_id)
        if not usuario:
            return {"error": "Usuario no encontrado"}

        ruta = db.session.query(Ruta).filter_by(zona=usuario.calle).first()
        if not ruta:
            return {"error": "No hay ruta para la colonia del usuario"}

        mapeo_dias = {
            "lunes": 0, "martes": 1, "miércoles": 2,
            "jueves": 3, "viernes": 4,
            "sábado": 5, "domingo": 6
        }

        def primera_fecha_futura(nro_dia_semana):
            hoy = datetime.now()
            dias_adelanto = (nro_dia_semana - hoy.weekday() + 7) % 7
            if dias_adelanto == 0:
                dias_adelanto = 7
            return (hoy + timedelta(days=dias_adelanto)).date()

        repartidor_seleccionado = None
        for r in db.session.query(Repartidor).all():
            disponible = True
            for d in dias:
                dl = d.lower()
                if dl not in mapeo_dias:
                    continue
                fecha_obj = primera_fecha_futura(mapeo_dias[dl])
                asign = db.session.query(AsignacionRepartidor).filter_by(
                    repartidor_id=r.id,
                    fecha=fecha_obj
                ).first()
                asignado = asign.total_asignado if asign else 0
                if asignado + cantidad > r.capacidad_maxima:
                    disponible = False
                    break
            if disponible:
                repartidor_seleccionado = r
                break

        if not repartidor_seleccionado:
            return {"error": "No hay repartidores disponibles"}

        if not isinstance(hora_programada, time):
            hora_obj = datetime.strptime(hora_programada, "%H:%M").time()
        else:
            hora_obj = hora_programada

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

        for d in dias:
            dl = d.lower()
            if dl not in mapeo_dias:
                continue
            fecha_obj = primera_fecha_futura(mapeo_dias[dl])
            fecha_visita = datetime.combine(fecha_obj, rutina.hora)
            visita = Visita(
                rutina_id=rutina.id,
                fecha=fecha_visita,
                qr_codigo=generar_codigo_qr_unico(),
                verificado=False
            )
            db.session.add(visita)

            asign = db.session.query(AsignacionRepartidor).filter_by(
                repartidor_id=repartidor_seleccionado.id,
                fecha=fecha_obj
            ).first()
            if asign:
                asign.total_asignado += cantidad
            else:
                nueva_asig = AsignacionRepartidor(
                    repartidor_id=repartidor_seleccionado.id,
                    fecha=fecha_obj,
                    total_asignado=cantidad
                )
                db.session.add(nueva_asig)

        db.session.commit()
        return rutina

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

def ModificarRutina(rutina_id, dias=None, hora_programada=None, cantidad=None, marcas=None, repartidor_id=None, ruta_id=None):
    try:
        rutina = db.session.query(Rutina).get(rutina_id)
        if not rutina:
            return {"error": "Rutina no encontrada"}

        mapeo_dias = {
            "lunes": 0, "martes": 1, "miércoles": 2,
            "jueves": 3, "viernes": 4,
            "sábado": 5, "domingo": 6
        }
        def primera_fecha_futura(nro_dia_semana):
            hoy = datetime.now()
            dias_adelanto = (nro_dia_semana - hoy.weekday() + 7) % 7
            if dias_adelanto == 0:
                dias_adelanto = 7
            return (hoy + timedelta(days=dias_adelanto)).date()

        dias_previos = rutina.dias.split(",") if rutina.dias else []
        cantidad_prev = rutina.cantidad

        if cantidad is not None:
            rutina.cantidad = int(cantidad)
        if dias is not None:
            rutina.dias = ",".join(dias)
        if hora_programada is not None:
            if not isinstance(hora_programada, time):
                try:
                    rutina.hora = datetime.strptime(hora_programada, "%H:%M:%S").time()
                except ValueError:
                    rutina.hora = datetime.strptime(hora_programada, "%H:%M").time()
            else:
                rutina.hora = hora_programada
        if marcas is not None:
            rutina.marca = ",".join(marcas)
        if repartidor_id is not None:
            rutina.repartidor_id = repartidor_id
        if ruta_id is not None:
            rutina.ruta_id = ruta_id

        visitas_anteriores = db.session.query(Visita).filter_by(rutina_id=rutina.id).all()
        for v in visitas_anteriores:
            db.session.delete(v)

        for d in dias_previos:
            dl = d.lower().strip()
            if dl not in mapeo_dias:
                continue
            fecha_obj = primera_fecha_futura(mapeo_dias[dl])
            asign_old = db.session.query(AsignacionRepartidor).filter_by(
                repartidor_id=rutina.repartidor_id,
                fecha=fecha_obj
            ).first()
            if asign_old:
                asign_old.total_asignado = max(0, asign_old.total_asignado - cantidad_prev)

        dias_nuevos = dias if dias is not None else dias_previos
        cantidad_nueva = int(cantidad) if cantidad is not None else cantidad_prev

        for d in dias_nuevos:
            dl = d.lower().strip()
            if dl not in mapeo_dias:
                continue
            fecha_obj = primera_fecha_futura(mapeo_dias[dl])
            fecha_visita = datetime.combine(fecha_obj, rutina.hora)
            nueva_visita = Visita(
                rutina_id=rutina.id,
                fecha=fecha_visita,
                qr_codigo=generar_codigo_qr_unico(),
                verificado=False
            )
            db.session.add(nueva_visita)

            asign = db.session.query(AsignacionRepartidor).filter_by(
                repartidor_id=rutina.repartidor_id,
                fecha=fecha_obj
            ).first()
            if asign:
                asign.total_asignado += cantidad_nueva
            else:
                db.session.add(AsignacionRepartidor(
                    repartidor_id=rutina.repartidor_id,
                    fecha=fecha_obj,
                    total_asignado=cantidad_nueva
                ))

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

def EliminarRutina(rutina_id):
    try:
        rutina = db.session.query(Rutina).get(rutina_id)
        if not rutina:
            return False

        visitas = db.session.query(Visita).filter_by(rutina_id=rutina_id).all()
        for v in visitas:
            db.session.delete(v)
        db.session.delete(rutina)
        db.session.commit()
        return True

    except Exception:
        db.session.rollback()
        return False

def obtener_visitas_proximas(usuario_id):
    ahora = datetime.now()
    return (
        db.session.query(Visita)
        .join(Rutina)
        .filter(Visita.fecha >= ahora, Rutina.usuario_id == usuario_id)
        .order_by(Visita.fecha.asc())
        .all()
    )