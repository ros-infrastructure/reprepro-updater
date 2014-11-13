from reprepro_updater import conf


inc = conf.IncomingFile(['lucid', 'oneiric', 'precise'])
print inc.generate_file_contents()


updates = conf.UpdatesFile(['lucid', 'oneiric', 'precise'], ['amd64', 'i386', 'armel'])
print updates.generate_file_contents('precise', 'amd64')


dist = conf.DistributionsFile(['lucid', 'oneiric', 'precise'], ['amd64', 'i386', 'armel'], 'REPOKEYID', updates )
print dist.generate_file_contents('amd64')
