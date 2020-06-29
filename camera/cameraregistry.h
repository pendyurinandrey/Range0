#ifndef CAMERAREGISTRY_H
#define CAMERAREGISTRY_H

#include <QObject>
#include <QCameraInfo>
#include "abstractcamera.h"

class CameraRegistry : public QObject
{
    Q_OBJECT
public:
    QList<std::shared_ptr<AbstractCamera>> getAvailableCameras();
    static CameraRegistry& getInstance();
    CameraRegistry(CameraRegistry const&) = delete;
    void operator=(CameraRegistry const&) = delete;
private:
    explicit CameraRegistry();
    QList<std::shared_ptr<AbstractCamera>> availableCameras;

signals:

};

#endif // CAMERAREGISTRY_H
