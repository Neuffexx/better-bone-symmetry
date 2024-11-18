bl_info = {
    "name": "Better Bone Symmetry",
    "author": "Pascal Schovanez",
    "version": (0, 1, 0),
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
armature = None         # Will be used by all Symmetry Options
pose = None             # Will be used for Constraints / Drivers
#saved_mode = None # If I want to let this functionality be called independant of being in pose mode or not, but unlikely
SourceNamer = "" # Bones to Copy Data from
TargetNamer = "" # Bones to Paste Data into
NamerStyle = ""  # Whether to check for Prefix/Suffix/Substring


#####                      #####
#     Main UI-Option Class     #
#####                      #####
class OBJECT_OT_bettersym(Operator):
    bl_label = "Better Bone Symmetry"
    bl_idname = "pose.better_bone_symmetry"
    bl_description = "Bone Symmetry toolkit, to unify common symmetry needs."
    bl_space = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}  # UNDO = alows re-do panel in bottom right of viewport, to adjust settings after operation ran.


    ###                   ###
    #   CUSTOM PROPERTIES   #
    # Properties for UNDO panel
    bSymmetryType: bpy.props.BoolProperty(
        name="Selected Bone(s)",
        #icon="RESTRICT_SELECT_OFF", - Doesnt recognize icon as a parameter?
        default=True,
        description="Whether to only Symmetrize the data from active/selected bones (TRUE) or all bones (FALSE) in the armature\nIf Selected Bone(s) True, then MUST select bones that are with the 'Target Namer' as they will be the ones moved to new collection(s)",
    )
    symmetrySource: bpy.props.StringProperty(
        name="Source Bone Namer",
        default=".L",
        description="The String that will be used to identify the bone(s), which to symmetrize extra data from.\n\n*Will do nothing if no bone(s) is found with this Namer",
    )
    symmetryTarget: bpy.props.StringProperty(
        name="Target Bone Namer",
        default=".R",
        description="The String that will be used to decide what bone(s), to give the extra data to.\n\n*Will do nothing if no bone(s) is found with this Namer",
    )
    symmetryNamingStyle: bpy.props.EnumProperty(
        name = "Namer Convention Style",
        default = "Suffix",
        items = [
            ("Prefix", "Prefix", "Prefix: will only search the END of the Bone(s)'s Name.\n\ni.e.\nValid Case: 'L.MyBone' | Invalid Case: 'MyBone L.'"),
            ("Suffix", "Suffix", "Suffix: will only search the START of the Bone(s)'s Name.\n\ni.e.\nValid Case: 'MyBone.L' | Invalid Case: '.LMyBone'"),
            ("Substring", "Substring", "Substring: Will search through ALL of the Bone(s)'s name, and chose any that match this character-combo case.\n\ni.e.\nAll of these are valid Cases: 'MyBone.L', 'My.LBone', '.LMyBone'")
             ],
        description = "Choose what naming convention should be considered when checking the names.",
    )
    bSymmetrizeCollections: bpy.props.BoolProperty(
        name="Sym Bone Collection",
        default=True,
        description="Move to Mirrored Bone Collections, assuming they are follow a naming convention (i.e. Suffix).\nWill create new collections if they dont already exist\n\n*MUST have same naming convention as Bones",
    )
    bAssignToTopParent: bpy.props.BoolProperty(
        name="Assign Top-Parent Collection",
        default=False,
        description="NOTE: Workaround to let you 'Solo' all child collections from a Parent's solo-button.\n\nIn addition to moving the bones to their mirrored parent collections, will also add/assign the bone(s) to the Parent Collection's, up the hierarchy.\n(Not needed if the bones are already assigned to their respective Parent Collections before mirroring the collections)\n\n*This will only work if the 'Sym Bone Collections' pass is also enabled.\n*WILL affect BOTH Source and Target bones",
        #warning="This will only work if the 'Sym Bone Collections' pass is also enabled",
    )
    bSymmetrizeConstraints: bpy.props.BoolProperty(
        name="Sym Bone Constraints",
        default=True,
        description="Copy the Bone-Constraints of the Source Bones to the Target Bones",
    )
    bRemoveExistingConstraints: bpy.props.BoolProperty(
        name="Delete Existing Constraints",
        default=True,
        description="Will remove existing Bone-Constraints of Target Bones, to avoid creating duplicates",
    )
    bSymmetrizeConstraintBones: bpy.props.BoolProperty(
        name="Mirror Constraint Targets",
        default=True,
        description="Whether to mirror Constraint's targeted Bone's.\nOnly used if 'Sym Bone Constraints' is enabled.\n\ni.e. \nSource-StretchTo: Target: 'MyArmature' | Bone: 'MyBone.L' ->\nTarget-StretchTo: Target: 'MyArmature' | Bone: 'MyBone.R'",
    )
    bSymmetrizeDrivers: bpy.props.BoolProperty(
        name="Sym Drivers",
        default=True,
        description="Will attempt to Copy the Driver(s) setup, that was used in the Source Bone(s) to the newly created Target Bone(s)",
    )


    ###            ###
    #   Conditions   #
    # Ensure only wanted Armature is selected in Pose Mode, with an active pose bone (need to have a Target that can be symmetrized
    @classmethod
    def poll(cls, context):
        return context.object.select_get() and context.mode == 'POSE'  # If in POSE mode then guaranteed to be an Armature, as only Armature's have this mode.

    # Creates a Pop-up to adjust parameters before actually running the script, MIGHT be usefuly, if using the UNDO panel proves to be too slow, as it live-updates.
    #def invoke(self, context, event):
    #    return context.window_manager.invoke_props_dialog(self)


    ###                     ###
    #   Class Functionality   #
    def execute(self, context):
        # Save Armature
        global armature, pose
        armature = context.active_object.data
        pose = context.active_object.pose
        # Bone Namers           *Note: One-Time assignment, and used by all passes, therefore globals
        global SourceNamer, TargetNamer, NamerStyle
        SourceNamer = self.symmetrySource
        TargetNamer = self.symmetryTarget
        NamerStyle = self.symmetryNamingStyle
        print("Source Namer: {} | Target Namer: {} | Style: {}".format(SourceNamer, TargetNamer, NamerStyle))
        # Bones to give Data
        targetBones = []

        ###                         ###
        #   Determine Source Method   #
        #   --- Selected Bones ---    #
        if self.bSymmetryType:
            print("Selected Bones Only")
            # PoseBones hold no collection information, need to extract associated 'Bone' objects
            for PoseBone in context.selected_pose_bones:
                targetBones.append(PoseBone.bone)
        else:
            print("All Bones")
            # 'armature.bones' holds a collection object (bpy.types.bpy_prop_collection), need to extract 'Bone' objects
            for key in armature.bones.keys():
                targetBones.append(armature.bones.get(key))

        ###                              ###
        #   Determine what to symmetrize   #
        #       --- Collections ---        #
        if self.bSymmetrizeCollections:
            print("Symmetrize COLLECTIONS")
            # Collections to be created - Tupple of [Collection, Mirrored Name]
            mirrored_collection_names = []

            # Get Collection Names
            gather_mirror_collections(targetBones, armature.collections, mirrored_collection_names)
            # Create Bone Collections
            create_mirror_collections(mirrored_collection_names, armature.collections)
            # Move Bones
            move_mirror_bones(targetBones, armature.collections)
            # Sort Collections
            sort_target_collections(armature)
            # Assign bone to Parent collections upwards of the collection hierarchy, until Top-Level parent.
            if self.bAssignToTopParent:
                assign_to_top_parent(targetBones)

        ###                              ###
        #        --- Modifiers ---         #
        if self.bSymmetrizeConstraints:
            print("Symmetrize MODIFIERS")
            # Copy the constraints from SourcePoseBones to TargetPoseBones
            copy_constraints(targetBones, self.bRemoveExistingConstraints, self.bSymmetrizeConstraintBones)

        ###                              ###
        #         --- Drivers ---          #
        if self.bSymmetrizeDrivers:
            print("Symmetrize DRIVERS")

        ###                                                    ###
        #        --- Deselect Source | Select Target ---         #
        #        Visual Feedback for Operation Completed         #
        select_bones_with_namer('t', targetBones)

        print("FINISHED EXECUTION: Better Bone Symmetry")
        return {'FINISHED'}


