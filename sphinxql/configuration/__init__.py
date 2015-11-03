import subprocess
import time

from .configurators import Configurator

indexes_configurator = Configurator()


def call_process(args, fail_silently=False):
    p = subprocess.Popen(args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()

    out = p.stdout.read().decode('UTF-8')
    if p.returncode != 0 and not fail_silently:
        raise Exception('\n\n' + out)
    return out


def index():
    return call_process(['indexer', '--all', '--config',
                         indexes_configurator.sphinx_file])


def reindex():
    out = call_process(['indexer', '--all', '--rotate', '--config',
                        indexes_configurator.sphinx_file])
    # it is not immediately available; wait a bit
    # see http://sphinxsearch.com/bugs/view.php?id=2350
    time.sleep(0.5)
    return out


def start(silent_fail=False):
    return call_process(['searchd', '--config',
                         indexes_configurator.sphinx_file], silent_fail)


def stop(silent_fail=False):
    return call_process(['searchd', '--stopwait', '--config',
                         indexes_configurator.sphinx_file], silent_fail)


def statistics():
    return call_process(['indextool', '--dumpheader', 'query_authorindex',
                         '--config', indexes_configurator.sphinx_file],
                        fail_silently=True)


def restart():
    stop(silent_fail=True)
    start()
