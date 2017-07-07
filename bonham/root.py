"""
    Bonham Root
    Author: Tim "tjtimer" Jedro
    version: 0.0.1dev

    Root provides the core capabilities for every Service
        -> read from and write to database
        -> sending emails (bonham_mail)
        -> identify the user (bonham_auth)

"""
import logging.config
from asyncio import Event
from multiprocessing import current_process
from pathlib import Path

from bonham.bonham_core.handler_protocol import ServiceProtocol, prepared_socket
from bonham.bonham_core.router import Router
from bonham.bonham_core.templates import Template
from bonham.bonham_core.utils import load_yaml_conf, prepared_uvloop
from bonham.settings import DEBUG, TEMPLATES_DIR

__all__ = [
    'Service'
    ]
config = load_yaml_conf(Path('logging.conf.yaml'))
logging.config.dictConfig(config)

logger = logging.getLogger(__file__)


class Service():
    instance_count = 0
    processes = {}
    process = current_process()

    def __init__(self):
        loop = prepared_uvloop(debug=DEBUG)
        self.wait_for = loop.run_until_complete
        self.router = Router()
        self.loop = loop
        self.index_template = self.wait_for(Template(TEMPLATES_DIR).load('index.html'))
        self.ready = Event()
        self.stopped = Event()
        self.server_protocol = ServiceProtocol
        self.server = None
        #  index.html is the only html document this service and this entire SPA/PWA ever renders
        print('end of Service.__init__(): ', vars(self))
        # setup_swagger(self)

    async def shutdown(self):
        print("shutdown Instance: ", self.server)
        logger.info(f"\n\n{'*'*10} Shutting down Bonham App Server instance {'*'*10}\n\n")
        print(self.server)
        self.server.close()
        await self.server.wait_closed()
        logger.info(f"\n\n{'*'*10} Successfully shut down Bonham App Server instance {'*'*10}\n\n")
        print(self.server)

    def run(self):
        self.instance_count += 1
        self.server = self.wait_for(
                self.loop.create_unix_server(
                        self.server_protocol,
                        # '127.0.1.2', 9091
                        sock=get_socket(self.instance_count)
                        )
                )
        print("after create server called: ", self.index_template)
        self.ready.set()
        print('serving on :', self.server.sockets[0].getsockname())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            print("\n\nKeyboardInterrupt at bonham root\n\n")
            pass
        except Exception as e:
            print(f"\n\n#########\nException at bonham root\n\n{type(e).__name__}")
            pass
        finally:
            self.wait_for(self.shutdown())
            self.wait_for(self.loop.shutdown_asyncgens())
            self.stopped.set()
        print('stopped: ', self.stopped)
        self.loop.stop()
        print(f"App instance {self} successfully shut down")


if __name__ == '__main__':
    service = Service()
    service.run()
    print("end main")
