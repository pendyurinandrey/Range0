#ifndef DEFAULTCAMERA_H
#define DEFAULTCAMERA_H

#include <QObject>
#include <QThread>
#include "abstractcamera.h"
#include "opencv2/videoio/videoio.hpp"
#include "defaultcameraworker.h"

class DefaultCamera : public AbstractCamera
{
    Q_OBJECT
public:
    DefaultCamera(int cameraIndex, QString description, QObject *parent = nullptr);
    virtual ~DefaultCamera();
    void start() override;
    void stop() override;

private:
    QThread* workerThread;
    DefaultCameraWorker* cameraWorker;
    std::atomic<int> startRequestedCount{0};

private slots:
    void frameIsReady(QSharedPointer<cv::Mat> newFrame);
    void fpsIsReady(double fps);

};

#endif // DEFAULTCAMERA_H
