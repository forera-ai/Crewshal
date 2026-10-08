"""Fixed authenticated synthetic provider fixture, outside every worker view."""

import http.server
import json
import socket
import threading

requests = []
workload_mode = "workload"


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        ok = self.headers.get("Authorization") == self.server.expected_auth
        self.server.auth_observations.append(
            {"path": self.path, "auth_matches": ok, "host": self.headers.get("Host")}
        )
        if not ok:
            self.send_error(403)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 <= length <= 65536:
            self.send_error(413)
            return
        body = self.rfile.read(length)
        value = json.loads(body)
        if value.get("transport_probe"):
            self.server.transport_observations.append(
                {
                    "probe": value["transport_probe"],
                    "auth_matches": ok,
                    "host": self.headers.get("Host"),
                }
            )
            if value["transport_probe"] == "redirect":
                self.send_response(307)
                self.send_header("Location", "http://127.0.0.1:8082/nonallowed")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        requests.append(
            {
                "path": self.path,
                "tool_outputs": [
                    {"call_id": x.get("call_id"), "output": str(x.get("output", ""))[:4096]}
                    for x in value.get("input", [])
                    if x.get("type") == "function_call_output"
                ],
                "tools": [t.get("name", t.get("type")) for t in value.get("tools", [])],
                "instruction_markers": [
                    marker
                    for marker in ("Synthetic injection:", "Synthetic global injection:")
                    if marker in body.decode(errors="replace")
                ],
                "instruction_injection_present": any(
                    marker in body.decode(errors="replace")
                    for marker in ("Synthetic injection:", "Synthetic global injection:")
                ),
            }
        )
        item = (
            {
                "id": "fc_tiny",
                "type": "function_call",
                "call_id": "call_tiny",
                "name": "exec_command",
                "arguments": json.dumps(
                    {
                        "cmd": "exec /bin/python3 -I -B /input/native-full-payload.py "
                        + workload_mode,
                        "max_output_tokens": 100,
                        "yield_time_ms": 10000,
                    }
                ),
            }
            if len(requests) == 1
            else {
                "id": "msg_tiny",
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": "tiny", "annotations": []}],
            }
        )
        response = {
            "id": "resp_tiny_" + str(len(requests)),
            "object": "response",
            "model": "synthetic",
            "status": "completed",
            "output": [item],
            "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
        }
        events = [
            ("response.created", {"response": dict(response, status="in_progress", output=[])}),
            ("response.output_item.added", {"output_index": 0, "item": item}),
            ("response.output_item.done", {"output_index": 0, "item": item}),
            ("response.completed", {"response": response}),
        ]
        data = "".join(
            "event: " + name + "\ndata: " + json.dumps(dict(value, type=name)) + "\n\n"
            for name, value in events
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def start(expected_auth):
    server = http.server.HTTPServer(("127.0.0.1", 8081), Handler)
    server.expected_auth = expected_auth
    server.auth_observations = []
    server.transport_observations = []
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def native_command(port):
    return [
        "/opt/codex/bin/codex",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--color",
        "never",
        "--json",
        "-C",
        "/scratch/checkout",
        "--add-dir",
        "/candidate/owned",
        "--add-dir",
        "/scratch",
        "-s",
        "workspace-write",
        "-m",
        "synthetic",
        "-c",
        'approval_policy="never"',
        "-c",
        'model_provider="fixture"',
        "-c",
        'model_providers.fixture.name="fixture"',
        "-c",
        'model_providers.fixture.base_url="http://127.0.0.1:' + str(port) + '/v1"',
        "-c",
        'model_providers.fixture.wire_api="responses"',
        "-c",
        "model_providers.fixture.requires_openai_auth=false",
        "-c",
        "model_providers.fixture.request_max_retries=0",
        "-c",
        "model_providers.fixture.stream_max_retries=0",
        "-c",
        "features.shell_snapshot=false",
        "-c",
        "project_doc_max_bytes=0",
        "-c",
        "features.sqlite=false",
        "-c",
        "thread_unload_delay_secs=0",
        "-c",
        "agents.enabled=false",
        "-c",
        "features.goals=false",
        "-c",
        "features.memories=false",
        "-c",
        "features.multi_agent=false",
        "-c",
        "features.hooks=false",
        "-c",
        "features.view_image=false",
        "-c",
        'web_search="disabled"',
        "-c",
        "analytics.enabled=false",
        "-c",
        "feedback.enabled=false",
        "-c",
        'otel.exporter="none"',
        "-c",
        'otel.trace_exporter="none"',
        "-c",
        'otel.metrics_exporter="none"',
        "-c",
        "check_for_update_on_startup=false",
        "-c",
        "features.plugins=false",
        "-c",
        "features.remote_plugin=false",
        "-c",
        "features.recommended_plugins=false",
        "-c",
        "features.plugin_hooks=false",
        "-c",
        "features.apps=false",
        "-c",
        "skills.bundled.enabled=false",
        "-c",
        "skills.include_instructions=false",
        "-c",
        "features.skip_host_skill_discovery=true",
        "-c",
        "allow_login_shell=false",
        "Write tiny into /scratch/native-tiny using command tool. Then finish.",
    ]


class SinkHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.server.observations.append(
            {"path": self.path, "bytes": len(self.rfile.read(min(length, 65536)))}
        )
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")


def start_sink():
    server = http.server.HTTPServer(("127.0.0.1", 8082), SinkHandler)
    server.observations = []
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def start_datagram_sinks():
    observations = []
    sockets = []
    stop = threading.Event()
    threads = []
    for family, name, address in (
        (socket.AF_INET, "udp", ("127.0.0.1", 8082)),
        (socket.AF_INET, "dns", ("127.0.0.1", 53)),
        (socket.AF_INET6, "ipv6", ("::1", 8082)),
    ):
        listener = socket.socket(family, socket.SOCK_DGRAM)
        listener.bind(address)
        listener.settimeout(0.05)
        sockets.append(listener)

        def receive(channel=listener, label=name):
            while not stop.is_set():
                try:
                    data, _ = channel.recvfrom(65536)
                    observations.append({"sink": label, "bytes": len(data)})
                except socket.timeout:
                    pass
                except OSError:
                    break

        thread = threading.Thread(target=receive, daemon=True)
        thread.start()
        threads.append(thread)
        with socket.socket(family, socket.SOCK_DGRAM) as control:
            control.sendto(b"control", address)
    return observations, sockets, stop, threads
