import traceback
from pathlib import Path
from typing import List
import numpy as np

from freemocap_blender_prep.data_models.parameter_models.parameter_models import Config
from freemocap_blender_prep.freemocap_data_handler.utilities.get_or_create_freemocap_data_handler import (
    get_or_create_freemocap_data_handler,
)
from freemocap_blender_prep.freemocap_data_handler.utilities.load_data import load_freemocap_data
from freemocap_blender_prep.freemocap_data_handler.operations.put_skeleton_on_ground import put_skeleton_on_ground
from freemocap_blender_prep.freemocap_data_handler.operations.enforce_rigid_bones.enforce_rigid_bones import enforce_rigid_bones
from freemocap_blender_prep.freemocap_data_handler.operations.fix_hand_data import fix_hand_data
from freemocap_blender_prep.freemocap_data_handler.helpers.saver import FreemocapDataSaver





class MainController:
    """
    This class is used to run the program as a main script.
    """

    def __init__(self, recording_path: str):

        self.recording_path = recording_path
        self.recording_name = Path(self.recording_path).stem
        self.freemocap_data_handler = get_or_create_freemocap_data_handler(
            recording_path=self.recording_path
        )

    def load_freemocap_data(self):
        try:
            print("Loading freemocap data....")
            self.freemocap_data_handler = load_freemocap_data(
                recording_path=self.recording_path
            )
            self.freemocap_data_handler.mark_processing_stage("original_from_file")
            
        except Exception as e:
            print(f"Failed to load freemocap data: {e}")
            raise e

    def calculate_virtual_trajectories(self):
        try:
            print("Calculating virtual trajectories....")
            self.freemocap_data_handler.calculate_virtual_trajectories()
            self.freemocap_data_handler.mark_processing_stage(
                "add_virtual_trajectories"
            )
        except Exception as e:
            print(f"Failed to calculate virtual trajectories: {e}")
            print(e)
            raise e

    def put_data_in_inertial_reference_frame(self):
        try:
            print("Putting freemocap data in inertial reference frame....")
            put_skeleton_on_ground(handler=self.freemocap_data_handler)
        except Exception as e:
            print(
                f"Failed when trying to put freemocap data in inertial reference frame: {e}"
            )
            print(traceback.format_exc())
            raise e

    def enforce_rigid_bones(self):
        print("Enforcing rigid bones...")
        try:
            self.freemocap_data_handler = enforce_rigid_bones(
                handler=self.freemocap_data_handler
            )

        except Exception as e:
            print(f"Failed during `enforce rigid bones`, error: `{e}`")
            print(e)
            raise e

    def fix_hand_data(self):
        try:
            print("Fixing hand data...")
            self.freemocap_data_handler = fix_hand_data(
                handler=self.freemocap_data_handler
            )
        except Exception as e:
            print(f"Failed during `fix hand data`, error: `{e}`")
            print(e)
            raise e

    def save_data_to_disk(self):
        try:
            print("Saving data to disk...")
            FreemocapDataSaver(handler=self.freemocap_data_handler).save(
                recording_path=self.recording_path
            )
        except Exception as e:
            print(f"Failed to save data to disk: {e}")
            print(e)
            raise e

    def run_all(self):
        print("Running all stages...")

        #Pure python stuff
        self.load_freemocap_data()
        self.calculate_virtual_trajectories()
        self.put_data_in_inertial_reference_frame()
        self.enforce_rigid_bones()
        self.fix_hand_data()
        self.save_data_to_disk()

        
if __name__ == '__main__':
    recording_path = r"C:\Users\aaron\FreeMocap_Data\recording_sessions\session_2024-02-14_14_33_40\recording_14_35_07_gmt-5"
    blend_file_path = None
    config = Config()
    main_controller = MainController(recording_path)
    main_controller.run_all()
    print("done")