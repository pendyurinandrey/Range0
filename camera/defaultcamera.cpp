#include "defaultcamera.h"
#include <opencv2/videoio.hpp>
#include <QDebug>
#include <QTimer>

DefaultCamera::DefaultCamera(int cameraIndex, QString description, QObject *parent): AbstractCamera(cameraIndex, description, parent)
{
    workerThread = nullptr;
    cameraWorker = nullptr;

}

DefaultCamera::~DefaultCamera() {
    if(workerThread) {
        connect(cameraWorker, &QObject::destroyed, workerThread, &QThread::quit);
        connect(workerThread, &QThread::finished, workerThread, &QThread::deleteLater);
        QMetaObject::invokeMethod(cameraWorker, "stopCapturing");
        cameraWorker->deleteLater();
    }
}

void DefaultCamera::start() {
    //Lazy init
    if(!workerThread) {
        qInfo() << "Start requested";
        std::unique_ptr<cv::VideoCapture> capture = std::make_unique<cv::VideoCapture>(id);
        workerThread = new QThread();
        workerThread->start();
        cameraWorker = new DefaultCameraWorker(std::move(capture));
        cameraWorker->moveToThread(workerThread);
        connect(cameraWorker, &DefaultCameraWorker::frameIsReady, this, &DefaultCamera::frameIsReady);
        connect(cameraWorker, &DefaultCameraWorker::fpsIsReady, this, &DefaultCamera::fpsIsReady);
        QTimer::singleShot(0, cameraWorker, &DefaultCameraWorker::startCapturing);
    }
    startRequestedCount++;
}

void DefaultCamera::stop() {
    if(startRequestedCount.load() == 0) {
        return;
    }

    startRequestedCount--;

    if(startRequestedCount.load() == 0) {
        QTimer::singleShot(0, cameraWorker, &DefaultCameraWorker::stopCapturing);
    }
}

void DefaultCamera::frameIsReady(QSharedPointer<cv::Mat> newFrame) {
    emit nextFrame(id, newFrame);
}
void DefaultCamera::fpsIsReady(double fps) {
    emit currentFps(id, fps);
}

