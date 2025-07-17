#!/usr/bin/env python3

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from colorama import Fore, Back, Style, init
import argparse

init(autoreset=True)

def get_container_logs(v1, pod, container_name):
    try:
        logs = v1.read_namespaced_pod_log(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            container=container_name,
            tail_lines=10,
            timestamps=True
        )
        return logs.strip().splitlines()
    except ApiException as e:
        return [f"{Fore.RED}Erreur lors de la récupération des logs: {e.reason}"]

def get_pod_events(v1_events, pod):
    try:
        field_selector = f"involvedObject.name={pod.metadata.name},involvedObject.namespace={pod.metadata.namespace}"
        events = v1_events.list_event_for_all_namespaces(field_selector=field_selector).items
        return sorted(events, key=lambda e: e.last_timestamp or e.event_time or e.first_timestamp or 0, reverse=True)
    except ApiException as e:
        return []

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

def check_pods(verbose):
    print("")
    config.load_kube_config()
    v1 = client.CoreV1Api()
    v1_events = client.CoreV1Api()
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
    print(f"✅ Running pods: {len(running_pods)}")
    print(f"💥 Pending pods: {len(pending_pods)}")
    print(f"❌ Failed/Other pods: {len(failed_pods)}")

    if verbose>=1:
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

                if verbose>=2:
                    logs = get_container_logs(v1, pod, name)
                    if logs:
                        print(f"{Fore.BLACK}{Back.YELLOW}    ⇢ Derniers logs :  ")
                        for line in logs:
                            print(f"{Style.DIM}       {line}")


            if verbose>=2:
                events = get_pod_events(v1_events, pod)
                if events:
                    print(f"{Fore.BLACK}{Back.LIGHTBLUE_EX}    ⇢ Événements récents :  ")
                    for e in events[:5]:
                        print(f"{Style.DIM}       [{e.type}] {e.reason}: {e.message} ({e.last_timestamp or e.event_time})")

            if verbose>=2: 
                print ("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kubernetes cluster check-up")
    parser.add_argument(
        "-v", "--verbose",
        action='count',
        default=0,
        help='Augmente le niveau de verbosité (peut être répété, ex: -v, -vv, -vvv)'
    )

    args = parser.parse_args()

    check_cluster_health() or exit(0)
    check_pods(args.verbose)

