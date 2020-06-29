#include "abstractcamera.h"

AbstractCamera::AbstractCamera(int id, QString description, QObject *parent) : QObject(parent)
{
    this->id = id;
    this->description = description;
}

int AbstractCamera::getId() {
    return id;
}

QString AbstractCamera::getDescription()  {
    return description;
}
