from datetime import datetime
from googleapiclient.discovery import build

def get_calendar_service():
    """Crea el cliente de Google Calendar."""
    # Asegúrate de tener las credenciales configuradas en el entorno
    return build('calendar', 'v3')

def consultar_disponibilidad(fecha: str) -> str:
    """
    Consulta la agenda respetando el horario de Bogotá.
    Formato fecha: YYYY-MM-DD
    """
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
        dia_semana = fecha_obj.weekday() # 0=Lunes, 5=Sábado, 6=Domingo

        # --- REGLAS DE NEGOCIO ---
        if dia_semana < 5: # Lunes a Viernes
            # UTC conversion: Bogotá es UTC-5, pero Calendar usa UTC o TimeZone aware.
            # Para simplificar, asumimos que el input y output se manejan correctamente o ajustamos offsets.
            # Aquí mantengo tu lógica original de strings ISO:
            t_min = f"{fecha}T18:00:00Z" 
            t_max = f"{fecha}T22:00:00Z"
            msg = "en días laborales (después de las 6:00 PM)"
            
        elif dia_semana == 5: # Sábado
            t_min = f"{fecha}T08:00:00Z" 
            t_max = f"{fecha}T17:00:00Z"
            msg = "el sábado (horario laboral)"
            
        else:
            return "El bufete está cerrado los domingos."

        # --- LLAMADA A API ---
        service = get_calendar_service()
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=t_min, 
            timeMax=t_max,
            singleEvents=True, 
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events: 
            return f"Todo el rango está libre {msg}."
        
        resumen = f"Agenda para {msg}: "
        for e in events:
            start = e['start'].get('dateTime') or e['start'].get('date')
            resumen += f"- Ocupado: {start}. "
            
        return resumen

    except ValueError:
        return "Formato de fecha inválido. Usa YYYY-MM-DD."
    except Exception as e:
        return f"Error técnico consultando agenda: {str(e)}"