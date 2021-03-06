try:
    from crawler.plugins.file_crawler import crawl_files
    from crawler.icrawl_plugin import IContainerCrawler
    import crawler.dockerutils as dockerutils
    from crawler.namespace import run_as_another_namespace
    import crawler.misc as misc
except ImportError:
    from plugins.file_crawler import crawl_files
    from icrawl_plugin import IContainerCrawler
    import dockerutils
    from namespace import run_as_another_namespace
    import misc
import logging

logger = logging.getLogger('crawlutils')


class FileContainerCrawler(IContainerCrawler):

    def get_feature(self):
        return 'file'

    def crawl(
            self,
            container_id=None,
            avoid_setns=False,
            root_dir='/',
            exclude_dirs=[
                '/boot',
                '/dev',
                '/proc',
                '/sys',
                '/mnt',
                '/tmp',
                '/var/cache',
                '/usr/share/man',
                '/usr/share/doc',
                '/usr/share/mime'],
            **kwargs):
        inspect = dockerutils.exec_dockerinspect(container_id)
        state = inspect['State']
        pid = str(state['Pid'])
        logger.debug('Crawling file for container %s' % container_id)

        if avoid_setns:
            rootfs_dir = dockerutils.get_docker_container_rootfs_path(
                container_id)
            exclude_dirs = [misc.join_abs_paths(rootfs_dir, d)
                            for d in exclude_dirs]
            return crawl_files(
                root_dir=misc.join_abs_paths(rootfs_dir, root_dir),
                exclude_dirs=exclude_dirs,
                root_dir_alias=root_dir)
        else:  # in all other cases, including wrong mode set
            return run_as_another_namespace(pid,
                                            ['mnt'],
                                            crawl_files,
                                            root_dir,
                                            exclude_dirs,
                                            None)
