import bpy
import math

class Satellite:
  def __init__(self, name, radius, distance_from_sun, orbital_speed, object):
    self.name = name # name of the satellite (integer identifier)
    self.radius = radius # radius of the satellite
    self.distance_from_sun = distance_from_sun # the starting distance of the satellite from the Sun
    self.orbital_speed = orbital_speed # number of revolutions around the parent planet completed between start and end frame
    self.object = object # reference to the satellite Blender object, None at first

# initialize satellites in solar system
satellite1 = Satellite("1", 1, 24, 2, None)
satellite2 = Satellite("2", 1, 44, 2, None)
satellite3 = Satellite("3", 1, 48, 3, None)
satellite4 = Satellite("4", 0.5, 66, 1.5, None)

class Planet:
  def __init__(self, name, radius, distance_from_sun, orbital_speed, object, satellites):
    self.name = name # name of the planet (integer identifier)
    self.radius = radius # radius of the planet
    self.distance_from_sun = distance_from_sun # the distance of the planet from the Sun
    self.orbital_speed = orbital_speed # number of revolutions around the Sun completed between start and end frame
    self.object = object # reference to the planet Blender object, None at first
    self.satellites = satellites # list of Satellites that orbit this planet

# initialize planets in solar system
planet1 = Planet("1", 1.5, 20, 2.25, None, [satellite1])
planet2 = Planet("2", 2, 40, 1.75, None, [satellite2, satellite3])
planet3 = Planet("3", 3, 55, 1.25, None, [])
planet4 = Planet("4", 2.5, 70, 1, None, [satellite4])

# all of the planets in this solar system
all_planets_data = [planet1, planet2, planet3, planet4]


# obj_radius is the radius of the celestial object
# orbit_radius is the distance of the celestial object from the center it is orbiting around
# name is the identification name of the celestial object
def create_celestial_obj(obj_radius, orbit_radius, name):
    celestial_obj = bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=obj_radius, location=(orbit_radius, 0.0, 0.0), scale=(1.0, 1.0, 1.0)) # create an icosphere to be the celestial object
    bpy.context.object.name = name # change the name of the celestial object
    bpy.ops.object.shade_smooth() # make the celestial object smooth
    return bpy.context.object # return reference to the celestial object
    
# rotate the planet on its axis
def set_planet_rotation(planet):
    # create animation data for the planet
    planet.animation_data_create()

    # bpy.data.actions holds all of the actions in the scenes
    planet.animation_data.action = bpy.data.actions.new(name=("PlanetRotation." + str(planet.name)))

    # fcurves: https://docs.blender.org/manual/en/latest/editors/graph_editor/fcurves/introduction.html
    planet_fcurve = planet.animation_data.action.fcurves.new(data_path="rotation_euler", index=2) # rotation z

    start_kf = planet_fcurve.keyframe_points.insert(frame=start_frame_num, value=0) # add animation start point
    end_kf = planet_fcurve.keyframe_points.insert(frame=end_frame_num, value=(3 * 2 * math.pi)) # add animation end point; value = 2*pi for one full rotation
    for point in planet_fcurve.keyframe_points:
        point.interpolation = "LINEAR" # set the animation curve's interpolation type to linear for constant speed orbit 
    return planet


# create planet objects from the list of Planets data
def create_planets(planet_data):
    planets = [] # save all planet objects
    for planet in planet_data:
        new_planet = create_celestial_obj(planet.radius, planet.distance_from_sun, "Planet." + planet.name) # create a new planet object
        set_planet_orbit(new_planet, planet.orbital_speed) # set the orbit animation of the new planet object
        set_planet_rotation(new_planet) # rotate planet
        planet.object = new_planet # store reference to created planet object
        planets.append(new_planet) # save the planet object in the list of planet objects
    return planets    

# sets the planet object's animation with speed determined by num_orbits done between start to end frame
def set_planet_orbit(planet, num_orbits):
    scene.cursor.location = (0.0, 0.0, 0.0)  # snap cursor to world origin at (0.0, 0.0, 0.0) so the orbits are around the world origin
    bpy.ops.object.empty_add(type='PLAIN_AXES',radius=10.0,location=scene.cursor.location) # create an empty at the world origin for the planet to rotate with
    planet_orbit_empty = bpy.context.object # save the empty as planet_orbit_empty
    bpy.context.object.name = planet.name + "-Sun-orbit" # rename the empty for this specific planet's orbit around the Sun
    planet.parent = planet_orbit_empty # make the empty the parent of the planet
    planet.matrix_parent_inverse = planet_orbit_empty.matrix_world.inverted() # assign parent relationship while keeping the transform; get rid of the initial parent's transformation effect on the child when setting the parent-child relationship 
    
    # create torus to see the orbit path of the planet around the Sun
    torus_radius = 0.2 # how thick the torus is
    bpy.ops.mesh.primitive_torus_add(align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), major_segments=48, minor_segments=12, mode='MAJOR_MINOR', major_radius=(abs(planet.location[0]) - (torus_radius / 2.0)), minor_radius=torus_radius) # create torus object centered around Sun (world origin)
    
    planet_orbit_path = bpy.context.object # save reference to the satellite orbit path torus object
    bpy.context.object.name = "Torus-" + planet.name + "-Sun-orbit" # change the name of the empty

    # make the torus follow the orbit
    planet_orbit_path.parent = planet_orbit_empty # make the empty the parent of the satellite
    planet_orbit_path.matrix_parent_inverse = planet_orbit_empty.matrix_world.inverted() # assign parent relationship while keeping the transform; get rid of the initial parent's transformation effect on the child when setting the parent-child relationship 
    
    # ROTATE THE EMPTY
    planet_orbit_empty.animation_data_create() # create animation data for the planet
    planet_orbit_empty.animation_data.action = bpy.data.actions.new(name=(planet.name + "-orbit"))  # bpy.data.actions holds all of the actions in the scenes
    
    # fcurves: https://docs.blender.org/manual/en/latest/editors/graph_editor/fcurves/introduction.html
    planet_fcurve = planet_orbit_empty.animation_data.action.fcurves.new(data_path="rotation_euler", index=2) # rotation z
    start_kf = planet_fcurve.keyframe_points.insert(frame=start_frame_num, value=0) # add animation start point
    end_kf = planet_fcurve.keyframe_points.insert(frame=end_frame_num, value=(2 * math.pi * num_orbits)) # add animation end point; value = 2*pi for one revolution around the Sun completed at the end frame number
    for point in planet_fcurve.keyframe_points:
        point.interpolation = "LINEAR" # set the animation curve's interpolation type to linear for constant speed orbit
    return


