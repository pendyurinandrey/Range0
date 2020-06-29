#ifndef RENDERERBUILDER_H
#define RENDERERBUILDER_H

#include <QObject>
#include <QLabel>
#include "camera/abstractcamera.h"
#include "abstractrenderer.h"
#include "qlabelrenderer.h"
#include "common/common.h"

class RendererBuilder : public QObject
{
    Q_OBJECT
public:
    explicit RendererBuilder(QObject *parent = nullptr);
    RendererBuilder* fromCamera(std::shared_ptr<AbstractCamera> camera);
    RendererBuilder* toQLable(QLabel* label, int preferredWidth, int preferredHeight);
    r0::qobj_unique_ptr<AbstractRenderer> build();

private:
    r0::qobj_unique_ptr<AbstractRenderer> renderer{};
    std::shared_ptr<AbstractCamera> camera{};


signals:

};

#endif // RENDERERBUILDER_H
