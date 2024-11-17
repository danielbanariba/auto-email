import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time
import os

# Desactivar la variable de entorno SSLKEYLOGFILE
if 'SSLKEYLOGFILE' in os.environ:
    del os.environ['SSLKEYLOGFILE']

def verify_credentials(email, password):
    try:
        # Crear contexto SSL sin verificación de archivo de log
        context = ssl.create_default_context()
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(email, password)
        server.quit()
        return True
    except Exception as e:
        print(f"\nError de verificación de credenciales: {str(e)}")
        print("\nPor favor asegúrate de:")
        print("1. Tener activada la verificación en dos pasos")
        print("2. Usar una contraseña de aplicación válida")
        print("3. El correo y la contraseña son correctos")
        return False

def send_email(sender_email, app_password, recipient, name, subject):
    smtp_server = "smtp.gmail.com"
    port = 587

    message = MIMEMultipart('alternative')
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = Header(subject, 'utf-8')

    body = f"""
    Hola {name},

    Este es un mensaje de prueba.
    """

    message.attach(MIMEText(body.encode('utf-8'), 'plain', 'utf-8'))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, app_password)
            server.send_message(message)
            print(f"Correo enviado exitosamente a {name} ({recipient})")
    except Exception as e:
        print(f"Error al enviar correo a {name} ({recipient}): {str(e)}")

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['Sheet']

def main():
    sender_email = ""
    # Eliminar espacios de la contraseña ingresada
    app_password = input("Ingresa la contraseña de aplicación de Google (16 caracteres sin espacios): ").replace(" ", "")

    # Verificar credenciales antes de continuar
    print("\nVerificando credenciales...")
    if not verify_credentials(sender_email, app_password):
        return

    subject = "Prueba de envío automático de correos"

    try:
        students = load_data("email.json")
        
        for student in students:
            name = student.get("Nombre")
            email = student.get("Email Institcional")
            
            if not email:
                print(f"No se encontró email para {name}, omitiendo...")
                continue

            print(f"Enviando correo a {name}...")
            send_email(sender_email, app_password, email, name, subject)
            time.sleep(1)

    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == "__main__":
    main()