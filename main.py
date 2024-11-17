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
        
        # Desactivar la variable de entorno SSLKEYLOGFILE
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
            context = ssl.create_default_context()
            server = smtplib.SMTP(
                self.config['email_settings']['smtp_server'],
                self.config['email_settings']['port']
            )
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(email, password)
            server.quit()
            return True
        except Exception as e:
            error_config = self.config['error_messages']['credentials']
            print(error_config['message'].format(error=str(e)))
            for instruction in error_config['instructions']:
                print(instruction)
            return False

    def create_email_body(self, name):
        template = self.config['email_template']
        fecha = self.get_formatted_date()
        
        body_parts = [
            f"{template['location']}, {fecha}",
            "",
            template['greeting'].format(name=name),
            "",
            template['body'],
            "",
            template['survey_intro'],
            "",
            template['survey_link'],
            "",
            template['closing'],
            "",
            template['signature']
        ]
        
        return "\n".join(body_parts)

    def send_email(self, sender_email, password, recipient, name):
        settings = self.config['email_settings']
        template = self.config['email_template']
        
        message = MIMEMultipart('alternative')
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = Header(template['subject'], 'utf-8')

        body = self.create_email_body(name)
        message.attach(MIMEText(body.encode('utf-8'), 'plain', 'utf-8'))

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(settings['smtp_server'], settings['port']) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(sender_email, password)
                server.send_message(message)
                print(f"Correo enviado exitosamente a {name} ({recipient})")
        except Exception as e:
            print(f"Error al enviar correo a {name} ({recipient}): {str(e)}")

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['Sheet']

def main():
    email_sender = EmailSender()
    sender_email = email_sender.config['email_settings']['sender_email']
    password = input("Ingresa tu contraseña: ")

    print("\nVerificando credenciales...")
    if not email_sender.verify_credentials(sender_email, password):
        return

    try:
        students = load_data("email.json")
        
        for student in students:
            name = student.get("Nombre")
            email = student.get("Email Institcional")
            
            if not email:
                print(f"No se encontró email para {name}, omitiendo...")
                continue

            print(f"Enviando correo a {name}...")
            email_sender.send_email(sender_email, password, email, name)
            time.sleep(1)

    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == "__main__":
    main()