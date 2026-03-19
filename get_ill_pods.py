#!/usr/bin/env python3

from kubernetes import client, config
from kubernetes.client.rest import ApiException
import argparse
import sys
import yaml
from datetime import datetime, timezone

try:
    from colorama import init, Fore, Style
    init(strip=False) 
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    class EmptyColor:
        def __getattr__(self, name): return ""
    Fore = Style = EmptyColor()

parser = argparse.ArgumentParser()
parser.add_argument('-U', '--unsecure', default=False, action='store_true', help='Allow destruction of system pods')
parser.add_argument('-R', '--report', default=False, action='store_true', help='Display debug info on stderr')
args = parser.parse_args()

try:
    config.load_kube_config()
    v1 = client.CoreV1Api()
    all_pods = v1.list_pod_for_all_namespaces().items
except Exception as e:
    print(f"{Fore.RED}Erreur connexion Kube: {e}{Style.RESET_ALL}", file=sys.stderr)
    sys.exit(1)

protected_namespaces = ["kube-system"]

def print_err(text, color=Fore.WHITE):
    """Affiche sur stderr avec la couleur choisie."""
    print(f"{color}{text}{Style.RESET_ALL}", file=sys.stderr)

def get_pod_details(pod):
    """Extrait les infos de status essentielles (façon kubectl describe)."""
    status = pod.status
    details = {
        "Status": status.phase,
        "Conditions": [{c.type: c.status} for c in (status.conditions or [])],
        "Containers": []
    }
    for cs in (status.container_statuses or []):
        state = "Running"
        reason = ""
        if cs.state.waiting:
            state, reason = "Waiting", cs.state.waiting.reason
        elif cs.state.terminated:
            state, reason = f"Terminated({cs.state.terminated.exit_code})", cs.state.terminated.reason
        
        details["Containers"].append({
            "Name": cs.name,
            "State": state,
            "Reason": reason,
            "Restarts": cs.restart_count
        })
    return yaml.dump(details, default_flow_style=False).strip()

def do_report(ns, podname, pod_obj):
    """Génère le rapport de diagnostic sur stderr sans bannières inutiles."""
    print_err(f">>> Describe pod", color=Fore.CYAN + Style.BRIGHT)
    print_err(get_pod_details(pod_obj))

    print_err(f">> Logs", color=Fore.CYAN + Style.BRIGHT)
    try:
        logs = v1.read_namespaced_pod_log(name=podname, namespace=ns, tail_lines=10)
        print_err(logs if logs else "(vides)")
    except ApiException:
        pass

    print_err(f">> Events", color=Fore.CYAN + Style.BRIGHT)
    try:
        events = v1.list_namespaced_event(namespace=ns, field_selector=f"involvedObject.name={podname}")
        if events.items:
            # Date plancher pour éviter le bug de comparaison None vs datetime
            epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
            
            # Tri sécurisé : on prend last_timestamp, sinon first, sinon epoch
            sorted_events = sorted(
                events.items, 
                key=lambda x: x.last_timestamp or x.first_timestamp or epoch
            )
            
            for e in sorted_events[-3:]:
                print_err(f"[{e.reason}] {e.message}")
    except ApiException:
        pass

if __name__ == "__main__":
    for pod in all_pods:
        ns = pod.metadata.namespace
        name = pod.metadata.name
        reason = pod.status.phase
    
        if pod.status.container_statuses:
            for cs in pod.status.container_statuses:
                if cs.state.waiting: 
                    reason = cs.state.waiting.reason
                    break
                elif cs.state.terminated: 
                    reason = cs.state.terminated.reason
                    break
    
        if reason not in ["Running", "Completed", "Succeeded"]:
            is_protected = ns in protected_namespaces
            
            cmd = f"kubectl delete -n {ns} pod {name}"
            if not args.unsecure and is_protected:
                print(f"# {cmd}")
            else:
                print(cmd)
    
            if args.report and (args.unsecure or not is_protected):
                print()
                do_report(ns, name, pod)
                print()
