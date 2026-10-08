"""Fixed synthetic Responses fixture; no model, gateway or tool executor."""

import http.server
import json
import threading

requests = []


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        if len(body) > 65536:
            self.send_error(413)
            return
        value = json.loads(body)
        requests.append(
            {
                "path": self.path,
                "tools": [t.get("name", t.get("type")) for t in value.get("tools", [])],
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
                        "cmd": "printf tiny > /scratch/native-tiny; cat /scratch/native-tiny",
                        "max_output_tokens": 100,
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


def start():
    server = http.server.HTTPServer(("127.0.0.1", 8081), Handler)
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
        "features.sqlite=false",
        "-c",
        "thread_unload_delay_secs=0",
        "-c",
        "agents.enabled=false",
        "Write tiny into /scratch/native-tiny using command tool. Then finish.",
    ]
