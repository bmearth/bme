config.fab_hosts = ['ariel@earthdev.burningman.com']

def push():
    local("hg push")
    deploy()

def deploy():
    sudo("su - bme")
    run("cd /home/bme/src/bme && hg pull && hg update")
    reload()
    
def reload():
    run("touch /home/bme/src/bme/deploy/bme.wsgi")
