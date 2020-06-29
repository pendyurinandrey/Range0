#include "cameraregistry.h"
#include "defaultcamera.h"
#include "common/common.h"

CameraRegistry::CameraRegistry()
{
    int cameraId = 0;
    for(auto &info: QCameraInfo::availableCameras()) {
        std::shared_ptr<AbstractCamera> camera =
                r0::makeQObjectShared(new DefaultCamera(cameraId, info.deviceName() + " - " + info.description()));
        availableCameras.push_back(camera);
        cameraId++;
    }
}

CameraRegistry& CameraRegistry::getInstance() {
    static CameraRegistry registry;
    return registry;
}

QList<std::shared_ptr<AbstractCamera>> CameraRegistry::getAvailableCameras() {
    return availableCameras;
}
