from email.message import EmailMessage
import email.utils
import smtplib
from logging.handlers import RotatingFileHandler, SMTPHandler
import logging


# Provide a class to allow SSL (Not TLS) connection for mail handlers by overloading the emit() method
class SSLSMTPHandler(SMTPHandler):

    def emit(self, record):
        """
        Emit a record.
        """
        try:
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP_SSL(self.mailhost, port)
            msg = EmailMessage()
            msg['From'] = self.fromaddr
            msg['To'] = ','.join(self.toaddrs)
            msg['Subject'] = self.subject
            msg['Date'] = email.utils.localtime()
            msg.set_content(self.format(record))
            if self.username:
                smtp.login(self.username, self.password)
            smtp.send_message(msg, self.fromaddr, self.toaddrs)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


mail_formatter = logging.Formatter('''
        Message type:       %(levelname)s
        Location:           %(pathname)s:%(lineno)d
        Module:             %(module)s
        Function:           %(funcName)s
        Time:               %(asctime)s

        Message:

        %(message)s
        ''')

file_formatter = logging.Formatter("[%(asctime)s] |  %(levelname)s | {%(pathname)s:%(lineno)d} | %(message)s")

def handle_logs(app):

    file_handler = RotatingFileHandler('logs/app.log', maxBytes=1 * 1024 * 1024, backupCount=100)
    file_handler.setFormatter(file_formatter)

    if not app.debug:
        file_handler.setLevel(logging.WARN)
        app.logger.addHandler(file_handler)
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SSLSMTPHandler(
                mailhost=(
                    app.config['MAIL_SERVER'],
                    app.config['MAIL_PORT']
                ),
                fromaddr='no-reply@julien-bonnefoy.dev',
                toaddrs=app.config['ADMINS'],
                subject='Website failure',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(mail_formatter)
            app.logger.addHandler(mail_handler)
    else:
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)