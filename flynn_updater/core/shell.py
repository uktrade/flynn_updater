import subprocess
import json
from django.conf import settings
from celery.utils.log import logger


def execute(cmd, shell=True):
    run = None
    try:
        run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output = run.stdout.read().rstrip().split("\n")
    except subprocess.CalledProcessError:
        error = run.stderr.read().rstrip().split("\n")
        logger.error(error)
        return error
    return output


def flynn_cli_init():
    install = 'L=%s && curl -sSL -A "`uname -sp`" https://dl.flynn.io/cli | zcat >$L && chmod +x $L' % settings.FLYNN_PATH
    setup = '%s cluster add -p %s default %s %s' % (settings.FLYNN_PATH, settings.FLYNN_PIN, settings.AWS_ROUTE53_DOMAIN, settings.FLYNN_PIN)
    if not execute('ls %s' % settings.FLYNN_PATH)[0]:
        execute(install)
        execute(setup)


def flynn_cli_update():
    execute('%s update' % settings.FLYNN_PATH)


def get_apps():
    return execute('%s apps | grep -v NAME | awk \'{print $2}\'' % settings.FLYNN_PATH)


def get_app_release(app):
    return execute('%s -a %s release -q' % (settings.FLYNN_PATH, app))


def get_app_current_release(app):
    return json.loads(execute('%s -a %s release show --json' % (settings.FLYNN_PATH, app))[0])['id']


def delete_app_release(app, release):
    return execute('%s -a %s release delete -y %s' % (settings.FLYNN_PATH, app, release))


def get_app_env(app):
    return execute('%s -a %s env' % (settings.FLYNN_PATH, app))


def set_app_env(app, envs: list):
    envars = ' \\'.join(envs)
    return execute('%s -a %s env set %s' % (settings.FLYNN_PATH, app, envars))
