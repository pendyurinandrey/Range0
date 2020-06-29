#include "newtrainingdialog.h"
#include "ui_newtrainingdialog.h"
#include <camera/cameraregistry.h>
#include <QFormLayout>
#include <QLabel>
#include <QRadioButton>
#include <QHBoxLayout>
#include <QButtonGroup>
#include "renderers/rendererbuilder.h"

NewTrainingDialog::NewTrainingDialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::NewTrainingDialog)
{
    ui->setupUi(this);

    ui->camerasTW->setHorizontalHeaderItem(0, new QTableWidgetItem("Choose"));
    ui->camerasTW->setHorizontalHeaderItem(1, new QTableWidgetItem("Camera Info"));
    ui->camerasTW->setHorizontalHeaderItem(2, new QTableWidgetItem("Preview"));

    chosenCamera = nullptr;
}

NewTrainingDialog::~NewTrainingDialog()
{
    for(int i=0; i<ui->camerasTW->columnCount(); i++) {
        delete ui->camerasTW->takeHorizontalHeaderItem(i);
    }

    cleanCameraInfoTable();

    delete ui;
}

void NewTrainingDialog::show() {
    initCamerasList();
    QWidget::show();
}

void NewTrainingDialog::initCamerasList() {
    cleanCameraInfoTable();
    chosenCamera = new QButtonGroup();

    auto cameras = CameraRegistry::getInstance().getAvailableCameras();

    ui->camerasTW->setRowCount(cameras.size());
    ui->camerasTW->setColumnCount(3);

    //QFormLayout layout(this);
    int i = 0;
    for(auto &iter: cameras) {
        displayCameraInfo(ui->camerasTW, iter, i);
        i++;
    }
}

void NewTrainingDialog::displayCameraInfo(QTableWidget *table, std::shared_ptr<AbstractCamera> &camera, int rowNumber) {
    QWidget* radioButtonCell = new QWidget(table);
    QRadioButton *radioButton = new QRadioButton(radioButtonCell);
    QHBoxLayout *radioButtonCellLayout = new QHBoxLayout(radioButtonCell);
    radioButtonCellLayout->addWidget(radioButton);
    radioButtonCellLayout->setAlignment(Qt::AlignCenter);
    radioButtonCell->setLayout(radioButtonCellLayout);
    table->setCellWidget(rowNumber, 0, radioButtonCell);

    QTableWidgetItem* cameraNameCell = new QTableWidgetItem(camera->getDescription());
    cameraNameCell->setTextAlignment(Qt::AlignCenter);
    cameraNameCell->setFlags(cameraNameCell->flags() ^ Qt::ItemIsEditable);
    table->setItem(rowNumber, 1, cameraNameCell);

    QLabel* cameraView = new QLabel(table);
    table->setCellWidget(rowNumber, 2, cameraView);
    cameraView->setScaledContents(true);
    cameraView->setText("Loading...");
    cameraIdToLabel.insert(camera->getId(), cameraView);

    RendererBuilder rendererBuilder;
    auto renderer = rendererBuilder.fromCamera(camera)->toQLable(cameraView, 100, 100)->build();

    currentRenderers.push_back(std::move(renderer));

    chosenCamera->addButton(radioButton, rowNumber);
    chosenCamera->setExclusive(true);

    table->resizeRowToContents(rowNumber);
}

// onClose
void NewTrainingDialog::reject() {

    QDialog::reject();
}

void NewTrainingDialog::cleanCameraInfoTable() {
    ui->camerasTW->clear();
    if(chosenCamera != NULL) {
        delete chosenCamera;
        chosenCamera = NULL;
    }
}
