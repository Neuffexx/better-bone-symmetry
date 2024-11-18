# Better Bone Symmetry
Symmetrize extra Bone data in Blender.

## Description
I was getting tired of running multiple scripts to copy over more data when symmetrizing bones.  
Therefore I put it all into one addon, though this does not replace the built in 'Symmetrize' tool.  
Bust is intended to be used after the built in one.

## Features:
- Symmetrize Bone Collections
  - Assign to Parent Collections (up the hierarchy)  
    *This is a workaround for 4.2.3
- Symmetrize Bone Constraints (WIP)
- Symmetrize Drivers (WIP)


## Details
    This Addon was made specifically to be flexible to work with any naming convention,
    BUT requires it to be consistent.
    (i.e. Bones and Collections need to have the same suffix, to use Collection Symmetry)

    Though it is possible to copy data between bones that outside Prefix/Suffix selection,
    via the substring option.
    (i.e. Source Namer: 'MCH - Thumb' | Target Namer: 'MCH - Finger', to copy Constraints: 'MCH - Thumb_01_tip' -> 'MCH - Finger_01_tip' etc.)  

### Location:  
- View3D > Pose  
- Pose Context Menu - W Hotkey (I use 27x keybinds, so it may be different for you)

### Options: 
![image](https://github.com/user-attachments/assets/c395494d-7715-4f10-b8f7-314345213009)

- **Selected Bones:**  
  When enabled, will only perform operations on/based on selected bones.
- **Source Bone Namer:**  
- **Target Bone Namer:**  
- **Namer Convention Style:**  
  - Prefix: Search for Source/Target Namer's at the START of the Name (i.e. L.MyBone)
  - Suffix: Search for Source/Target Namer's at the END of the Name (i.e. MyBone.L)
  - Substring: Search for Source/Target Namer's ANYWHERE in the Name (i.e. My.LBone)
- **Sym Bone Collections:**  
  When enabled, will symmetrize bone collections, assigning the bones to their appropriate collection.  
  Will also sort the symmetrized collections to follow the hierarchy of nested source collections  
  `(Sorting cannot be turned off at the moment)`.
- **Assign Top-Parent Collection:**  
  When enabled, will assign bones to the Parent collection's of its collection, recursively.  
  Allowing you to solo nested collections, from the Top-Parent collection.
- **Sym Bone Constraints:**  
  When enabled, will copy bone constraints from the Source-bones to the Target-bones.
- **Sym Drivers:**  
