from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, CollisionHandlerEvent, Vec3
import DefensePaths as defensePaths
import SpaceJamClasses as spaceJamClasses
from CollideObjectBase import PlacedObject
import re                                                                                       #regex module import for string editing
from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect

class SpaceJam(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.SetupScene()
        
        
        self.pusher.addCollider(self.Ship.collisionNode, self.Ship.modelNode)                                                       #Add collider to our 'from' object and pss it the geometry of our model
        self.cTrav.addCollider(self.Ship.collisionNode, self.pusher)                                                                #Allow that collider to be interacted with by others in scene
        self.cTrav.showCollisions(self.render)                                                                                      #See when collisions happen

        fullCycle = 60
        for j in range(fullCycle):
            spaceJamClasses.Drone.droneCount += 1
            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)

            self.DrawCloudDefense(self.Planet1, nickName)
            self.DrawBaseballSeams(self.Planet4, nickName, j, fullCycle)
            
        defensePaths.CircleXY(self)
        defensePaths.CircleXZ(self)
        defensePaths.CircleYZ(self)
        self.SetCamera()
        

    def DrawCloudDefense(self, centralObject, droneName):
        unitVec = defensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * 500 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/Drones/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/Drones/DroneDefender/octotoad1_auv.png", position, 10)

    def DrawBaseballSeams(self, centralObject, droneName, step, numSeams, radius = 1):
        unitVec = defensePaths.BaseballSeams(step, numSeams, B = 0.4)
        unitVec.normalize()
        position = unitVec * radius * 250 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/Drones/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/Drones/DroneDefender/octotoad1_auv.png", position, 5)

    def SetCamera(self):
        self.disableMouse()
        self.camera.reparentTo(self.Ship.modelNode)
        self.camera.setFluidPos(0, 1, 0)

    def SetupScene(self):
        self.cTrav = CollisionTraverser()                                                                                           #Goes through every collidable object in scene
        base.cTrav = self.cTrav
        self.cTrav.traverse(self.render)                                                                                            #Traverse through everything in render node
        self.pusher = CollisionHandlerPusher()                                                                                      #Pusher for when 2 objects with colliders touch
        self.handler = CollisionHandlerEvent()
        self.handler.addInPattern('into')
        self.accept('into', self.HandleInto)
            #Universe
        self.Universe = spaceJamClasses.Universe(self.loader, "./Assets/Universe/Universe.x", self.render, 'Universe', "./Assets/Universe/starfield-in-blue.jpg", (0, 0, 0), 15000)

            #Spaceship
        self.Ship = spaceJamClasses.Spaceship(self.loader,"./Assets/Spaceships/Dumbledore/Dumbledore.egg", self.render, 'Ship', (0, 0, 0), 10, self.taskMgr, self.render, self.accept, self.cTrav, self.handler)

            #Planets
        self.Planet1 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/redPlanet.x", self.render, 'Planet1', "./Assets/Planets/Planet1.jpg", (150, 5000, 67), 350)
        self.Planet2 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/redPlanet.x", self.render, 'Planet2', "./Assets/Planets/Planet2.jpg", (5000, 1000, 183), 600)
        self.Planet3 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/redPlanet.x", self.render, 'Planet3', "./Assets/Planets/Planet3.png", (500, 9060, 23), 200)
        self.Planet4 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/redPlanet.x", self.render, 'Planet4', "./Assets/Planets/Planet4.png", (1000, 1833, 1000), 350)
        self.Planet5 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/redPlanet.x", self.render, 'Planet5', "./Assets/Planets/Planet5.png", (183, 500, 1500), 300)
        self.Planet6 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/redPlanet.x", self.render, 'Planet6', "./Assets/Planets/Planet6.png", (2000, 2000, 2300), 400)

            #Space Station
        self.Station = spaceJamClasses.SpaceStation(self.loader, "./Assets/SpaceStation/SpaceStation1B/spaceStation.egg", self.render, 'Station', (-1000, -1000, -1000), 40)

        self.Sentinal1 = spaceJamClasses.Orbiter(self.loader, self.task_mgr, "./Assets/Drones/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0,
                                                 "./Assets/Drones/DroneDefender/octotoad1_auv.png", self.Planet5, 900, "MLB", self.Ship)
        self.Sentinal2 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/Drones/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0,
                                                 "./Assets/Drones/DroneDefender/octotoad1_auv.png", self.Planet2, 500, "Cloud", self.Ship)
        
    def HandleInto(self, entry):
        fromNode = entry.getFromNodePath().getName()
        print("fromNode: " + fromNode)
        intoNode = entry.getIntoNodePath().getName()
        print("intoNode: " + intoNode)

        intoPosition = Vec3(entry.getSurfacePoint(self.render))

        tempVar = fromNode.split('_')
        shooter = tempVar[0]
        tempVar = intoNode.split('_')
        tempVar = intoNode.split('_')
        victim = tempVar[0]

        pattern = r'[0-9]'
        strippedString = re.sub(pattern, '', victim)

        if (strippedString == "Drone"):
            print(shooter + ' id DONE.')
            spaceJamClasses.Missile.Intervals[shooter].finish()
            print(victim, ' hit at ', intoPosition)
            self.DroneDestroy(victim, intoPosition)
        else:
            spaceJamClasses.Missile.Intervals[shooter].finish()

    def SetParticles(self):
        base.enableParticles()
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig("./Assets/Spaceships/Part-Fx/Part-Efx/basic_xpld_efx.ptf")
        self.explodeEffect.setScale(20)
        self.explodeNode = self.render.attachNewNode('ExplosionEffects')

    def DroneDestroy(self, hitID, hitPosition):
        nodeID = self.render.find(hitID)
        nodeID.detachNode()

        self.explodeNode.setPos(hitPosition)                                            #start explosion
        self.Explode(hitPosition)

    def Explode(self, impactPoint):
        self.cntExplode += 1
        tag = 'particles-' + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, fromData = 0, toData = 1, duration = 4.0, extraArgs = [impactPoint])
        self.explodeIntervals[tag].start()

    def ExplodeLight(self, t, explosionPosition):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable()
        elif t == 0:
            self.explodeEffect.start(self.explodeNode)


        

        
app = SpaceJam()
app.Ship.SetKeyBinding()
app.run()