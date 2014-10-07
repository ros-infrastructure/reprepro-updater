from reprepro_updater import conf


inc = conf.IncomingFile(['lucid', 'oneiric', 'precise'])
print inc.generate_file_contents()


inc = conf.UpdatesFile(['fuerte', 'groovy'], ['lucid', 'oneiric', 'precise'], ['amd64', 'i386', 'armel'])
print inc.generate_file_contents()


inc = conf.DistributionsFile(['lucid', 'oneiric', 'precise'], ['amd64', 'i386', 'armel'], ['fuerte', 'groovy'] )
print inc.generate_file_contents('groovy', 'precise', 'amd64')
