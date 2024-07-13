import os

from .infisical import InfisicalClient

if __name__ == "__main__":
    client1: InfisicalClient = InfisicalClient(
        url=os.environ["INFISICAL_URL_1"],
        environment=os.environ["INFISICAL_ENVIRONMENT_1"],
        workspace_id=os.environ["INFISICAL_WORKSPACE_ID_1"],
        client_id=os.environ["INFISICAL_CLIENT_ID_1"],
        client_secret=os.environ["INFISICAL_CLIENT_SECRET_1"],
    )
    client2: InfisicalClient = InfisicalClient(
        url=os.environ["INFISICAL_URL_2"],
        environment=os.environ["INFISICAL_ENVIRONMENT_2"],
        workspace_id=os.environ["INFISICAL_WORKSPACE_ID_2"],
        client_id=os.environ["INFISICAL_CLIENT_ID_2"],
        client_secret=os.environ["INFISICAL_CLIENT_SECRET_2"],
    )

    client2.import_from_dict(client1.get_all_secrets())
