#ifndef TRAININGWIZARD_H
#define TRAININGWIZARD_H

#include <QDialog>
#include <QCameraInfo>
#include <QTableWidget>
#include <QButtonGroup>
#include "camera/abstractcamera.h"
#include <QMap>
#include <QLabel>
#include "common/common.h"
#include "renderers/abstractrenderer.h"

namespace Ui {
class NewTrainingDialog;
}

class NewTrainingDialog : public QDialog
{
    Q_OBJECT

public:
    explicit NewTrainingDialog(QWidget *parent = nullptr);
    ~NewTrainingDialog();
    void show();
    void reject();

private:
    Ui::NewTrainingDialog *ui;
    QButtonGroup *chosenCamera;
    void initCamerasList();
    void displayCameraInfo(QTableWidget *table, std::shared_ptr<AbstractCamera> &camera, int rowNumber);
    void cleanCameraInfoTable();
    QMap<int, QLabel*> cameraIdToLabel;
    std::list<r0::qobj_unique_ptr<AbstractRenderer>> currentRenderers;


};

#endif // TRAININGWIZARD_H
