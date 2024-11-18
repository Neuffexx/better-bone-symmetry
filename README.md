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
**NOTE**  
This Addon was made specifically to be flexible in working with any naming convention,  
BUT requires it to be consistent.  
    
    i.e. Bones and Collections need to have the same suffix, to use Collection Symmetry

If no Collection is involved though, then it is possible to copy data between bones outside Prefix/Suffix conventions,
via the substring option.  
    
    i.e. 
    ) Bones: 'MCH - Thumb_XX_tip.L', and 'MCH - Finger_XX_tip.L'
    ) Source Namer: 'Thumb' 
    ) Target Namer: 'Finger'
    ) Namver Convention: 'Substring'
    Copy's Constraints: 'MCH - Thumb_01_tip.L' -> 'MCH - Finger_01_tip.L'
    For all 'Thumb_XX' and 'Finger_XX' bones selected (if Selected Bones enabled).
    
    --- WARNING! ---
    In such a usecase, where you want to copy data between bones of the same symmetry side,
    this can also copy the constarints .R bones, if they exist, not only .L bones.
    Therefore it is recommended to do this before creating bones via Blender's Symmetrize, or use 'Selected Bones' option.


### Location:  
- View3D > Pose Mode > Pose
- Pose Context Menu - W Hotkey  
  (I use 27x keybinds, so it may be different for you)

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
