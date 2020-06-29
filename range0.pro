QT       += core gui multimedia widgets

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++14

# The following define makes your compiler emit warnings if you use
# any Qt feature that has been marked deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
    camera/abstractcamera.cpp \
    camera/cameraregistry.cpp \
    camera/defaultcamera.cpp \
    camera/defaultcameraworker.cpp \
    dialogs/newtrainingdialog.cpp \
    main.cpp \
    rangezeromain.cpp \
    renderers/abstractrenderer.cpp \
    renderers/qlabelrenderer.cpp \
    renderers/qlabelrendererworker.cpp \
    renderers/rendererbuilder.cpp

HEADERS += \
    camera/abstractcamera.h \
    camera/cameraregistry.h \
    camera/defaultcamera.h \
    camera/defaultcameraworker.h \
    common/common.h \
    dialogs/newtrainingdialog.h \
    rangezeromain.h \
    renderers/abstractrenderer.h \
    renderers/qlabelrenderer.h \
    renderers/qlabelrendererworker.h \
    renderers/rendererbuilder.h

FORMS += \
    dialogs/newtrainingdialog.ui \
    rangezeromain.ui

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

macx: OPENCV_BASE_PATH = /usr/local
macx: OPENCV_BASE_LIB_PATH = $${OPENCV_BASE_PATH}/lib

INCLUDEPATH += $${OPENCV_BASE_PATH}/include/opencv4
DEPENDPATH += $${OPENCV_BASE_LIB_PATH}

macx: LIBS += -L$${OPENCV_BASE_LIB_PATH} -lopencv_videoio -lopencv_core -lopencv_imgcodecs -lopencv_imgproc
macx: PRE_TARGETDEPS += $${OPENCV_BASE_LIB_PATH}/libopencv_videoio.a $${OPENCV_BASE_LIB_PATH}/libopencv_core.a $${OPENCV_BASE_LIB_PATH}/libopencv_imgcodecs.a
macx: PRE_TARGETDEPS += $${OPENCV_BASE_LIB_PATH}/libopencv_imgproc.a

macx {
    OPENCV_3RD_PARTY = $$files($${OPENCV_BASE_LIB_PATH}/opencv4/3rdparty/*.a)
    for(FILE, OPENCV_3RD_PARTY) {
        BASENAME = $$basename(FILE)
        EXT_REMOVED = $$replace(BASENAME,\.a,)
        LIBS += -L$${OPENCV_BASE_LIB_PATH}/opencv4/3rdparty/ -l$$replace(EXT_REMOVED, ^lib,)
    }
}

mac: LIBS += -framework Foundation
mac: LIBS += -framework CoreFoundation
mac: LIBS += -framework AVFoundation
mac: LIBS += -framework CoreGraphics
mac: LIBS += -framework CoreMedia
mac: LIBS += -framework CoreVideo
mac: LIBS += -framework Accelerate
mac: LIBS += -framework OpenCL

DISTFILES += \
    .gitignore
