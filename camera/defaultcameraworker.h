#ifndef DEFAULTCAMERAWORKER_H
#define DEFAULTCAMERAWORKER_H

#include <QObject>
#include "opencv2/videoio/videoio.hpp"
#include <QSharedPointer>

class DefaultCameraWorker : public QObject
{
    Q_OBJECT
public:
    explicit DefaultCameraWorker(std::unique_ptr<cv::VideoCapture> capture, QObject *parent = nullptr);

signals:
    void frameIsReady(QSharedPointer<cv::Mat> newFrame);
    void fpsIsReady(double fps);
public slots:
    void startCapturing();
    void stopCapturing();
private:
    std::unique_ptr<cv::VideoCapture> capture;
    bool isStopRequested = false;

};

#endif // DEFAULTCAMERAWORKER_H
