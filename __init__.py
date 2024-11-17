bl_info = {
    "name": "Better Bone Symmetry",
    "author": "Pascal Schovanez",
    "version": (0, 1),
    "blender": (4, 2, 0),
    "location": "View3D > Pose",  # Sidebar > Symmetrize Tab / Pose Mode Context Menu",
    "description": "Symmetrize extra Bone data.",
    "warning": "",
    "wiki_url": "",
    "category": "Pose",
}

################
#   NOTE TO SELF
################
# This addon will not replace the existing symmetrize function.
# Instead, it will simply be used to 'symmetrize extra bone information, beyond the standard symmetrize function'.
# Meaning that it will only be used in 'Pose Mode' not 'Edit Mode'.


################
#   TODO
################
# - Re-write functions to take selected bones as SOURCE for all functions (instead of searching for bones via the .L and .R opperators. (not sure if they are still needed for the collections though?)
#       - Maybe simply add a toggle for 'Selected Bone(s)', swapping between searching all bones or only for the selected ones.
#           - Change dynamically whether this toggle is already selected or not, based on if a bone has is selected/active when the function is called. (Maybe via polling?)
# - Figure out how to call the symmetrize tool, and pass the Direction variable to it, so that it can be ran through the Addon - completely.
# - Figure out Enums, how to make them, and if its possible to take existing Blender enums. (i.e. Symmetrize - Direction enum)
# - Figure out how to add addon functionality to the POSE menu shortcut (might only need to properly add it to the 'Pose' menu, but currently doesnt show up in hot-key-menu)


import bpy
from bpy.types import (
    AddonPreferences,
    Operator,
    Panel,
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    StringProperty,
    EnumProperty,
)
#from enum import ENUM - blender doesnt know what this is

#####         #####
#     GLOBALS     #
#####         #####
rig = None          # Will be used by all Symmetry Options
#saved_mode = None # If I want to let this functionality be called independant of being in pose mode or not, but unlikely


#####                      #####
#     Main UI-Option Class     #
#####                      #####
class OBJECT_OT_bettersym(Operator):
    bl_label = "Better Bone Symmetry"
    bl_idname = "pose.better_bone_symmetry"
    bl_description = "Bone Symmetry toolkit, to unify common symmetry needs."
    bl_space = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER",
                  "UNDO"}  # UNDO = alows re-do panel in bottom right of viewport, to adjust settings after operation ran.


    ###                   ###
    #   CUSTOM PROPERTIES   #
    ###                   ###
    # Properties for UNDO panel
    bSymmetryType: bpy.props.BoolProperty(
        name="Selected Bone(s)",
        #icon="RESTRICT_SELECT_OFF", - Doesnt recognize icon as a parameter?
        default=True,
        description="Whether to only Symmetrize the data from active/selected bones (TRUE) or all bones (FALSE) in the armature.",
    )
    symmetrySource: bpy.props.StringProperty(
        name="Source Bone Namer",
        default=".L",
        description="The String that will be used to identify the bone(s), which to symmetrize extra functionality from.",
    )
    symmetryTarget: bpy.props.StringProperty(
        name="Target Bone Namer",
        default=".R",
        description="The String that will be used to decide what bone(s), to give the extra functionality to./nWill do nothing if no bone(s) is found with this Namer.",
    )
    symmetryNamingStyle: bpy.props.EnumProperty(
        name = "Naming Convention Style",
        default = "Suffix",
        items = [
            ("Prefix", "Prefix", "Prefix: will only search the END of the Bone(s)'s Name (i.e Valid Case: L.MyBone | Invalid Case: MyBone L.)"),
            ("Suffix", "Suffix", "Suffix: will only search the START of the Bone(s)'s Name (i.e Valid Case: MyBone.L | Invalid Case: .LMyBone)"),
            ("Substring", "Substring", "Substring: Will search through ALL of the Bone(s)'s name, and chose any that match this character-combo case (i.e Both of these are valid matches: MyBone.L, My.LBone)")
             ],
        description = "Choose what naming convention should be considered when checking the names. ---------- Might be useless since the Namers will already indicate the convention",
    )
    bSymmetrizeCollections: bpy.props.BoolProperty(
        name="Sym Bone Collection",
        default=True,
        description="Move to Mirrored Bone Collections, assuming they are follow a naming convention (i.e. Suffix)./nWill create new collections if they dont already exist, matching the naming convention of the Bone.",
    )
    bSymmetrizeModifiers: bpy.props.BoolProperty(
        name="Sym Bone Modifiers",
        default=True,
        description="Copy the Modifiers of the Source Bones to the Target Bones.",
    )
    bSymmetrizeDrivers: bpy.props.BoolProperty(
        name="Sym Bone Drivers",
        default=True,
        description="Will attempt to Copy the Driver(s) setup, that was used in the Source Bone(s) to the newly created Target Bone(s)./nIf no matching modifiers are found on the relevant bones then no drivers will be created.",
    )


    ###            ###
    #   Conditions   #
    ###            ###
    # Ensure only wanted Armature is selected in Pose Mode, with an active pose bone (need to have a Target that can be symmetrized
    @classmethod
    def poll(cls, context):
        return context.object.select_get() and context.mode == 'POSE'  # If in POSE mode then guaranteed to be an Armature, as only Armature's have this mode.

    # Creates a Pop-up to adjust parameters before actually running the script, MIGHT be usefuly, if using the UNDO panel proves to be too slow, as it live-updates.
    #def invoke(self, context, event):
    #    return context.window_manager.invoke_props_dialog(self)


    ###                     ###
    #   Class Functionality   #
    ###                     ###
    def execute(self, context):
        # Save Armature
        armature = context.active_object.data
        # Bones to Source Data from
        sourceBones = []

        # --- Determine Source Method ---
        if self.bSymmetryType: # Selected Bones
            print("Selected Bones Only")
            sourceBones = context.selected_pose_bones
        else:
            print("All Bones")
            sourceBones = armature.bones

        # --- Determine what to symmetrize ---
        if self.bSymmetrizeCollections:
            print("Symmetrize COLLECTIONS")

        if self.bSymmetrizeModifiers:
            print("Symmetrize MODIFIERS")

        if self.bSymmetrizeDrivers:
            print("Symmetrize DRIVERS")

        print("FINISHED EXECUTION: Better Bone Symmetry")
        return {'FINISHED'}


#####             #####
#     Collections     #
#####             #####



#####           #####
#     Modifiers     #
#####           #####



#####         #####
#     Drivers     #
#####         #####



#####         #####
#     Helpers     #
#####         #####

class Style():
    PREFIX = "Prefix",
    SUFFIX = "Suffix",
    SUBSTRING = "Substring",


#####                    #####
#     Addon Registration     #
#####                    #####

# Register addon class as menu-operator
def menu_func(self, context):
    self.layout.operator(OBJECT_OT_bettersym.bl_idname, icon="BONE_DATA")

# Un/Register functions for when addon is installed or removed
def register():
    bpy.utils.register_class(OBJECT_OT_bettersym)
    #bpy.types.VIEW3D_MT_pose.append(menu_func)  # Register operator to Pose-Menu
    bpy.types.VIEW3D_MT_pose_context_menu.append(menu_func)  # Register operator to Pose-Context-Menu
    print("Registered: Better Bone Symmetry")


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_bettersym)
    #bpy.types.VIEW3D_MT_pose.remove(menu_func)
    bpy.types.VIEW3D_MT_pose_context_menu.remove(menu_func)
    print("Unregistered: Better Bone Symmetry")

# Addon Entry Point
if __name__ == "__main__":
    register()