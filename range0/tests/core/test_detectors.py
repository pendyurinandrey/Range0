#   Range0 - the software for practical shooting training
#   Copyright (C) 2020 pendyurinandrey
#  #
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#  #
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#  #
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pytest
import cv2.cv2 as cv

from range0.core.detectors import SimpleDetectionStrategy

debug_enabled = False


@pytest.mark.usefixtures('datadir')
def test_simple_detector_strategy(datadir):
    file = '{}/simple_red_dot.jpg'.format(datadir)
    frame = cv.imread(file)
    strategy = SimpleDetectionStrategy()
    result = strategy.detect(frame)
    if debug_enabled:
        for point in result.points:
            print('x = {}, y = {}'.format(point.x, point.y))
            frame = __draw_circle(frame, point.x, point.y)
        cv.imwrite('test_simple_detector_strategy_output.jpg', frame)

    assert len(result.points) == 1
    assert result.points[0].x == 894
    assert result.points[0].y == 1601


def __draw_circle(img, x_center: float, y_center: float):
    cv.circle(img, (x_center, y_center), 15, (0, 0, 0), -1)
    return img