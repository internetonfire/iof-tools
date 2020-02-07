#!/usr/bin/env python
import time
import datetime as dt
from argparse import ArgumentParser
from subprocess import Popen, PIPE
from os.path import isfile


OMNI = "omni -V 3 -c ./omni_config -p {{}} {command}"
STATUS = OMNI.format(command="status -a {} {}")
CREATE_SLICE = OMNI.format(command="createslice {}")
RENEW_SLICE = OMNI.format(command="renewslice {} {}")
ALLOCATE = OMNI.format(command="allocate {} {} {}")
PROVISION = OMNI.format(command="provision {} {}")
START = OMNI.format(command="performoperationalaction {} {} geni_start")
DELETE = OMNI.format(command="delete {} {}")


class ProcessOutput:
    def __init__(self, out, err):
        self.stdout = out.decode('utf-8')
        self.stderr = err.decode('utf-8')


def local(command, dry_run=False):
    if dry_run:
        print(command + "\n")
        return ProcessOutput(b"", b"")
    proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = proc.communicate()
    return ProcessOutput(stdout, stderr)


def create_slice(testbed, exp_name, duration, project, dry_run):
    args = "-V3 -a {}".format(testbed)


def reserve(testbed, exp_name, duration, rspec, project, dry_run):
    args = "-a {}".format(testbed)

    end = dt.datetime.utcnow() + dt.timedelta(hours=int(duration))
    end = end.strftime("%Y%m%dT%H:%M:%S%Z")
    checkcmd = STATUS.format(project, testbed, exp_name)
    cmd_result = local(checkcmd, dry_run)
    if not dry_run and cmd_result.stderr.find("geni_ready") != -1:
        print("Slice already reserved. Resources ready")
        return True

    # Reserve and start
    print("Creating slice and allocating experiment")
    local(CREATE_SLICE.format(project, exp_name), dry_run)
    local(RENEW_SLICE.format(project, exp_name, end), dry_run)
    alloc = local(ALLOCATE.format(project, args, exp_name, rspec), dry_run)

    if not dry_run and alloc.stderr.find("Error") != -1:
        print(alloc.stderr)
        print("Resources are not available")
        return False

    local(PROVISION.format(project, args, exp_name), dry_run)
    local(START.format(project, args, exp_name), dry_run)

    # Wait till reserved
    tic = time.time()
    n = 1
    cmd_result = local(checkcmd, dry_run)
    while not dry_run and cmd_result.stderr.find("geni_ready") == -1:
        if cmd_result.stderr.find("geni_failed") != -1:
            print("One node failed to boot. Output:")
            print(cmd_result.stderr)
            return False
        print("Waiting for nodes to perform boot... Attempt {}".format(n))
        n += 1
        time.sleep(10)
        cmd_result = local(checkcmd)
    toc = time.time() - tic
    print("Resources ready." + " Took: {}".format(toc))
    return True


def release(testbed, exp_name, project, dry_run):
    args = "-V3 -a {}".format(testbed)
    checkcmd = STATUS.format(project, testbed, exp_name)
    if not dry_run and local(checkcmd).stderr.find("geni_ready") == -1 and \
       local(checkcmd).stderr.find("geni_provisioned") == -1:
        print("Experiment %s not found" % exp_name)
        return False

    # release the slice
    print("Releasing resources")
    local(DELETE.format(project, args, exp_name), dry_run)
    return True


def main():
    parser = ArgumentParser()
    parser.add_argument("-t", "--testbed", dest="testbeds",
                        default="twist", action="store", metavar="TESTBED",
                        help="Comma separated list of testbeds on which the "
                             "resources should be reserved. If the rspec file "
                             "includes nodes from multiple testbeds, then all "
                             "of them should be listed here "
                             "[default: %(default)s]")
    parser.add_argument("-d", "--duration", dest="duration", type=int,
                        default=3, action="store", metavar="DURATION",
                        help="Duration in hours [default: %(default)s]")
    parser.add_argument("-n", "--name", dest="name", default="experiment",
                        action="store", metavar="SLICENAME",
                        help="Name of the slice [default: %(default)s]")
    parser.add_argument("-f", "--rspec", dest="rspec", default="test.rspec",
                        action="store", metavar="FILENAME",
                        help=".rspec file to use [default: %(default)s]")
    parser.add_argument("-p", "--project", dest="project",
                        default="internetonfire", action="store",
                        help="project the resources should be reserved for "
                             "[default: %(" "default)s]")
    parser.add_argument("-r", "--release", dest="delete", action="store_true",
                        help="Deletes an existing experiment. If not set, "
                             "the application creates a new experiment",
                        default=False)
    parser.add_argument("-x", "--dry-run", action="store_true", default=False,
                        dest="dry_run",
                        help="Setting this flags causes the script to output "
                             "the list of omni commands that should be run "
                             "without actually executing them "
                             "[default: %(default)s]")

    args = parser.parse_args()
    testbed = args.testbeds
    duration = args.duration
    name = args.name
    rspec = args.rspec
    delete = args.delete
    project = args.project
    dry_run = args.dry_run

    if not isfile(rspec):
        print("File %s not found" % rspec)
        return False

    if not delete:
        return reserve(testbed, name, duration, rspec, project, dry_run)
    else:
        return release(testbed, name, project, dry_run)


if __name__ == "__main__":
    main()
