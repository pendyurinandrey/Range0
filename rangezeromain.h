#ifndef RANGEZEROMAIN_H
#define RANGEZEROMAIN_H

#include <QMainWindow>
#include <dialogs/newtrainingdialog.h>

QT_BEGIN_NAMESPACE
namespace Ui { class RangeZeroMain; }
QT_END_NAMESPACE

class RangeZeroMain : public QMainWindow
{
    Q_OBJECT

public:
    RangeZeroMain(QWidget *parent = nullptr);
    ~RangeZeroMain();

private slots:
    void on_actionTrainingWizard_triggered();

private:
    Ui::RangeZeroMain *ui;
    NewTrainingDialog* newTrainingDialog;
};
#endif // RANGEZEROMAIN_H
