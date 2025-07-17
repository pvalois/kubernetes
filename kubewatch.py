#!/usr/bin/env python3

from kubernetes import config, client, watch
from kubernetes.client.exceptions import ApiException
from colorama import Fore, Style, init
import argparse
import sys
import threading
from datetime import datetime

init(autoreset=True)

print_lock = threading.Lock()

EVENT_COLORS = {
    "ADDED": Fore.GREEN,
    "MODIFIED": Fore.YELLOW,
    "DELETED": Fore.RED,
}

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

def watch_resource(name, list_func):
    watcher = watch.Watch()
    try:
        for event in watcher.stream(list_func(), timeout_seconds=0):
            obj = event.get("object")
            ev_type = event.get("type", "UNKNOWN")
            color = EVENT_COLORS.get(ev_type, Fore.MAGENTA)

            metadata = getattr(obj, "metadata", None)
            if not metadata:
                continue

            obj_name = metadata.name
            namespace = getattr(metadata, "namespace", None)
            ns_prefix = f"{namespace}/" if namespace else ""

            with print_lock:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"{Fore.CYAN}{now}   {color}{name.upper():<12} {ev_type:<10}{Style.RESET_ALL} {ns_prefix}{obj_name}")
    except ApiException as e:
        with print_lock:
            print(f"{Fore.RED}[API ERROR] {e}")
    except Exception as e:
        with print_lock:
            print(f"{Fore.RED}[ERROR] {e}")

def main():
    parser = argparse.ArgumentParser(description="Multi-watcher Kubernetes")
    parser.add_argument(
        "resources",
        nargs="*",
        type=str,
        help="Ressources à watcher (par défaut: namespace)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Lister les ressources disponibles"
    )
    args = parser.parse_args()

    if args.list:
        list_resources()

    if not args.resources:
        args.resources = ["namespace"]

    invalid = [r for r in args.resources if r not in RESOURCE_MAP]
    if invalid:
        with print_lock:
            print(f"{Fore.RED}Ressources inconnues: {', '.join(invalid)}")
        list_resources()

    config.load_kube_config()

    threads = []
    for res in args.resources:
        t = threading.Thread(target=watch_resource, args=(res, RESOURCE_MAP[res]))
        t.daemon = True
        t.start()
        threads.append(t)

    try:
        while True:
            for t in threads:
                t.join(timeout=1)
    except KeyboardInterrupt:
        with print_lock:
            print(f"{Fore.WHITE}\n[!] Terminé par l'utilisateur.")

if __name__ == "__main__":
    main()

