import pulumi
from pulumi_kubernetes import core, apiextensions

# Get the Pulumi API token.
pulumi_config = pulumi.Config()
pulumi_access_token = pulumi_config.require_secret("pulumiAccessToken")
pulumi_stack_name = pulumi_config.get("nginxStackName")


def init():

    # Create the API token as a Kubernetes Secret.
    access_token = core.v1.Secret(
        "accesstoken", string_data={"access_token": pulumi_access_token}
    )

    # Create an NGINX deployment in-cluster.
    my_stack = apiextensions.CustomResource(
        "my-stack",
        api_version="pulumi.com/v1",
        kind="Stack",
        spec={
            "envRefs": {
                "PULUMI_ACCESS_TOKEN": {
                    "type": "Secret",
                    "secret": {
                        "name": access_token.metadata.name,
                        "key": "access_token",
                    },
                },
            },
            "stack": pulumi_stack_name,
            "projectRepo": "https://github.com/ig0rsky/pulumi-nginx",
            # "commit": "2b0889718d3e63feeb6079ccd5e4488d8601e353",
            "branch": "refs/heads/master",  # Alternatively, track master branch.
            "destroyOnFinalize": True,
        },
    )
    return locals()
