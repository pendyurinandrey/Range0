#include "rendererbuilder.h"

RendererBuilder::RendererBuilder(QObject *parent) : QObject(parent)
{

}

RendererBuilder* RendererBuilder::fromCamera(std::shared_ptr<AbstractCamera> camera) {
    this->camera = camera;
    return this;
}

RendererBuilder* RendererBuilder::toQLable(QLabel* label, int preferredWidth, int preferredHeight) {
    renderer.reset(new QLabelRenderer(label, preferredWidth, preferredHeight));
    return this;
}

r0::qobj_unique_ptr<AbstractRenderer> RendererBuilder::build() {
    connect(camera.get(), &AbstractCamera::nextFrame,
                renderer.get(), &AbstractRenderer::render);
    camera->start();

    return std::move(renderer);
}
