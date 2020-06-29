#include "rangezeromain.h"

#include <QApplication>

Q_DECLARE_METATYPE(QSharedPointer<cv::Mat>)
int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    qRegisterMetaType<QSharedPointer<cv::Mat>>();

    RangeZeroMain w;
    w.show();
    return a.exec();
}
