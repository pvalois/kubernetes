#!/usr/bin/env python3

import argparse, yaml, subprocess, time, os

def generate_vm_yaml(args):
    vm = {
        "apiVersion": "kubevirt.io/v1",
        "kind": "VirtualMachine",
        "metadata": {"name": args.name, "namespace": args.namespace},
        "spec": {
            "running": False,
            "template": {
                "metadata": {"labels": {"kubevirt.io/domain": args.name}},
                "spec": {
                    "domain": {
                        "cpu": {"cores": args.cpu},
                        "resources": {"requests": {"memory": args.ram}},
                        "devices": {
                            "disks": [
                                {"name": "containerdisk", "disk": {"bus": "virtio"}}
                            ]
                        }
                    },
                    "volumes": [
                        {
                            "name": "containerdisk",
                            "containerDisk": {
                                "image": "kubevirt/cirros-container-disk-demo"
                            }
                        }
                    ]
                }
            }
        }
    }

    output_file = args.output or f"{args.name}.yaml"
    with open(output_file, "w") as f:
        yaml.dump(vm, f)
    print(f"✅ VM plan saved to {output_file}")

def apply_vm(plan):
    subprocess.run(["oc", "apply", "-f", plan], check=True)

def start_vm(plan):
    with open(plan) as f:
        vm = yaml.safe_load(f)
    name = vm["metadata"]["name"]
    namespace = vm["metadata"]["namespace"]
    subprocess.run(["virtctl", "start", name, "-n", namespace], check=True)

def trace_vm(plan):
    with open(plan) as f:
        vm = yaml.safe_load(f)
    name = vm["metadata"]["name"]
    namespace = vm["metadata"]["namespace"]

    print(f"📡 Tracing VM: {name}")
    while True:
        result = subprocess.run(["oc", "get", "vm", name, "-n", namespace,
                                 "-o", "jsonpath={.status.ready}"],
                                 capture_output=True, text=True)
        state = result.stdout.strip()
        print(f"→ Status: {state}")
        if state == "True":
            print("✅ VM is running.")
            break
        elif state == "False":
            print("⏳ VM not ready...")
        else:
            print("⚠️ Unknown state.")
        time.sleep(3)

def show_events(plan):
    with open(plan) as f:
        vm = yaml.safe_load(f)
    name = vm["metadata"]["name"]
    namespace = vm["metadata"]["namespace"]
    subprocess.run(["oc", "get", "events", "-n", namespace,
                    "--field-selector", f"involvedObject.name={name}"])

def destroy_vm(plan):
    subprocess.run(["oc", "delete", "-f", plan], check=True)

# --- Main CLI Parser ---
def main():
    parser = argparse.ArgumentParser(description="KubeVirt VM Generator CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate
    gen = subparsers.add_parser("generate", help="Generate VM YAML plan")
    gen.add_argument("--name", required=True)
    gen.add_argument("--cpu", type=int, default=1)
    gen.add_argument("--ram", default="2Gi")
    gen.add_argument("--disk", default="10Gi")  # Not yet dynamically used
    gen.add_argument("--namespace", default="default")
    gen.add_argument("-o", "--output", help="Output file (default: <name>.yaml)")
    gen.set_defaults(func=generate_vm_yaml)

    # apply
    apply = subparsers.add_parser("apply", help="Apply VM plan")
    apply.add_argument("plan")
    apply.set_defaults(func=lambda args: apply_vm(args.plan))

    # start
    start = subparsers.add_parser("start", help="Start the VM")
    start.add_argument("plan")
    start.set_defaults(func=lambda args: start_vm(args.plan))

    # trace
    trace = subparsers.add_parser("trace", help="Trace VM status until ready")
    trace.add_argument("plan")
    trace.set_defaults(func=lambda args: trace_vm(args.plan))

    # events
    events = subparsers.add_parser("events", help="Show VM-related events")
    events.add_argument("plan")
    events.set_defaults(func=lambda args: show_events(args.plan))

    # destroy
    destroy = subparsers.add_parser("destroy", help="Destroy the VM")
    destroy.add_argument("plan")
    destroy.set_defaults(func=lambda args: destroy_vm(args.plan))

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

