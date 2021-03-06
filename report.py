#!/usr/bin/python
import yaml
from collections import defaultdict
from pprint import pprint as p

README_STUB = """
Grand Canyon Space Estimator
============================

How are we doing on space on our rafts?  Here are some little scripts to
estimate how much space we'll have on the grand trip. Edit
the YAML files to change assumptions, and then run `python gear.py` to generate
a report.

Here are the most recent results:
"""

class GearEstimator(object):
    def __init__(self, stowage, gear):
        self.stowage = stowage
        self.gear = gear

    def report_craft(self):
        print self.generate_craft_report()

    def generate_craft_report(self):
        report = "Craft:\n"
        for name, desc in self.craft().iteritems():
            report += '  - %s %s, each with:\n' % (
                    self.stowage['fleet'][name], name)
            for space, count in desc.iteritems():
                report += "    - %s %s\n" % (count, space)
        return report

    def report_stowage_levels(self):
        cont = self.containers()
        row_format = "{:>15}" * 3
        print "Gear Stowage Levels:"
        print row_format.format('Container', 'Available', 'Needed')
        for container, levels in self.containers().iteritems():
            print row_format.format(container, levels['available'], levels['needed'])

    def update_readme(self):
        stowageReport = '<table><tr><td>Container</td><td>Available</td><td>Needed</td></tr>'
        for container, levels in self.containers().iteritems():
            stowageReport += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (container, levels['available'], levels['needed'])
        stowageReport += '</table>'
        
        with open('README.md', 'w') as readmeFile:
            readmeFile.write('\n'.join([README_STUB, self.generate_craft_report(), stowageReport])) 
        
    def craft(self):
        return self.stowage.get('craft')

    def containers(self):
        containersAvailable = self.containers_available()
        containersNeeded = self.gear_space_requirements()
        containers = {}
        for container in containersNeeded.keys():
            containers[container] = {
                'available': containersAvailable[container],
                'needed': containersNeeded[container]
            }
        return containers
                
    def containers_available(self):
        containersAvailable = defaultdict(lambda: 0)
        for name, spaces in self.craft().iteritems():
            numInFleet = self.stowage['fleet'][name]
            convertedSpaces = self.convert_craft_space_to_container(spaces)
            for cont, count in convertedSpaces.iteritems():
                containersAvailable[cont] += count * numInFleet
        return dict(containersAvailable)

    def convert_craft_space_to_container(self, spaces):
        conversions = self.stowage['capacity']
        result = defaultdict(lambda:0)
        for space, count in spaces.iteritems():
            conversion = conversions.get(space)
            if conversion:
                result[conversion.keys()[0]] += conversion.values()[0] * count
            else:
                result[space] += count
        return dict(result)
            
    def gear_space_requirements(self):
        "Return a dict of container and how much is needed by gear"
        containersRequired = defaultdict(lambda:0)
        for item, reqs in self.gear['gearList'].iteritems():
            for container, spaceNeeded in reqs['stow'].iteritems():
                containersRequired[container] += reqs.get('count', 1) * spaceNeeded
        return dict(containersRequired)

if __name__ == '__main__':
    with open('stowage.yaml') as stowageFile:
        stowage = yaml.load(stowageFile.read())
    with open('gear.yaml') as gearFile:
        gear = yaml.load(gearFile.read())
    ge = GearEstimator(stowage, gear)
    ge.report_craft()
    ge.report_stowage_levels()
    ge.update_readme()
        
