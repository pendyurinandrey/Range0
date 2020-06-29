#ifndef ABSTRACTCAMERA_H
#define ABSTRACTCAMERA_H

#include <QObject>
#include <opencv2/core/mat.hpp>
#include <QSharedPointer>

class AbstractCamera : public QObject
{
    Q_OBJECT
public:
    explicit AbstractCamera(int id, QString description, QObject *parent = nullptr);
    virtual void start() = 0;
    virtual void stop() = 0;

    int getId();
    QString getDescription();

protected:
    int id;
    QString description;


signals:
    void nextFrame(int cameraId, QSharedPointer<cv::Mat> newFrame);
    void currentFps(int cameraId, double fps);


};

#endif // ABSTRACTCAMERA_H