#####             #####
#     Collections     #
#####             #####

# Recursively gather Bone-Collections with SourceNamer and change to TargetNamer for Mirroring
def gather_mirror_collections(target_bones, collections, mirrored_collection_names):
    for collection in collections:
        # Check if Collection has SourceNamer
        if has_namer('s', collection.name):
            # Avoid creating collections that dont need mirroring (since there are no bones that need it in them)
            for bone in collection.bones:
                # Ensure that Bone has TargetNamer, and is a 'Source Bone'
                if has_namer('t', bone.name) and (bone in target_bones):
                    mirrored_name = get_target_name(collection.name)
                    # Avoide dupplicate append, in case more than 1 bone inside of same mirrored collection
                    if mirrored_name not in [item[1] for item in mirrored_collection_names]:
                        mirrored_collection_names.append((collection, mirrored_name))
                        print("ADDING MIRRORED COLLECTION: {}".format(mirrored_name))

        # Check if current collection has any children
        if hasattr(collection, 'children'):
            gather_mirror_collections(target_bones, collection.children, mirrored_collection_names)

# Create new Bone-Collections based on the gathered names and save reference
def create_mirror_collections(mirrored_collection_names, collections):
    print("CREATING COLLECTIONS:")

    for original_collection, mirrored_name in mirrored_collection_names:
        # Duplication check
        if not get_collection(mirrored_name, collections):
            new_collection = collections.new(name=mirrored_name)
            # Log
            print("Created Collection: {}".format(new_collection.name))

            # Set the parent collection to maintain hierarchy
            if original_collection.parent:
                parent_mirrored_name = get_target_name(original_collection.parent.name)
                # Check if parent exists first before creating relationship
                parent_collection = get_collection(parent_mirrored_name, collections)
                if parent_collection:
                    new_collection.parent = parent_collection
                    # Log
                    print(
                        "- Assigned To Parent: {}".format(parent_mirrored_name))

