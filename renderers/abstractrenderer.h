#ifndef ABSTRACTRENDERER_H
#define ABSTRACTRENDERER_H

#include <QObject>
#include <opencv2/core/mat.hpp>
#include <QSharedPointer>

class AbstractRenderer : public QObject
{
    Q_OBJECT
public:
    explicit AbstractRenderer(QObject *parent = nullptr);
    virtual void startRendering() = 0;
    virtual void stopRendering() = 0;

public slots:
    virtual void render(int cameraId, QSharedPointer<cv::Mat> frame) = 0;

};

#endif // ABSTRACTRENDERER_H
