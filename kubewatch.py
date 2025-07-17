#!/usr/bin/env python3

#!/usr/bin/env python3

from kubernetes import config, client, watch
from kubernetes.client.exceptions import ApiException
from colorama import Fore, Style, init
import argparse
import sys

init(autoreset=True)

# 🎨 Couleurs d'événements
EVENT_COLORS = {
    "ADDED": Fore.GREEN,
    "MODIFIED": Fore.YELLOW,
    "DELETED": Fore.RED,
}

# 🔁 Ressources supportées
RESOURCE_MAP = {
    "namespace": lambda: client.CoreV1Api().list_namespace,
    "pod": lambda: client.CoreV1Api().list_pod_for_all_namespaces,
    "node": lambda: client.CoreV1Api().list_node,
    "svc": lambda: client.CoreV1Api().list_service_for_all_namespaces,
    "deployment": lambda: client.AppsV1Api().list_deployment_for_all_namespaces,
}

def list_resources():
    print("Ressources disponibles :")
    for r in RESOURCE_MAP:
        print(f" - {r}")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Kubernetes Watcher avec couleur")
    parser.add_argument(
        "resource",
        nargs="?",
        default="pod",
        choices=RESOURCE_MAP.keys(),
        help="Type de ressource à watcher (défaut: pod)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Lister les ressources disponibles et quitter"
    )
    args = parser.parse_args()

    if args.list:
        list_resources()

    config.load_kube_config()
    watcher = watch.Watch()

    try:
        lister = RESOURCE_MAP[args.resource]()
        for event in watcher.stream(lister, timeout_seconds=0):
            obj = event.get("object")
            ev_type = event.get("type", "UNKNOWN")
            color = EVENT_COLORS.get(ev_type, Fore.MAGENTA)

            name = getattr(obj.metadata, "name", "???")
            namespace = getattr(obj.metadata, "namespace", None)
            ns_prefix = f"{namespace}/" if namespace else ""

            print(f"{color}{ev_type:<10}{Style.RESET_ALL} {ns_prefix}{name}")
    except KeyboardInterrupt:
        print(f"{Fore.WHITE}\n[!] Watch interrompu par l'utilisateur.")
    except ApiException as e:
        print(f"{Fore.RED}[API ERROR] {e}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {e}")

if __name__ == "__main__":
    main()

