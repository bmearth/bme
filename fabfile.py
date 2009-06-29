def update():
    local("hg pull && hg update")
    local("touch deploy/bme.wsgi")
