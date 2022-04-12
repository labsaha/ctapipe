from astropy import units as u
import numpy as np

from ctapipe.containers import ImageParametersContainer, HillasParametersContainer
from ctapipe.image.cleaning import tailcuts_clean
from ctapipe.image import ImageProcessor
from ctapipe.io import EventSource
from ctapipe.reco import HillasReconstructor, HillasIntersection

from ctapipe.reco.reco_algorithms import InvalidWidthException

from ctapipe.utils import get_dataset_path
from astropy.coordinates import SkyCoord, AltAz
from ctapipe.calib import CameraCalibrator

import pytest


@pytest.fixture
def reconstructors():
    return [HillasIntersection, HillasReconstructor]


def test_reconstructors(reconstructors):
    """
    a test of the complete fit procedure on one event including:
    • tailcut cleaning
    • hillas parametrisation
    • HillasPlane creation
    • direction fit
    • position fit

    in the end, proper units in the output are asserted"""

    filename = get_dataset_path(
        "gamma_LaPalma_baseline_20Zd_180Az_prod3b_test.simtel.gz"
    )

    source = EventSource(filename, max_events=10)
    subarray = source.subarray
    calib = CameraCalibrator(source.subarray)
    image_processor = ImageProcessor(source.subarray)
    horizon_frame = AltAz()

    for event in source:
        calib(event)
        image_processor(event)

        for ReconstructorType in reconstructors:
            reconstructor = ReconstructorType(subarray)

            reconstructor(event)

            name = ReconstructorType.__name__
            assert event.dl2.stereo.geometry[name].alt.unit.is_equivalent(u.deg)
            assert event.dl2.stereo.geometry[name].az.unit.is_equivalent(u.deg)
            assert event.dl2.stereo.geometry[name].core_x.unit.is_equivalent(u.m)
