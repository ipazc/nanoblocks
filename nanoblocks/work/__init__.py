from .backend.nano_local_work_server import NanoLocalWorkServer
from .backend.nano_remote_work_server import NanoRemoteWorkServer


LOCAL_WORK_SERVER = NanoLocalWorkServer()
NINJA_REMOTE_WORK_SERVER = NanoRemoteWorkServer(work_server_http_url='https://mynano.ninja/api/node')


__all__ = ["NanoLocalWorkServer", "NanoRemoteWorkServer",
           "LOCAL_WORK_SERVER", "NINJA_REMOTE_WORK_SERVER"]
