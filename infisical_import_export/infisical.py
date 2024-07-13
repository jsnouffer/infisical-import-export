import json
import os

import requests


class InfisicalClient:
    def __init__(self, url: str, environment: str, workspace_id: str, client_id: str, client_secret: str):
        self.url = url
        self.environment = environment
        self.workspace_id = workspace_id
        self.token = self.__login(client_id, client_secret)
        self.auth_header = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def __login(self, client_id: str, client_secret: str) -> str:
        request_url: str = f"{self.url}/api/v1/auth/universal-auth/login"
        payload = {"clientId": client_id, "clientSecret": client_secret}

        response = requests.request(
            "POST",
            request_url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()["accessToken"]

    def get_folders(self, folder: str = None) -> list[str]:
        request_url: str = f"{self.url}/api/v1/folders?environment={self.environment}&workspaceId={self.workspace_id}"

        if folder:
            request_url = request_url + f"&directory={folder}"

        response = requests.request(
            "GET",
            request_url,
            headers=self.auth_header,
        )
        response.raise_for_status()
        folders: list[str] = ["/"]
        for f in [f"{folder if folder else ''}/{x['name']}" for x in response.json()["folders"]]:
            folders.append(f)
            for subfolder in self.get_folders(folder=f"{f}"):
                if subfolder != "/":
                    folders.append(f"{subfolder}")

        return folders

    def create_folder(self, path: str) -> None:
        request_url: str = f"{self.url}/api/v1/folders"
        payload: dict = {
            "environment": self.environment,
            "workspaceId": self.workspace_id,
            "name": os.path.basename(os.path.normpath(path)),
            "folderName": os.path.basename(os.path.normpath(path)),
            "directory": os.path.dirname(os.path.normpath(path)),
            "path": os.path.dirname(os.path.normpath(path)),
        }

        response = requests.request(
            "POST",
            request_url,
            json=payload,
            headers=self.auth_header,
        )
        response.raise_for_status()

    def create_folders(self, paths: list[str]) -> None:
        for path in paths:
            if path != "/":
                self.create_folder(path)

    def get_secrets(self, path: str) -> list[dict]:
        request_url: str = f"{self.url}/api/v3/secrets/raw?environment={self.environment}&workspaceId={self.workspace_id}&secretPath={path}"
        response = requests.request(
            "GET",
            request_url,
            headers=self.auth_header,
        )
        response.raise_for_status()
        return response.json()["secrets"] if "secrets" in response.json() else []

    def get_all_secrets(self) -> dict[str, list[dict]]:
        secrets: dict = {}
        for folder in self.get_folders():
            secrets[folder] = self.get_secrets(path=folder)
        return secrets

    def create_secret(self, path: str, secret: dict) -> None:
        request_url: str = f"{self.url}/api/v3/secrets/raw/{secret['secretKey']}"
        payload: dict = {
            "environment": self.environment,
            "workspaceId": self.workspace_id,
            "secretPath": os.path.normpath(path),
            "secretValue": secret["secretValue"],
            "secretComment": secret["secretComment"],
            "type": secret["type"],
        }

        print(f"Creating secret {path}{'/' if path != '/' else ''}{secret['secretKey']}")
        response = requests.request(
            "DELETE",
            request_url,
            json=payload,
            headers=self.auth_header,
        )
        response = requests.request(
            "POST",
            request_url,
            json=payload,
            headers=self.auth_header,
        )
        response.raise_for_status()

    def import_from_file(self, path: str) -> None:
        with open(path, "r") as f:
            secrets: dict = json.load(f)
        self.import_from_dict(secrets)

    def import_from_dict(self, secrets: dict) -> None:
        self.create_folders(secrets.keys())
        for path in secrets:
            for secret in secrets[path]:
                self.create_secret(path, secret)

    def export_all(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.get_all_secrets(), f, indent=2)
