---
theme : "night"
transition: "fade"
highlightTheme: "monokai"
logoImg: "images/reply_logo.png"
slideNumber: true
title: "Automation on K8s"

---

Hey! 👋

![Me](images/me.png){style="border:none;border-radius:41%"}{.fragment}

--

I work as a Rollout DevOps Engineer @ Allianz.{.fragment .current-visible}

We use Azure as the underlying infrastructure provider.{.fragment .current-visible}

Compute is done exclusively on Kubernetes.{.fragment .current-visible}

--

The project is about creating middleware to do data aggregation from multiple OEs within Allianz.{.fragment .current-visible}

When I started this project, I was tasked with the creation of a generic software delivery pipeline.{.fragment .current-visible}

--

This software delivery pipeline has to run on **K8s**{.fragment .highlight-red}.{.fragment}

It has to be generic enough to support any arbitrary workflow,
including **CI/CD**{.fragment .highlight-blue} workloads.{.fragment}

Finally, it should be **modular**{.fragment .highlight-green}.{.fragment}

--

On top of that, I have to regularly provision cloud resources to prototype new ideas.{.fragment .current-visible}

Before handing the provisioning task over to another team,{.fragment .current-visible}

I have to write some code to provision my experimental setup in a **repeatable**{.fragment .highlight-red} way.{.fragment}

--

This talk is about the automation patterns I've found whilst implementing this software delivery pipeline.{.fragment .current-visible}

We'll briefly cover a lot of topics in a short period of time. {.fragment .current-visible}

Please don't be afraid to stop me and ask your question about the topic I'm covering. {.fragment .current-visible}

---

