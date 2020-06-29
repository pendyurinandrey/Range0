#include "rangezeromain.h"
#include "ui_rangezeromain.h"

RangeZeroMain::RangeZeroMain(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::RangeZeroMain)
{
    ui->setupUi(this);
    newTrainingDialog = new NewTrainingDialog(this);
}

RangeZeroMain::~RangeZeroMain()
{
    delete ui;
}


void RangeZeroMain::on_actionTrainingWizard_triggered()
{
    newTrainingDialog->setModal(true);
    newTrainingDialog->show();
}
