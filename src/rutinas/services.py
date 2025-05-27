from flask import session 
from src.database.coneccion import db, Rutina, Repartidor, Ruta, Visita, Usuario

def CrearRutina(usuario_id, dias, hora, cantidad, marca=None, repartidor_id=None, ruta_id=None):
    try:
        
        repartidores = db.session.query(Repartidor).all()
        asignado = False
        for r in repartidores:
            if r.cantidad + cantidad <= 20:
                r.cantidad += cantidad
                asignado = True
                break
        if not asignado:
            return False

        ruta_existe = db.session.query(Ruta).filter_by(calle=Usuario.calle).first()
        if ruta_existe:
            Ruta.clientes += 1
            db.session.commit()
        else:
            return False
        
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return False
        
        nueva_rutina = Rutina(
            usuario_id=usuario_id,
            dias=dias,
            hora=hora,
            cantidad=cantidad,
            marca=marca,
            repartidor_id=repartidor_id,
            ruta_id=ruta_id
        )
        db.session.add(nueva_rutina)
        db.session.commit()
        return True
    except:
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
    
def InicioSesionPurificadora(contrasena):
    try:
        if contrasena == "contrasena_segura": 
            return True
        else:
            return False
    except:
        return False