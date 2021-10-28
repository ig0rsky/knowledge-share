import pulumi
from pulumi.resource import ResourceOptions
import pulumi_kubernetes as kubernetes

# Work around https://github.com/pulumi/pulumi-kubernetes/issues/1481
def delete_status():
    def f(o):
        if "status" in o:
            del o["status"]

    return f


def init():
    crds = kubernetes.yaml.ConfigFile(
        "crds",
        file="https://raw.githubusercontent.com/pulumi/pulumi-kubernetes-operator/master/deploy/crds/pulumi.com_stacks.yaml",
        transformations=[delete_status()],
    )

    operator_service_account = kubernetes.core.v1.ServiceAccount(
        "operatorServiceAccount",
        metadata={
            "name": "pulumi-kubernetes-operator",
        },
    )
    operator_role = kubernetes.rbac.v1.Role(
        "operatorRole",
        metadata={
            "name": "pulumi-kubernetes-operator",
        },
        rules=[
            {
                "api_groups": [""],
                "resources": [
                    "pods",
                    "services",
                    "services/finalizers",
                    "endpoints",
                    "persistentvolumeclaims",
                    "events",
                    "configmaps",
                    "secrets",
                ],
                "verbs": [
                    "create",
                    "delete",
                    "get",
                    "list",
                    "patch",
                    "update",
                    "watch",
                ],
            },
            {
                "api_groups": ["apps"],
                "resources": [
                    "deployments",
                    "daemonsets",
                    "replicasets",
                    "statefulsets",
                ],
                "verbs": [
                    "create",
                    "delete",
                    "get",
                    "list",
                    "patch",
                    "update",
                    "watch",
                ],
            },
            {
                "api_groups": ["monitoring.coreos.com"],
                "resources": ["servicemonitors"],
                "verbs": [
                    "create",
                    "get",
                ],
            },
            {
                "api_groups": ["apps"],
                "resource_names": ["pulumi-kubernetes-operator"],
                "resources": ["deployments/finalizers"],
                "verbs": ["update"],
            },
            {
                "api_groups": [""],
                "resources": ["pods"],
                "verbs": ["get"],
            },
            {
                "api_groups": ["apps"],
                "resources": [
                    "replicasets",
                    "deployments",
                ],
                "verbs": ["get"],
            },
            {
                "api_groups": ["pulumi.com"],
                "resources": ["*"],
                "verbs": [
                    "create",
                    "delete",
                    "get",
                    "list",
                    "patch",
                    "update",
                    "watch",
                ],
            },
            {
                "api_groups": ["coordination.k8s.io"],
                "resources": ["leases"],
                "verbs": [
                    "create",
                    "get",
                    "list",
                    "update",
                ],
            },
        ],
    )
    operator_role_binding = kubernetes.rbac.v1.RoleBinding(
        "operatorRoleBinding",
        metadata={
            "name": "pulumi-kubernetes-operator",
        },
        subjects=[
            {
                "kind": "ServiceAccount",
                "name": "pulumi-kubernetes-operator",
            }
        ],
        role_ref={
            "kind": "Role",
            "name": "pulumi-kubernetes-operator",
            "api_group": "rbac.authorization.k8s.io",
        },
    )
    operator_deployment = kubernetes.apps.v1.Deployment(
        "operatorDeployment",
        metadata={
            "name": "pulumi-kubernetes-operator",
        },
        spec={
            "replicas": 1,
            "selector": {
                "match_labels": {
                    "name": "pulumi-kubernetes-operator",
                },
            },
            "template": {
                "metadata": {
                    "labels": {
                        "name": "pulumi-kubernetes-operator",
                    },
                },
                "spec": {
                    "service_account_name": "pulumi-kubernetes-operator",
                    "image_pull_secrets": [
                        {
                            "name": "pulumi-kubernetes-operator",
                        }
                    ],
                    "containers": [
                        {
                            "name": "pulumi-kubernetes-operator",
                            "image": "pulumi/pulumi-kubernetes-operator:v1.0.0",
                            "command": ["pulumi-kubernetes-operator"],
                            "args": ["--zap-level=debug"],
                            "image_pull_policy": "Always",
                            "env": [
                                {
                                    "name": "WATCH_NAMESPACE",
                                    "value_from": {
                                        "field_ref": {
                                            "field_path": "metadata.namespace",
                                        },
                                    },
                                },
                                {
                                    "name": "POD_NAME",
                                    "value_from": {
                                        "field_ref": {
                                            "field_path": "metadata.name",
                                        },
                                    },
                                },
                                {
                                    "name": "OPERATOR_NAME",
                                    "value": "pulumi-kubernetes-operator",
                                },
                            ],
                        }
                    ],
                },
                "terminationGracePeriodSeconds": 300,
            },
        },
        opts=ResourceOptions(depends_on=crds),
    )
    return locals()
