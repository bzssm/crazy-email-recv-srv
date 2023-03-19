import json

from smtpx import CrazySrvHandler
from web import web_start

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP

if __name__ == "__main__":
    json_str = open("config.json").read()
    cf = json.loads(json_str)

    smtpd_host = cf["smtpd"]["host"]
    smtpd_port = cf["smtpd"]["port"]

    rest_host = smtpd_host
    rest_port = cf["rest"]["port"]

    handler = CrazySrvHandler()
    controller = Controller(handler, hostname=smtpd_host, port=smtpd_port)
    controller.factory = lambda: SMTP(handler, enable_SMTPUTF8=True)

    try:
        controller.start()
        web_start(rest_host, rest_port)
    except KeyboardInterrupt:
        print("Shutting down")
    finally:
        controller.stop()