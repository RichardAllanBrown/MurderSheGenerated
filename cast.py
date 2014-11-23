import random
from pprint import pprint

import graph
import relationships as rship
from relationships import relType

class cast(graph.graph):
    """ Network of relationships between characters """
    def __init__(self):
        graph.graph.__init__(self)
        self.allRelationships = list()
        self.plotFamilies = list()

    def addCharacter(self, c):
        self.addVertex(c)

    def createRelationship(self, charA, charB, relType = None):
        # Don't add relationship if already related
        for edge in self.edges[charA]:
            if edge[0] == charB:
                return
        # Create relationship object
        rel = rship.relationship(charA, charB, relType)
        self.allRelationships.append(rel)
        self.addRelationship(charA, charB, rel)

    def addRelationship(self, charA, charB, rel):
        self.edges[charA].append((charB, rel))
        self.edges[charB].append((charA, rel))

    def removeDirectedRelationship(self, charA, charB):
        """ Removes v2 from v1 edge list """
        for to in self.edges[charA]:
            if to[0] == charB:
                self.edges[charA].remove(to)

    def removeReciprocalRelationship(self, charA, charB):
        self.removeDirectedRelationship(charA, charB)
        self.removeDirectedRelationship(charB, charA)

    def removeRandomRelationship(self):
        if not self.edges:
            print("ERROR: No relationships to be removed")
            return
        charA = None
        charB = None
        while charB == None:
            charA = random.choice(list(self.edges.keys()))
            if self.edges[charA]:
                charB = random.choice(self.edges[charA])[0]
        self.removeReciprocalRelationship(charA, charB)

    def totallyConnect(self):
        """ Create a relationship between every pair of vertices """
        for charA in self.edges:
            for charB in self.edges:
                if charA != charB:
                    # Confirm relationship doesn't already exist
                    exists = False
                    for rel in self.edges[charA]:
                        if rel[0] == charB:
                            exists = True
                            break
                    if not exists:
                        self.createRelationship(charA, charB)

    def gatherConnectedRelTypeMembers(self, charA, desiredType, members):
        members.append(charA)
        for rel in self.edges[charA]:
            if rel[1].type == desiredType and not rel[0] in members:
                # Extend search to matching character's relationships
                self.gatherConnectedRelTypeMembers(rel[0], desiredType, members)
        return members

    def createFamilialRelationships(self, family):
        if family == None:
            print("ERROR: No family supplied to createFamilialRelationships")
            return
        for charA in family.members:
            for charB in family.members:
                if charA == charB:
                    continue
                # Create relationship
                self.createRelationship(charA, charB, rship.relType.familial)

    def generatePlotFamilies(self, rangeFamilies, rangeFamilyMembers):
        """
        Creates parameterised number of families with parameterised numbers of members by creating family
        entities and selecting members.
        :param rangeFamilies: tuple of min, max number of familes desired
        :param rangeFamilyMembers: tuple of min, max number of members of each family
        :return: None
        """
        candidates = self.getFamilyCandidates()
        numFamilies = random.randint(*rangeFamilies)
        # If player count can't support 2-member families at min family count, reduce numFamilies so it can
        if len(candidates) < numFamilies*2:
            print("WARNING: Player count cannot sustain num families. Reducing num family min/max.")
            numFamilies = random.randint(0, int(len(candidates)/2))
        print("- Families (" + str(numFamilies) + ") -")
        if len(candidates) < rangeFamilyMembers[0]*numFamilies:
            print("ERROR: Less family candidates than min member count allows")
        # Create desired number of multi-member plot families
        for n in range(numFamilies):
            remainingFamilies = numFamilies - n
            if len(candidates) < remainingFamilies * 2:
                print("ERROR: Less family candidates than desired families")
                break
            newFamily = rship.family()
            # Cap possible family members so to-be created families have minimum of two members each
            numSpareCandidates = len(candidates) - (remainingFamilies * 2)
            # Used desired min/max, unless there aren't enough
            minAdditionalMembers = min(rangeFamilyMembers[0]-2, numSpareCandidates)
            maxAdditionalMembers = min(rangeFamilyMembers[1]-2, numSpareCandidates)
            numMembers = 2 + random.randint(minAdditionalMembers, maxAdditionalMembers)
            print("New Family: " + newFamily.surname + "(" + str(numMembers) + ")")
            for m in range(numMembers):
                member = candidates.pop()
                member.setFamily(newFamily)
                print(member.getFullName())
            # Create familial relationships
            self.createFamilialRelationships(newFamily)

    def generateNonPlotFamilies(self):
        """ Create single-member non-plot families """
        candidates = self.getFamilyCandidates()
        for charA in candidates:
            newFamily = rship.family()
            charA.family = newFamily

    def getFamilyCandidates(self):
        """ Returns list of all characters eligible to be added to a family """
        candidates = list()
        for charA in self.edges.keys():
            if charA.family == None:
                candidates.append(charA)
        return candidates

    def generateRomanticEntanglements(self, numRomances):
        """ Creates romantic relationships between characters """
        for n in range(numRomances):
            # Perform number of attempts, to attempt to guarantee numRomances
            numAttempts = 10
            for attemptNumber in range(numAttempts):
                charA = random.choice(list(self.edges.keys()))
                candidates = self.getRomanceCandidates(charA)
                if candidates:
                    # Create relationship
                    self.createRelationship(charA, random.choice(candidates), rship.relType.romantic)
                    break
                else:
                    continue

    def getRomanceCandidates(self, charA):
        candidates = list(self.edges.keys())
        # Avoid self-romance
        candidates.remove(charA)
        for charB in candidates:
            remove = False
            # Avoid duplicate romances
            if charA in self.edges:
                for edge in self.edges[charA]:
                    if edge[0] == charB and edge[1].type == rship.relType.romantic:
                        remove = True
                        break
            if remove:
                candidates.remove(charB)
        return candidates