# set the orbit animation for a given satellite object around a given planet object
def set_satellite_orbit(satellite, speed, planet):
    print("planet.location: " + str(planet.location))
    print("satellite.location: " + str(satellite.location))
    bpy.ops.object.empty_add(type='PLAIN_AXES',radius=10.0,location=planet.location) # add an empty at the planet's location for the satellite to rotate with
    satellite_orbit_empty = bpy.context.object
    bpy.context.object.name = satellite.name + "-" + planet.name + "-orbit" # change the name of the empty

    satellite.parent = satellite_orbit_empty # make the empty the parent of the satellite
    satellite.matrix_parent_inverse = satellite_orbit_empty.matrix_world.inverted() # assign parent relationship while keeping the transform; get rid of the initial parent's transformation effect on the child when setting the parent-child relationship 
    satellite_orbit_empty.parent = planet # make the planet the parent of the empty that the satellite is the child of
    satellite_orbit_empty.matrix_parent_inverse = planet.matrix_world.inverted() # assign parent relationship while keeping the transform; get rid of the initial parent's transformation effect on the child when setting the parent-child relationship 
    
    # create torus to see the orbit path of the satellite
    torus_radius = 0.2 # how thick the torus is
    bpy.ops.mesh.primitive_torus_add(align='WORLD', location=planet.location, rotation=(0.0, 0.0, 0.0), major_segments=48, minor_segments=12, mode='MAJOR_MINOR', major_radius=(abs(satellite.location[0] - planet.location[0]) - (torus_radius / 2.0)), minor_radius=torus_radius) # create torus object
    
    satellite_orbit_path = bpy.context.object # save reference to the satellite orbit path torus object
    bpy.context.object.name = "Torus-" + satellite.name + "-" + planet.name + "-orbit" # change the name of the empty

    # make the torus follow the orbit
    satellite_orbit_path.parent = satellite_orbit_empty # make the empty the parent of the satellite
    satellite_orbit_path.matrix_parent_inverse = satellite_orbit_empty.matrix_world.inverted() # assign parent relationship while keeping the transform; get rid of the initial parent's transformation effect on the child when setting the parent-child relationship 
    
    # ROTATE THE EMPTY
    satellite_orbit_empty.animation_data_create() # create animation data for the satellite
    satellite_orbit_empty.animation_data.action = bpy.data.actions.new(name=(satellite.name + "-orbit")) # bpy.data.actions holds all of the actions in the scenes
    
    # fcurves: https://docs.blender.org/manual/en/latest/editors/graph_editor/fcurves/introduction.html
    satellite_fcurve = satellite_orbit_empty.animation_data.action.fcurves.new(data_path="rotation_euler", index=2) # rotation z
    start_kf = satellite_fcurve.keyframe_points.insert(frame=start_frame_num, value=0) # add animation start point
    end_kf = satellite_fcurve.keyframe_points.insert(frame=end_frame_num, value=(2 * math.pi * speed)) # add animation end point; value = 2*pi for one revolution around the Sun completed at the end frame number
    for point in satellite_fcurve.keyframe_points:
        point.interpolation = "LINEAR" # set the animation curve's interpolation type to linear for constant speed orbit
    return
        

# create the satellites orbiting the Planets in the solar system     
def create_satellites(planets):
    satellites = [] # save all satellite objects
    for planet in planets:
        for satellite in planet.satellites:
            new_satellite = create_celestial_obj(satellite.radius, satellite.distance_from_sun, "Satellite." + satellite.name) # create a new satellite object
            set_satellite_orbit(new_satellite, satellite.orbital_speed, planet.object) # set satellite orbit animation around the planet
            satellite.object = new_satellite # store reference to created planet object
            satellites.append(new_satellite) # save the satellite object in the list of satellite objects
    return 


# Set up scene
start_frame_num = 1
end_frame_num = 240

scene = bpy.context.scene
scene.frame_start = start_frame_num
scene.frame_end = end_frame_num
scene.frame_current = start_frame_num
create_celestial_obj(8, 0, "Sun") # create the Sun
planets = create_planets(all_planets_data)
create_satellites(all_planets_data)