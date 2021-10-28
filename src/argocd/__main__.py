import pulumi

from pulumi_kubernetes.core.v1 import Namespace, LimitRange
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


argocd_ns = Namespace("argo-cd")

argocd_lr = LimitRange(
    "argo-cd-lr",
    metadata={"namespace": argocd_ns.id},
    spec={
        "limits": [
            {
                "type": "Container",
                "default_request": {"cpu": "100m", "memory": "128Mi"},
                "default": {"cpu": "1000m", "memory": "1024Mi"},
            }
        ]
    },
)
chart_name = "argocd"
argocd = Chart(
    chart_name,
    config=ChartOpts(
        chart="argo-cd",
        namespace=argocd_ns.id,
        version="3.17.6",
        fetch_opts=FetchOpts(
            repo="https://argoproj.github.io/argo-helm/",
        ),
        values={
            "dex": {"enabled": False},
        },
    ),
)

pulumi.export("argocd_ns", argocd_ns.id)
