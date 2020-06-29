#ifndef QLABELRENDERER_H
#define QLABELRENDERER_H

#include <QObject>
#include "abstractrenderer.h"
#include <QLabel>
#include <QThread>

class QLabelRenderer : public AbstractRenderer
{
    Q_OBJECT
public:
    explicit QLabelRenderer(QLabel *label, int preferredWidth, int preferredHeight, QObject *parent = nullptr);
    virtual ~QLabelRenderer();
    void startRendering() override;
    void stopRendering() override;

private:
    QLabel *label = nullptr;
    QThread* workerThread = nullptr;
    int preferredWidth;
    int preferredHeight;

public slots:
    void render(int cameraId, QSharedPointer<cv::Mat> frame) override;

};

#endif // QLABELRENDERER_H
