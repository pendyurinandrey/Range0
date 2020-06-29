#ifndef COMMON_H
#define COMMON_H

#include <QObject>

namespace r0 {
    struct QObjectDeleteLater {
        void operator()(QObject *o) {
            o->deleteLater();
        }
    };

    template<typename T, typename = std::enable_if<std::is_base_of<QObject, T>::value>>
    using qobj_unique_ptr = std::unique_ptr<T, QObjectDeleteLater>;

    template<typename T, typename = std::enable_if<std::is_base_of<QObject, T>::value>>
    std::shared_ptr<T> makeQObjectShared(T *obj) {
        return std::shared_ptr<T>(obj, QObjectDeleteLater());
    }
};

#endif // COMMON_H
