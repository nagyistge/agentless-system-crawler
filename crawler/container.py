#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import logging
import psutil
import misc
import namespace

logger = logging.getLogger('crawlutils')


def list_raw_containers(user_list='ALL'):
    """
    A running container is defined as a group of processes with the
    `pid` namespace different to the `init` process `pid` namespace.
    """
    init_ns = namespace.get_pid_namespace(1)
    for p in psutil.process_iter():
        pid = (p.pid() if hasattr(p.pid, '__call__') else p.pid)
        if pid == 1 or pid == '1':

            # don't confuse the init process as a container

            continue
        if user_list not in ['ALL', 'all', 'All']:
            if str(pid) not in user_list:

                # skip containers not in the list

                continue
        if misc.process_is_crawler(pid):

            # don't confuse the crawler process with a container

            continue
        curr_ns = namespace.get_pid_namespace(pid)
        if not curr_ns:

            # invalid container

            continue
        if curr_ns == init_ns:
            continue
        yield Container(pid, curr_ns)


class Container(object):

    """
    This class abstracts a running Linux container.
    """

    def __init__(
        self,
        pid,
        container_opts={},
        process_namespace=None,
    ):
        self.pid = str(pid)
        self.short_id = str(hash(pid))
        self.long_id = str(hash(pid))
        self.name = str(pid)
        self.namespace = str(pid)
        self.image = None
        self.root_fs = None
        self.log_prefix = None
        self.log_file_list = None
        self.process_namespace = (process_namespace or
                                  namespace.get_pid_namespace(pid))

        # XXX(kollerr): when running in alchemy environment, non-alchemy
        # containres should be ignored

    def __eq__(self, other):
        """
        A container is equal to another if they have the same PID
        """
        return self.pid == other.pid

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_docker_container(self):
        return False

    def __str__(self):
        return str(self.__dict__)

    def get_memory_cgroup_path(self, node='memory.stat'):
        raise NotImplementedError()

    def get_cpu_cgroup_path(self, node='cpuacct.usage'):
        raise NotImplementedError()

    def is_running(self):
        return os.path.exists('/proc/' + self.pid)

    def link_logfiles(self, options={}):
        raise NotImplementedError()

    def unlink_logfiles(self, options={}):
        raise NotImplementedError()
