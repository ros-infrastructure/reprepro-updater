from reprepro_updater import conf


inc = conf.IncomingFile(['lucid', 'oneiric', 'precise'])
print inc.generate_file_contents()


inc = conf.UpdatesFile(['fuerte', 'groovy'], ['lucid', 'oneiric', 'precise'], ['amd64', 'i386', 'armel'], 'B01FA116', 'http://50.28.27.175/repos/building' )
print inc.generate_file_contents()


inc = conf.DistributionsFile(['lucid', 'oneiric', 'precise'], ['amd64', 'i386', 'armel'], ['fuerte', 'groovy'] )
print inc.generate_file_contents('groovy', 'precise', 'amd64')