[//]: # (Requirements)

--

## Let's recap our requirements:

* Run on K8s{.fragment}
* Be cloud/git provider agnostic{.fragment}
* Loosely coupled{.fragment}
* Easily extendible/replacable{.fragment}

--

Before we start on our CI/CD platform,{.fragment}

</br>

How do we automate provisioning of the underlying infrastructure?{.fragment}

</br>
</br>

#### The answer is Terraform, or Pulumi.{.fragment}

---

Here's what provisioning code looks like:{.fragment}
```python{style="font-size:xx-large;line-height:150%" .fragment}
import pulumi
import pulumi_digitalocean as digitalocean

playground = digitalocean.Project("playground",
    description="A project to represent development resources.",
    environment="Development",
    purpose="Web Application")
```

I'm using the [digitalocean provider](https://www.pulumi.com/registry/packages/digitalocean/api-docs/) of Pulumi.{.fragment}

--

You can **create**{.fragment .highlight-green}/**manage**{.fragment .highlight-blue}/**delete**{.fragment .highlight-red} any supported resource using the same code pattern as before.{.fragment}

</br>

Let's provision some basic playground.{.fragment}

--

<!-- .slide: data-background="images/demo_time.gif" -->

---

[//]: # (Deep Dive into CI/CD)

---

# CI/CD?
::: block
*"Our CI/CD pipeline takes 10 mins to finish."* {.fragment style=background:red;width:66%}
:::
---
*"You have a pipeline? WTF I still deploy manually. :(("* {.fragment style=background:red;margin-left:33%;width:66%}

--

"What the hell is CI/CD?"

--

[CI: Continous Integration](https://aws.amazon.com/devops/continuous-integration/)

* Merge code **frequently**{.fragment .highlight-green}.{.fragment}

* Run automated test/builds **on every change**{.fragment .highlight-green}.{.fragment}

* Make releases **easier**{.fragment .highlight-green} and dev cycles **shorter**{.fragment .highlight-green}.{.fragment}

--

[//]: # (CD definition)

--

[CD: Continous Delivery](https://aws.amazon.com/devops/continuous-delivery/)

* **Every time**{.fragment .highlight-green} there's a new artifact, deploy it to an dev/test environment.{.fragment}

* Run integration, end-to-end, manual tests on deployed artifact. {.fragment }

* Always have a deployment-ready artifact for production. {.fragment}

---

[//]: # (CI)

---

# CI/CD on Kubernetes

We have a few options for Continous Integration that fit our [requirements](#/1): {.fragment}
* [Argo Workflow](https://argoproj.github.io/argo-workflows/) {.fragment}
* [Tekton](https://tekton.dev/docs/) {.fragment}

--

I picked Argo Workflow, because the infra team already uses ArgoCD. {.fragment}

</br>

I've also worked with it before. {.fragment}

---

[//]: # (CD)

---

## How does Argo Workflows work?

The answer is: [Controllers.](https://kubernetes.io/docs/concepts/architecture/controller/) {.fragment}

The controller pattern is a core K8s building block. {.fragment}

--

## What does a K8s resource look like?

```yaml{.fragment}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 2 # tells deployment to run 2 pods matching the template
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

--

## How do you know how this resource spec looks like?

There's an [API reference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.22/).
{.fragment}

--

## How can I extend K8s with custom controllers?

We need to take a look at the [operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/).{.fragment}

</br>

There's so many operators out there. {.fragment}

You can browse through them @ [operatorhub.io](https://operatorhub.io). {.fragment}

--

## Does Argo Workflows use this pattern?

Yes, Argo Workflows is implemented as a Kubernetes CRD (Custom Resource Definition).{.fragment}

Argo controllers periodically reconcile between the actual state and the desired state of custom resources of kind `Workflow`.{.fragment}

--

## What does an Workflow resource look like?
```yaml{.fragment}
apiVersion: argoproj.io/v1alpha1
kind: Workflow                  # new type of k8s spec
metadata:
  generateName: hello-world-    # name of the workflow spec
spec:
  entrypoint: whalesay          # invoke the whalesay template
  templates:
  - name: whalesay              # name of the template
    container:
      image: docker/whalesay
      command: [cowsay]
      args: ["hello world"]
      resources:                # limit the resources
        limits:
          memory: 32Mi
          cpu: 100m
```

---

## Intermission

That was a lot.{.fragment .current-visible}

But now we know what K8s operators are, and how they work. {.fragment .current-visible}

We are now going to deploy a complex, operator-based application.{.fragment}

---

## Intermission

We now have a lot a resource manifests on our hands, but still no way to automatically deploy them.

---

## Continous Delivery

Let's revisit the [definition.](#/4/4) {.fragment}

So, we need to make sure that all releases are deployed periodically, using a sync loop. {.fragment}

A release here can be any logical grouping of a set of K8s resources. {.fragment}

--

## ArgoCD

Let's deploy ArgoCD and have a look at the UI. {.fragment}

Same operator pattern as Argo Workflows. {.fragment}

ArgoCD creates a custom resource definition aptly named `Application`.{.fragment}

--

Now that we have some manifests, where are we going store them? {.fragment}

We already use git for everything, including code and configs, so let's use that. {.fragment}

Let's add some application resources to our cluster, and see what happens. {.fragment}


--

<!-- .slide: data-background="images/demo_time.gif" -->

---

### WTF is GitOps?

<div class="tweet" data-src="https://twitter.com/weaveworks/status/1452685502130401285" style="width:100%;display:flex;justify-content:center"></div>

--

### WTF is GitOps?

</br>

You'll hear this term often when working with operators. {.fragment}

Git is used to store the desired state of your resources. {.fragment}

The actual state of your resources is saved into Etcd (K8s control plane). {.fragment}

---

## Going Meta

The question is:

Is it possible to deploy ArgoCD using **itself**? {.fragment}

--

<!-- .slide: data-background="images/what.gif" -->

--

### Definition of meta-: {.fragment}

> denoting something of a higher or second-order kind.
> Ex:"metaprogramming" {.fragment}

>  referring to itself or to the conventions of its genre; self-referential. {.fragment}

--

### Can we go further from here?

Let's say we want to automate provisioning of **any**{.fragment .highlight-red} cloud resource. {.fragment}

With everything we've seen so far, can you guess where this is going? {.fragment .current-visible}

--

## Introducing:
## Pulumi Operator {.fragment}

> I provision your K8s cluster on top a meta-cluster so that I may deploy manifests that deploy their own manifests. {.fragment}

--

<!-- .slide: data-background="images/ohsnap.gif" -->


---

## Key Takeaways:

* Automatic provisioning of any kind of resource is possible using operators. {.fragment}

* Recursive references create some funny situations. Try deleting a recursively provisioned cluster.{.fragment}

* Metaclusters are not absolutely necessary, but can be [useful](https://www.youtube.com/watch?v=wzj2VQutJws). {.fragment}

---

<!-- .slide: style="text-align: left;" -->

# THE END

- [Metaclusters at Alibaba](https://discourse.world/h/2020/01/09/How-Alibaba-Cloud-manages-tens-of-thousands-of-Kubernetes-clusters-with...Kubernetes) {.fragment}

- [Metaclusters at Datadog](https://www.youtube.com/watch?v=wzj2VQutJws) {.fragment}

- [What is Crossplane?](https://www.youtube.com/watch?v=UffM5Gr1m-0) {.fragment}

- [Github repo]() {.fragment}




