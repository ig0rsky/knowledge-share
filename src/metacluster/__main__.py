"""A DigitalOcean Python Pulumi program"""

import pulumi
import pulumi_digitalocean as digitalocean
import pulumi_op as operator
import pulumi_kubernetes as kubernetes
import nginx

playground = digitalocean.Project(
    "playground",
    description="A project to represent development resources.",
    environment="Development",
    purpose="Knowledge Share",
)

cluster = digitalocean.KubernetesCluster(
    "metacluster",
    region="fra1",
    version="1.21.5-do.0",
    node_pool=digitalocean.KubernetesClusterNodePoolArgs(
        name="default-pool",
        size="s-2vcpu-2gb",
        auto_scale=True,
        min_nodes=2,
        max_nodes=4,
    ),
)

pulumi.export("kubeconfig", cluster.kube_configs)
pulumi.export("apiserver_endpoint", cluster.endpoint)
pulumi.export("cluster_urn", cluster.urn)

kubecfg_name = "cluster_kubecfg.json"
cluster.kube_configs.apply(lambda config: write_kubeconfig(config, kubecfg_name))


def write_kubeconfig(config, filename):
    import json

    with open(filename, "w") as f:
        f.write(json.dumps(config))
    kubernetes.Provider("kubernetes-provider", kubeconfig=str(cluster.kube_configs))


operator.init()
nginx.init()


# Cannot associate a Kubernetes project with a Project, yet.
# See here: https://www.pulumi.com/registry/packages/digitalocean/api-docs/projectresources/