# Sort Target Collections to match the hierarchy of Source Collections
def sort_target_collections(armature):
    print("SORTING COLLECTIONS")
    for source_collection in armature.collections:
        if has_namer('s', source_collection.name):
            # Get the mirrored collection for the current source collection
            target_name = get_target_name(source_collection.name)
            target_collection = get_collection(target_name, armature.collections)

            if target_collection:
                # If the source collection has a parent, find its mirrored counterpart and set it as the parent
                if source_collection.parent:
                    parent_target_name = get_target_name(source_collection.parent.name)
                    parent_target_collection = get_collection(parent_target_name, armature.collections)
                    if parent_target_collection:
                        target_collection.parent = parent_target_collection
                        print(f"Assigned: {target_name} to {parent_target_name}")

                # Assign the correct parent for child collections if they exist
                for child_collection in source_collection.children:
                    child_target_name = get_target_name(child_collection.name)
                    child_target_collection = get_collection(child_target_name, armature.collections)
                    if child_target_collection:
                        child_target_collection.parent = target_collection
                        print(f"Assigned Child: {child_target_name} -> Parent: {target_name}")

# Move Bones to correct Collections (only if R bones are in L collections)
def move_mirror_bones(target_bones, collections):
    print("MOVING BONES:")
    for bone in target_bones:
        # Check if the bone has the mirrored suffix (i.e. ".R")
        if TargetNamer in bone.name:
            for collection in bone.collections:
                # Check if the collection has the original suffix (i.e. ".L")
                if SourceNamer in collection.name:
                    # Find the corresponding collection in the dictionary
                    mirrored_collection_key = get_target_name(collection.name)
                    mirrored_collection = get_collection(mirrored_collection_key, collections)
                    if mirrored_collection:
                        # Assign the bone to the mirrored collection
                        mirrored_collection.assign(bone)
                        # Unassign it from the original collection
                        collection.unassign(bone)

                        # Log
                        print("Move Bone: '{}', from Collection: '{}' to Mirrored-Collection: '{}'".format(bone.name, collection.name, mirrored_collection_key))

# Assign Bones to Top-Level Parent collections - to allow soloing all child collections of Top-Level Parent.
# (4.2.3 Workaround)
def assign_to_top_parent(target_bones):
    print("ASSIGNING BONES")
    for bone in target_bones:
        for collection in bone.collections:
            current_collection = collection
            # Traverse upwards in the hierarchy and assign the bone to each parent collection
            while current_collection.parent is not None:
                parent_collection = current_collection.parent
                if bone.name not in parent_collection.bones.keys():
                    parent_collection.assign(bone)
                    print(f"Assigned Bone: {bone.name} to Collection: {parent_collection.name}")
                current_collection = parent_collection


#####             #####
#     Constraints     #
#####             #####

