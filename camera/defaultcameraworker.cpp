#include "defaultcameraworker.h"
#include <QDateTime>
#include <QtDebug>
#include <QCoreApplication>
#include <opencv2/imgproc/imgproc.hpp>

DefaultCameraWorker::DefaultCameraWorker(std::unique_ptr<cv::VideoCapture> capture, QObject *parent) : QObject(parent)
{
    this->capture = std::move(capture);
}

void DefaultCameraWorker::startCapturing() {
    qInfo() << "Capturing was started";
    qint64 startTime = QDateTime::currentMSecsSinceEpoch();
    qint64 lastFpsEmitTime = startTime;
    qint64 frameCount = 0;

    while(!isStopRequested) {
        cv::Mat nextFrame;
        *capture >> nextFrame;

        if(nextFrame.empty()) {
            qWarning() << "Empty frame was received from camera.";
            break;
        }

        cv::cvtColor(nextFrame, nextFrame, cv::COLOR_BGR2RGB);

        frameCount++;

        // Force processing QT events (because Event Loop is blocked)
        if(frameCount % 10 == 0) {
            QCoreApplication::processEvents();
        }

        // TODO: Fix memory alloction
        emit frameIsReady(QSharedPointer<cv::Mat>(new cv::Mat(nextFrame)));
        if(QDateTime::currentMSecsSinceEpoch() - lastFpsEmitTime > 30000) {
            double currentFps = (double) frameCount / ((QDateTime::currentMSecsSinceEpoch() - startTime) / 1000.0);
            emit fpsIsReady(currentFps);
            lastFpsEmitTime = QDateTime::currentMSecsSinceEpoch();
        }
    }

    isStopRequested = false;
}

void DefaultCameraWorker::stopCapturing() {
    isStopRequested = true;
}
