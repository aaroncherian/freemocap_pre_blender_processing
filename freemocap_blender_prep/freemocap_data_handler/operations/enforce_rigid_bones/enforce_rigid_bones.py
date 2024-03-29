from copy import deepcopy
from typing import Dict, Any

import numpy as np
from freemocap_blender_prep.data_models.bones.bone_definitions import BONE_DEFINITIONS
from freemocap_blender_prep.data_models.mediapipe_names.mediapipe_heirarchy import MEDIAPIPE_HIERARCHY

from .calculate_body_dimensions import calculate_body_dimensions
from ..enforce_rigid_bones.calculate_bone_length_statistics import calculate_bone_length_statistics
from ...handler import FreemocapDataHandler


def enforce_rigid_bones(handler: FreemocapDataHandler,
                        bones: Dict[str, Dict[str, Any]] = BONE_DEFINITIONS) -> FreemocapDataHandler:
    print('Enforcing rigid bones - altering bone lengths to ensure they are the same length on each frame...')
    original_trajectories = handler.trajectories
    updated_trajectories = deepcopy(original_trajectories)

    # Update the information of the virtual bones
    bones = calculate_bone_length_statistics(trajectories=original_trajectories, bones=bones)

    # Print the current bones length median, standard deviation and coefficient of variation
    log_bone_statistics(bones=bones, type='original')

    # Iterate through the lengths array of each bone and check if the length is outside the interval defined by x*stdev with x as a factor
    # If the bone length is outside the interval, adjust the coordinates of the tail empty and its children so the new bone length is at the border of the interval

    for name, bone in bones.items():
        print(f"Enforcing rigid length for bone: {name}...")

        desired_length = bone['median']

        head_name = bone['head']
        tail_name = bone['tail']

        for frame_number, raw_length in enumerate(bone['lengths']):
            if np.isnan(raw_length) or raw_length == 0:
                continue

            head_position = original_trajectories[head_name][frame_number, :]
            tail_position = original_trajectories[tail_name][frame_number, :]

            bone_vector = tail_position - head_position

            # Get the normalized bone vector by dividing the bone_vector by its length
            try:
              bone_vector_norm = bone_vector / raw_length
            except ZeroDivisionError:
              raw_length = 0.0001
              bone_vector_norm = bone_vector / raw_length

            # Calculate the new tail position delta by multiplying the normalized bone vector by the difference of desired_length and original_length
            position_delta = bone_vector_norm * (desired_length - raw_length)

            updated_trajectories = translate_trajectory_and_its_children(name=tail_name,
                                                                         position_delta=position_delta,
                                                                         frame_number=frame_number,
                                                                         updated_trajectories=updated_trajectories)

    print('Bone lengths enforced successfully!')

    # Update the information of the virtual bones
    updated_bones = calculate_bone_length_statistics(trajectories=updated_trajectories, bones=bones)

    # Print the current bones length median, standard deviation and coefficient of variation
    log_bone_statistics(bones=updated_bones, type='updated')

    print('Updating freemocap data handler with the new trajectories...')
    for name, trajectory in updated_trajectories.items():
        handler.set_trajectory(name=name, data=trajectory)

    handler.mark_processing_stage(name='enforced_rigid_bones',
                                  metadata={"bone_data": updated_bones,
                                            "body_dimensions": calculate_body_dimensions(bones_info=updated_bones),
                                            "skeleton_hierarchy": MEDIAPIPE_HIERARCHY},
                                  )
    return handler


def translate_trajectory_and_its_children(name: str,
                                          position_delta: np.ndarray,
                                          frame_number: int,
                                          updated_trajectories: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    # recursively translate the tail empty and its children by the position delta.
    try:
        updated_trajectories[name][frame_number, :] = updated_trajectories[name][frame_number, :] + position_delta

        if name in MEDIAPIPE_HIERARCHY.keys():
            for child_name in MEDIAPIPE_HIERARCHY[name]['children']:
                translate_trajectory_and_its_children(name=child_name,
                                                      position_delta=position_delta,
                                                      frame_number=frame_number,
                                                      updated_trajectories=updated_trajectories)
    except Exception as e:
        print(f"Error while adjusting trajectory `{name}` and its children:\n error:\n {e}")
        print(e)
        raise Exception(f"Error while adjusting trajectory and its children: {e}")

    return updated_trajectories


def log_bone_statistics(bones: Dict[str, Dict[str, Any]], type: str):
    log_string = f'\n\n[{type}] Bone Length Statistics:\n'
    header_string = f"{'BONE':<15} {'MEDIAN (cm)':>12} {'STDEV (cm)':>12} {'CV (%)':>12}"
    log_string += header_string + '\n'
    for name, bone in bones.items():
        # Get the statistic values
        median_string = str(round(bone['median'] * 100, 7))
        stdev_string = str(round(bone['stdev'] * 100, 7))
        cv_string = str(round(bone['stdev'] / bone['median'] * 100, 4))
        log_string += f"{name:<15} {median_string:>12} {stdev_string:>12} {cv_string:>12}\n"

    print(log_string)