# Copies the constraint of a source pose-bone, based on a target pose-bones name.
def copy_constraints(target_bones, remove_existing, mirror_subtargets):
    global pose

    print("COPYING CONSTRAINTS")
    # Get the PoseBone of the source_bones
    # Only PoseBone's hold information to Constraints.
    target_pose_bones = []
    for target_bone in target_bones:
        target_pose_bones.append(pose.bones.get(target_bone.name))
    # Filter to only be 'Target' bones
    filtered_target_pose_bones = []
    for pose_bone in target_pose_bones:
        if has_namer('t', pose_bone.name):
            filtered_target_pose_bones.append(pose_bone)

    print("Filtered Bones:")
    for bone in filtered_target_pose_bones:
        print("- Bone: {}".format(bone.name))

    for target_pose_bone in filtered_target_pose_bones:
        # Remove all bone constraints (avoid duplicates)
        if remove_existing:
            while target_pose_bone.constraints:
                target_pose_bone.constraints.remove(target_pose_bone.constraints[0])

        # Get bone to copy constraint from
        source_bone_name = get_source_name(target_pose_bone.name)
        source_pose_bone = get_bone(source_bone_name, pose.bones)
        if source_pose_bone:
            # Copy each constraint from source bone to target bone
            for constraint in source_pose_bone.constraints:
                new_constraint = target_pose_bone.constraints.new(type=constraint.type)
                # Copy over properties of the constraint
                for attr in dir(constraint):
                    if not attr.startswith("_") and attr not in {'type', 'rna_type', 'bl_rna'}:
                        try:
                            # Special handling for 'target' and 'subtarget' attributes in constraints
                            if attr == 'subtarget' and mirror_subtargets:
                                # Mirror the bone name in 'subtarget'
                                setattr(new_constraint, attr, get_target_name(getattr(constraint, attr)))
                            else:
                                setattr(new_constraint, attr, getattr(constraint, attr))
                        except AttributeError as ae:
                            print("- Attribute Error, for Constraint '{}': \n{}".format(new_constraint.name, ae))
                print(
                    f"Copied constraint: '{constraint.name}' from: '{source_bone_name}' to: '{target_pose_bone.name}'")


#####         #####
#     Drivers     #
#####         #####



#####         #####
#     Helpers     #
#####         #####

class Style():
    PREFIX = "Prefix"
    SUFFIX = "Suffix"
    SUBSTRING = "Substring"

# Recursively check if a Collection Exists, via name for provided collections
def collection_exists(collection_name, collections):
    for collection in collections:
        if collection.name == collection_name:
            return True
        # Check if current collection has any children
        if hasattr(collection, 'children'):
            if collection_exists(collection_name, collection.children):
                return True
    return False

# Check if a Collection Exists via Name, and return it if it does
def get_collection(collection_name, collections):
    # Use an iterative approach with a stack to avoid recursion
    stack = list(collections)
    while stack:
        collection = stack.pop()
        if collection.name == collection_name:
            return collection
        # Add children to the stack for further searching
        if hasattr(collection, 'children'):
            stack.extend(collection.children)
    return None

def get_bone(bone_name, bones):
    for bone in bones:
        if bone_name == bone.name:
            return bone
    return None

# If the Bone/Collection's matches the Namer convention, based on the NamerStyle, returns True
# NamerType = Literal['s', 't']
def has_namer(NamerType, name):
    match NamerType:
        case 's':
            match NamerStyle:
                case Style.PREFIX:
                    if name.startswith(SourceNamer):
                        return True
                case Style.SUFFIX:
                    if name.endswith(SourceNamer):
                        return True
                case Style.SUBSTRING:
                    if SourceNamer in name:
                        return True
        case 't':
            match NamerStyle:
                case Style.PREFIX:
                    if name.startswith(TargetNamer):
                        return True
                case Style.SUFFIX:
                    if name.endswith(TargetNamer):
                        return True
                case Style.SUBSTRING:
                    if TargetNamer in name:
                        return True
        case _:
            print("'NamerType' neither Source or Target: {}".format(name))

    #print("Has No Namer of {} for {}".format(NamerType, name))
    return False

# Deselects all Bones, then selects bones from the given list that fullfill the Namer requirement
def select_bones_with_namer(NamerType, bones):
    bpy.ops.pose.select_all(action='DESELECT')
    for bone in bones:
        if has_namer(NamerType, bone.name):
            bone.select = True

# Get the Target name of a Source name
def get_target_name(source_name):
    return source_name.replace(SourceNamer, TargetNamer)

# Get the Source name of a Target name
def get_source_name(target_name):
    return target_name.replace(TargetNamer, SourceNamer)


#####                    #####
#     Addon Registration     #
#####                    #####

# Register addon class as menu-operator
def menu_func(self, context):
    self.layout.operator(OBJECT_OT_bettersym.bl_idname, icon="BONE_DATA")

# Un/Register functions for when addon is installed or removed
def register():
    bpy.utils.register_class(OBJECT_OT_bettersym)
    bpy.types.VIEW3D_MT_pose.append(menu_func)  # Register operator to Pose-Menu
    bpy.types.VIEW3D_MT_pose_context_menu.append(menu_func)  # Register operator to Pose-Context-Menu
    print("Registered: Better Bone Symmetry")


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_bettersym)
    bpy.types.VIEW3D_MT_pose.remove(menu_func)
    bpy.types.VIEW3D_MT_pose_context_menu.remove(menu_func)
    print("Unregistered: Better Bone Symmetry")

# Addon Entry Point
if __name__ == "__main__":
    register()