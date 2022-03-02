# Copyright 2020 - 2021 MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Callable, Sequence

from monai.inferers import SlidingWindowInferer
from monai.transforms import (
    Activationsd,
    AddChanneld,
    AsDiscreted,
    LoadImaged,
    NormalizeIntensityd,
    Resized,
    ToNumpyd,
    ToTensord,
)

from monailabel.interfaces.tasks.infer import InferTask, InferType
from monailabel.transform.post import BoundingBoxd, Restored


class MyInfer(InferTask):
    """
    This provides Inference Engine for pre-trained segmentation (UNet) model over MSD Dataset.
    """

    def __init__(
        self,
        path,
        network=None,
        type=InferType.SEGMENTATION,
        label_names=None,
        spatial_size=(128, 128, 128),
        dimension=3,
        description="A pre-trained model for volumetric (3D) segmentation over 3D Images",
    ):
        super().__init__(
            path=path,
            network=network,
            type=type,
            labels=label_names,
            dimension=dimension,
            description=description,
        )
        self.spatial_size = spatial_size
        self.label_names = label_names

    def pre_transforms(self, data=None) -> Sequence[Callable]:
        return [
            LoadImaged(keys="image", reader="ITKReader"),
            AddChanneld(keys="image"),
            Resized(keys=("image", "label"), spatial_size=self.spatial_size),
            NormalizeIntensityd(keys="image"),
            ToTensord(keys="image"),
        ]

    def inferer(self, data=None) -> Callable:
        return SlidingWindowInferer(roi_size=[96, 96, 96])

    def inverse_transforms(self, data=None) -> Sequence[Callable]:
        return []  # Self-determine from the list of pre-transforms provided

    def post_transforms(self, data=None) -> Sequence[Callable]:
        return [
            Activationsd(keys="pred", softmax=True),
            AsDiscreted(keys="pred", argmax=True),
            ToNumpyd(keys="pred"),
            Restored(keys="pred", ref_image="image"),
            BoundingBoxd(keys="pred", result="result", bbox="bbox"),
        ]
