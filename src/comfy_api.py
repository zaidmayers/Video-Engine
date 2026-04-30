"""ComfyUI API client — uploads images, queues prompts, polls for results."""

import json
import os
import time
import uuid
import urllib.request
import urllib.parse
import requests


class ComfyAPIError(Exception):
    pass


class ComfyClient:
    def __init__(self, host: str, port: int):
        self.base_url = f"http://{host}:{port}"
        self.client_id = str(uuid.uuid4())

    def is_ready(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def wait_until_ready(self, timeout: int = 120) -> None:
        deadline = time.time() + timeout
        print("  Waiting for ComfyUI server...", end="", flush=True)
        while time.time() < deadline:
            if self.is_ready():
                print(" ready.")
                return
            time.sleep(2)
            print(".", end="", flush=True)
        raise ComfyAPIError(f"ComfyUI not reachable at {self.base_url} after {timeout}s")

    def upload_image(self, image_path: str, subfolder: str = "") -> str:
        """Upload an image to ComfyUI input directory. Returns the uploaded filename."""
        with open(image_path, "rb") as f:
            data = f.read()
        filename = os.path.basename(image_path)
        files = {"image": (filename, data, "image/png")}
        params = {"overwrite": "true"}
        if subfolder:
            params["subfolder"] = subfolder
        r = requests.post(f"{self.base_url}/upload/image", files=files, data=params)
        r.raise_for_status()
        result = r.json()
        return result.get("name", filename)

    def queue_prompt(self, workflow: dict) -> str:
        """Queue a prompt and return the prompt_id."""
        payload = {"prompt": workflow, "client_id": self.client_id}
        r = requests.post(
            f"{self.base_url}/prompt",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise ComfyAPIError(f"Workflow error: {data['error']}\nDetails: {data.get('node_errors', {})}")
        return data["prompt_id"]

    def wait_for_prompt(self, prompt_id: str, timeout: int = 3600, poll_interval: int = 5) -> dict:
        """Poll until the prompt completes. Handles ComfyUI disconnects with automatic reconnect."""
        deadline = time.time() + timeout
        print(f"  Generating [prompt={prompt_id[:8]}]", end="", flush=True)
        down_since = None

        while time.time() < deadline:
            try:
                r = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=10)
                r.raise_for_status()
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    requests.exceptions.HTTPError):
                if down_since is None:
                    down_since = time.time()
                    print(f"\n  [!] ComfyUI connection lost — waiting for restart...", flush=True)
                elif time.time() - down_since > 300:
                    raise ComfyAPIError(
                        "ComfyUI has been unreachable for 5+ minutes. "
                        "It likely crashed (OOM). Restart ComfyUI and re-run with --skip-images."
                    )
                time.sleep(15)
                continue

            if down_since is not None:
                print(f"  [OK] ComfyUI reconnected. Continuing...", flush=True)
                down_since = None

            history = r.json()
            if prompt_id in history:
                entry = history[prompt_id]
                status = entry.get("status", {})
                if status.get("completed"):
                    print(" done.")
                    return entry
                if status.get("status_str") == "error":
                    msgs = [m for m in status.get("messages", []) if m[0] == "execution_error"]
                    raise ComfyAPIError(f"Execution error: {msgs}")

            time.sleep(poll_interval)
            print(".", end="", flush=True)

        raise ComfyAPIError(f"Prompt {prompt_id} timed out after {timeout}s")

    def get_output_files(self, history_entry: dict) -> list[dict]:
        """Extract list of output file dicts from a history entry."""
        files = []
        outputs = history_entry.get("outputs", {})
        for node_id, node_output in outputs.items():
            for key in ("images", "videos", "gifs", "audios"):
                for item in node_output.get(key, []):
                    files.append(item)
        return files

    def download_output(self, file_info: dict, dest_path: str) -> str:
        """Download an output file. Returns the saved path."""
        params = {
            "filename": file_info["filename"],
            "subfolder": file_info.get("subfolder", ""),
            "type": file_info.get("type", "output"),
        }
        url = f"{self.base_url}/view?" + urllib.parse.urlencode(params)
        r = requests.get(url, stream=True)
        r.raise_for_status()
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
        return dest_path

    def run_workflow(self, workflow: dict, dest_path: str, timeout: int = 1800) -> str:
        """Queue workflow, wait for completion, download first output file."""
        prompt_id = self.queue_prompt(workflow)
        entry = self.wait_for_prompt(prompt_id, timeout=timeout)
        files = self.get_output_files(entry)
        if not files:
            raise ComfyAPIError("Workflow completed but produced no output files")
        return self.download_output(files[0], dest_path)
