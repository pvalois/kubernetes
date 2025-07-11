#!/usr/bin/env python3

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from colorama import Fore, Style, init
import argparse

init(autoreset=True)

def check_cluster_health():
    try:
        config.load_kube_config()  # Charge ~/.kube/config
        v1 = client.CoreV1Api()
    except ApiException as e:
        print(f"❌ Problème avec l’API Kubernetes: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

    print(f"🔗 API access: OK")

    # Check nœuds
    nodes = v1.list_node().items
    if not nodes:
        print(f"❌ Aucun nœud détecté.")
        return False
    for node in nodes:
        name = node.metadata.name
        conditions = {cond.type: cond.status for cond in node.status.conditions}
        if conditions.get("Ready") != "True":
            print(f"⚠️  Node {name} n’est pas Ready.")
        else:
            print(f"✅ Node {name} est Ready.")

    # Check kube-system pods
    pods = v1.list_namespaced_pod("kube-system").items
    for pod in pods:
        status = pod.status.phase
        if status not in ("Running", "Succeeded"):
            print(f"⚠️  kube-system Pod {pod.metadata.name} => {status}")
    print(f"✅ kube-system pods check terminé")

    # Check composants critiques
    expected = ["kube-apiserver", "kube-controller-manager", "kube-scheduler"]
    for name in expected:
        found = any(name in pod.metadata.name for pod in pods)
        mark = f"✅" if found else f"{Fore.RED}❌"
        print(f"{mark} {name}")

    return True

def check_pods(verbose=False):
    print("")
    config.load_kube_config()
    v1 = client.CoreV1Api()
    all_pods = v1.list_pod_for_all_namespaces().items

    running_pods = []
    pending_pods = []
    failed_pods = []

    for pod in all_pods:
        status = pod.status.phase
        conditions = pod.status.conditions or []

        if status == "Running":
            ready_cond = next((c for c in conditions if c.type == "Ready"), None)
            if ready_cond and ready_cond.status == "True":
                running_pods.append(pod)
            else:
                pending_pods.append(pod)
        elif status == "Pending":
            pending_pods.append(pod)
        else:
            failed_pods.append(pod)

    # Résumé
    print(f"✅Running pods: {len(running_pods)}")
    print(f"💥Pending pods: {len(pending_pods)}")
    print(f"❌Failed/Other pods: {len(failed_pods)}")

    if verbose:
        print("")
        for pod in pending_pods + failed_pods:
            print(f"{Fore.CYAN}[{pod.status.phase}] {pod.metadata.namespace}/{pod.metadata.name}")

            container_statuses = pod.status.container_statuses or []
            for cs in container_statuses:
                name = cs.name
                state = cs.state
                reason = "Unknown"

                if state.waiting:
                    reason = state.waiting.reason or "Waiting"
                elif state.terminated:
                    reason = state.terminated.reason or "Terminated"
                elif state.running:
                    reason = "Running (not ready?)"

                print(f"  ↳ container: {name}, reason: {Fore.MAGENTA}{reason}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kubernetes cluster check-up")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Affiche plus d'informations"
    )
    args = parser.parse_args()

    check_cluster_health() or exit(0)
    check_pods(verbose=args.verbose)

