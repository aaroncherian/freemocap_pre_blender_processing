from dataclasses import dataclass, field


@dataclass
class AdjustEmpties:
    vertical_align_reference: str = "left_knee"
    vertical_align_angle_offset: float = 0.0
    ground_align_reference: str = "left_foot_index"
    vertical_align_position_offset: float = 0.0
    correct_fingers_empties: bool = True
    add_hand_middle_empty: bool = True


@dataclass
class ReduceBoneLengthDispersion:
    interval_variable: str = "median"
    interval_factor: float = 0.0


@dataclass
class ReduceShakiness:
    recording_fps: float = 30.0


@dataclass
class AddRig:
    bone_length_method: str = "median_length"
    keep_symmetry: bool = False
    add_fingers_constraints: bool = True
    use_limit_rotation: bool = False


@dataclass
class AddBodyMesh:
    body_mesh_mode: str = "custom"


@dataclass
class Config:
    adjust_empties: AdjustEmpties = field(default_factory=AdjustEmpties)
    reduce_bone_length_dispersion: ReduceBoneLengthDispersion = field(default_factory=ReduceBoneLengthDispersion)
    reduce_shakiness: ReduceShakiness = field(default_factory=ReduceShakiness)
    add_rig: AddRig = field(default_factory=AddRig)
    add_body_mesh: AddBodyMesh = field(default_factory=AddBodyMesh)
