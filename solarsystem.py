import bpy
import math

# planet_radius is the radius of the planet
# orbit_radius is the distance of the planet from the Sun
# planet_num is the identification name of the planet
def create_planet(planet_radius, orbit_radius, name):
    planet = bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=planet_radius, location=(orbit_radius, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
    bpy.context.object.name = name # change the name of the planet object
    bpy.ops.object.shade_smooth() # make the planet smooth
    return bpy.context.object # return reference to the planet object
    

# num_planets is the number of planets orbiting the Sun in this solar system
def create_planets(num_planets):
    planets = [] # save all planet objects
    for i in range(num_planets):
        new_planet = create_planet(2, 20 * (i + 1), "Planet." + str(i)) # create a new planet object
        set_orbit_animation(new_planet, (i + 1) * 1.5, i) # set the orbit animation of the new planet object
        planets.append(new_planet) # save the planet object in the list of planet objects
    

def set_orbit_animation(planet, num_orbits, planet_num):
    # select the planet so that it's active
    bpy.context.view_layer.objects.active = planet
    planet.select_set(True)

    # set the planet's origin to be the world origin as the center to orbit around
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")

    # create animation data for the planet
    planet.animation_data_create()

    # bpy.data.actions holds all of the actions in the scenes
    planet.animation_data.action = bpy.data.actions.new(name=("PlanetOrbit." + str(planet_num)))
    
    # fcurves: https://docs.blender.org/manual/en/latest/editors/graph_editor/fcurves/introduction.html
    planet_fcurve = planet.animation_data.action.fcurves.new(data_path="rotation_euler", index=2) # rotation z

    # bpy.data.actions[action].fcurves.new
    start_kf = planet_fcurve.keyframe_points.insert(frame=start_frame_num, value=0) # add animation start point
    end_kf = planet_fcurve.keyframe_points.insert(frame=end_frame_num, value=(2 * math.pi * num_orbits)) # add animation end point; value = 2*pi for one revolution around the Sun completed at the end frame number
    for point in planet_fcurve.keyframe_points:
        point.interpolation = "LINEAR" # set the animation curve's interpolation type to linear for constant speed orbit
        

# Test
start_frame_num = 1
end_frame_num = 240

scene = bpy.context.scene
scene.frame_start = start_frame_num
scene.frame_end = end_frame_num
scene.frame_current = start_frame_num
# planet = create_planet(3, 20, "Earth")
create_planets(2)
