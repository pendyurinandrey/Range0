#include "qlabelrenderer.h"
#include <QPixmap>
#include <QtDebug>

QLabelRenderer::QLabelRenderer(QLabel *label, int preferredWidth, int preferredHeight, QObject *parent) : AbstractRenderer(parent)
{
    qInfo() << "Init";
    this->label = label;
    this->preferredWidth = preferredWidth;
    this->preferredHeight = preferredHeight;
}

QLabelRenderer::~QLabelRenderer() {
    qInfo() << "Destroy";
}

void QLabelRenderer::startRendering() {

}

void QLabelRenderer::stopRendering() {

}

void QLabelRenderer::render(int cameraId, QSharedPointer<cv::Mat> frame) {
    QPixmap r = QPixmap::fromImage(QImage((unsigned char*) frame->data, frame->cols, frame->rows, QImage::Format_RGB888));
    label->setPixmap(r.scaled(preferredWidth, preferredHeight, Qt::KeepAspectRatio));
    //label->resize(r.size());
}
