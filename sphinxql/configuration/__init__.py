import subprocess

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
    return call_process(['indexer', '--all', '--rotate', '--config', indexes_configurator.sphinx_file])


def start(silent_fail=False):
    return call_process(['searchd', '--config', indexes_configurator.sphinx_file], silent_fail)


def stop(silent_fail=False):
    return call_process(['searchd', '--stopwait', '--config', indexes_configurator.sphinx_file], silent_fail)


def restart():
    stop(silent_fail=True)
    start()
